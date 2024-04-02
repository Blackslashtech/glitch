package logging

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"github.com/sirupsen/logrus"
)

func Init() {
	logrus.SetFormatter(&logrus.TextFormatter{
		ForceColors:            true,
		FullTimestamp:          true,
		TimestampFormat:        "2006-01-02 15:04:05",
		DisableLevelTruncation: false,
		CallerPrettyfier: func(f *runtime.Frame) (string, string) {
			filename := filepath.Base(f.File)
			return "", fmt.Sprintf(" %s:%d", filename, f.Line)
		},
	})
	logrus.SetReportCaller(true)

	switch {
	case os.Getenv("BLUWAL_LOG_LEVEL") != "":
		level, err := logrus.ParseLevel(os.Getenv("BLUWAL_LOG_LEVEL"))
		if err != nil {
			logrus.Fatalf("parsing log level: %v", err)
		}
		logrus.SetLevel(level)
	default:
		logrus.SetLevel(logrus.InfoLevel)
	}
}
