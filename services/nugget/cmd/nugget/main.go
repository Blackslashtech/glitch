package main

import (
	"context"
	"crypto/rand"
	"errors"
	"io"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"sync"
	"syscall"
	"time"

	"nugget/internal/cleaner"
	"nugget/internal/logging"
	"nugget/internal/service"

	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
	"golang.org/x/net/websocket"
)

func connectionHandler(pwd string, secret []byte) func(conn *websocket.Conn) {
	dataDir := filepath.Join(pwd, "data")

	return func(ws *websocket.Conn) {
		connID := uuid.NewString()[:8]

		cc := service.NewConnectionContext(ws, dataDir, connID, secret)
		var msg string
		for {
			err := websocket.Message.Receive(ws, &msg)
			if errors.Is(err, io.EOF) {
				logrus.Debugf("client disconnected")
				break
			}
			if err != nil {
				logrus.Debugf("receiving message: %v", err)
				break
			}
			logrus.Debugf("received message: %s", msg)
			cc.ProcessCommand(msg)
		}
	}
}

func readSecret() []byte {
	secret, err := os.ReadFile("secrets/nugget")
	if err == nil {
		return secret
	}
	secret = make([]byte, 32)
	if _, err := io.ReadFull(rand.Reader, secret); err != nil {
		logrus.Fatalf("generating secret: %v", err)
	}
	if err := os.WriteFile("secrets/nugget", secret, 0600); err != nil {
		logrus.Fatalf("writing secret: %v", err)
	}
	return secret
}

func main() {
	logging.Init()

	// Safe non-concurrent init.
	readSecret()

	pwd, err := os.Getwd()
	if err != nil {
		logrus.Fatalf("getting working directory: %v", err)
	}

	http.Handle("/ws/", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		r.Header.Set("Origin", "http://"+r.Host)
		websocket.Handler(connectionHandler(pwd, readSecret())).ServeHTTP(w, r)
	}))

	wg := sync.WaitGroup{}
	wg.Add(1)
	go func() {
		defer wg.Done()
		logrus.Info("http server started on :5555")
		if err := http.ListenAndServe(":5555", nil); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logrus.Fatalf("running http server: %v", err)
		}
		logrus.Info("http server stopped")
	}()

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	c := cleaner.NewCleaner(
		5*time.Minute,
		20*time.Minute,
		filepath.Join(pwd, "data"),
	)
	wg.Add(1)
	go func() {
		defer wg.Done()
		logrus.Info("starting cleaner")
		c.Run(ctx)
		logrus.Info("cleaner stopped")
	}()

	<-ctx.Done()

	logrus.Info("shutting down")
	cancel()
	wg.Wait()
}
