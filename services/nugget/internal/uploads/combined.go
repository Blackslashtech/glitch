package uploads

import (
	"errors"
	"fmt"
	"io"
)

func CombinedCloser(closers ...io.Closer) io.Closer {
	return combinedCloser{closers}
}

type combinedCloser struct {
	closers []io.Closer
}

func (c combinedCloser) Close() error {
	var finalErr error
	for _, closer := range c.closers {
		if err := closer.Close(); err != nil {
			finalErr = errors.Join(finalErr, fmt.Errorf("closing %v: %w", closer, err))
		}
	}
	return finalErr
}
