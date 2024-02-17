package captcha

import (
	"context"
	"encoding/binary"
	"encoding/hex"
	"errors"
	"fmt"
	"runtime"
	"strings"

	"github.com/sirupsen/logrus"
	"golang.org/x/sync/errgroup"
)

const (
	checkCtxInterval = 100000
	debugInterval    = 1000000
)

func Solve(ctx context.Context, challenge string) (string, error) {
	tokens := strings.SplitN(challenge, ":", 3)
	if len(tokens) < 3 {
		return "", fmt.Errorf("invalid argument, not enough tokens: %d", len(tokens))
	}

	nonce, err := hex.DecodeString(tokens[0])
	if err != nil {
		return "", fmt.Errorf("decoding nonce: %w", err)
	}

	odd := false
	if len(tokens[1])%2 == 1 {
		odd = true
		tokens[1] = tokens[1] + "0"
	}
	hash, err := hex.DecodeString(tokens[1])
	if err != nil {
		return "", fmt.Errorf("decoding hash: %w", err)
	}

	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	results := make(chan string, 10)
	g, gctx := errgroup.WithContext(ctx)

	workers := runtime.GOMAXPROCS(0)
	for i := 0; i < workers; i++ {
		i := i
		g.Go(func() error {
			return run(gctx, i, workers, results, nonce, hash, odd)
		})
	}

	select {
	case <-ctx.Done():
		if err := g.Wait(); err != nil && !errors.Is(err, context.Canceled) && !errors.Is(err, context.DeadlineExceeded) {
			logrus.Errorf("waiting for workers: %v", err)
		}

		return "", ctx.Err()
	case res := <-results:
		cancel()

		if err := g.Wait(); err != nil && !errors.Is(err, context.Canceled) {
			logrus.Errorf("waiting for workers: %v", err)
		}

		return res, nil
	}
}

func run(
	ctx context.Context,
	worker, totalWorkers int,
	res chan<- string,
	nonce []byte,
	hash []byte,
	oddHash bool,
) error {
	n := len(nonce)
	buf := make([]byte, n+4)
	copy(buf, nonce)

	for iter := 0; ; iter++ {
		if iter%debugInterval == 0 && iter > 0 {
			logrus.Debugf("worker %d: %d iterations", worker, iter)
		}
		if iter%checkCtxInterval == 0 {
			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
			}
		}

		iterVal := worker + iter*totalWorkers
		binary.LittleEndian.PutUint32(buf[n:], uint32(iterVal))
		if equal(calculateHash(buf)[:len(hash)], hash, oddHash) {
			res <- fmt.Sprintf("%x", buf[n:])
			return nil
		}
	}
}

func equal(a, b []byte, odd bool) bool {
	if len(a) != len(b) {
		return false
	}
	for i, val := range a {
		if odd && i == len(a)-1 {
			return a[i]&0xf0 == b[i]&0xf0
		}
		if val != b[i] {
			return false
		}
	}
	return true
}
