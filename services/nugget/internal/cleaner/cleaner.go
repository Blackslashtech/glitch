package cleaner

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/sirupsen/logrus"
)

type Cleaner struct {
	interval  time.Duration
	threshold time.Duration
	dataDir   string

	logger *logrus.Entry
}

func NewCleaner(interval, threshold time.Duration, dataDir string) *Cleaner {
	return &Cleaner{
		interval:  interval,
		threshold: threshold,
		dataDir:   dataDir,

		logger: logrus.WithFields(logrus.Fields{
			"component": "cleaner",
			"interval":  interval,
			"threshold": threshold,
			"data_dir":  dataDir,
		}),
	}
}

func (c *Cleaner) Run(ctx context.Context) {
	t := time.NewTicker(c.interval)
	defer t.Stop()

	if err := c.clean(); err != nil {
		c.logger.Errorf("running initial clean: %v", err)
	}

	for {
		select {
		case <-ctx.Done():
			return
		case <-t.C:
			if err := c.clean(); err != nil {
				c.logger.Errorf("cleaning: %v", err)
			}
		}
	}
}

func (c *Cleaner) clean() error {
	dirs, err := os.ReadDir(c.dataDir)
	if err != nil {
		return fmt.Errorf("reading data dir: %w", err)
	}

	cntRemoved := 0
	for _, dir := range dirs {
		if !dir.IsDir() {
			continue
		}
		info, err := dir.Info()
		if err != nil {
			c.logger.Warnf("getting info for %s: %v", dir.Name(), err)
		}
		if time.Since(info.ModTime()) > c.threshold {
			c.logger.Debugf("removing %s", dir.Name())
			if err := os.RemoveAll(filepath.Join(c.dataDir, dir.Name())); err != nil {
				c.logger.Warnf("removing %s: %v", dir.Name(), err)
			} else {
				cntRemoved++
			}
		}
	}

	c.logger.Infof("removed %d directories", cntRemoved)

	return nil
}
