package utils

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func FileExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.Mode().IsRegular()
}

func GetFilename(path string) string {
	return filepath.Base(filepath.Clean(path))
}

func GetHiddenFilename(path string) string {
	return fmt.Sprintf(".%s", GetFilename(path))
}

func IsHidden(path string) bool {
	return strings.HasPrefix(GetFilename(path), ".")
}

func StripExt(path string) string {
	return strings.TrimSuffix(path, filepath.Ext(path))
}
