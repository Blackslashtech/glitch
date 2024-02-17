package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"nugget/internal/captcha"
	"nugget/internal/logging"

	"github.com/sirupsen/logrus"
)

func main() {
	logging.Init()

	if len(os.Args) < 2 {
		logrus.Fatalf("usage: %s <nonce>:<hash>:<>", os.Args[0])
	}

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	start := time.Now()
	solution, err := captcha.Solve(ctx, os.Args[1])
	if err != nil {
		logrus.Fatalf("solving captcha: %v", err)
	}
	logrus.WithField("elapsed", time.Since(start)).Infof("found: %s", solution)
	fmt.Println(solution)
}
