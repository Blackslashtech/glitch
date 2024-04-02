package main

import (
	"context"
	"errors"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"bluwal/internal/controller"
	"bluwal/internal/logging"
	"bluwal/internal/service"
	bwpb "bluwal/pkg/proto/bluwal"

	"github.com/c4t-but-s4d/neo/v2/pkg/mu"
	"github.com/c4t-but-s4d/neo/v2/pkg/neohttp"
	"github.com/genjidb/genji"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	logging.Init()

	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "bluwal.db"
	}
	db, err := genji.Open(dbPath)
	if err != nil {
		logrus.Fatalf("opening db: %v", err)
	}

	bc, err := controller.NewController(db)
	if err != nil {
		logrus.Fatalf("creating controller: %v", err)
	}

	bs := service.NewService(bc)

	server := grpc.NewServer()
	reflection.Register(server)

	bwpb.RegisterBluwalServiceServer(server, bs)

	httpHandler := http.NewServeMux()
	httpHandler.Handle("/", neohttp.StaticHandler("front/dist"))

	handler := mu.NewHandler(server, mu.WithHTTPHandler(httpHandler))
	httpServer := &http.Server{
		Handler: handler,
		Addr:    ":9090",
	}

	runCtx, runCancel := signal.NotifyContext(context.Background(), syscall.SIGTERM, syscall.SIGINT)
	defer runCancel()

	go func() {
		logrus.Infof("starting server on %s", httpServer.Addr)
		if err := httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logrus.Fatalf("error running http server: %v", err)
		}
	}()

	<-runCtx.Done()
	logrus.Info("shutting down")

	shutdownCtx, shutdownCancel := signal.NotifyContext(context.Background(), syscall.SIGTERM, syscall.SIGINT)
	defer shutdownCancel()
	if err := httpServer.Shutdown(shutdownCtx); err != nil {
		logrus.Fatalf("error stopping http server: %v", err)
	}

	logrus.Info("finished")
}
