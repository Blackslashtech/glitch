package service

import (
	"fmt"
	"path/filepath"
	"strings"
)

func (cc *ConnectionContext) sanitizePath(path string) (string, error) {
	path, err := filepath.Abs(path)
	if err != nil {
		return "", fmt.Errorf("cleaning path `%s`: %w", path, err)
	}

	if !strings.HasPrefix(path, cc.baseDir) {
		return "", fmt.Errorf("path `%s` is not in base root `%s`", path, cc.baseDir)
	}
	return path, nil
}

func (cc *ConnectionContext) sanitizeMyProjectPath(path string) (string, error) {
	preSanitized, err := cc.sanitizePath(path)
	if err != nil {
		return "", err
	}

	if !strings.HasPrefix(preSanitized, cc.projectDir) {
		return "", fmt.Errorf("path `%s` is not in project root `%s`", preSanitized, cc.projectDir)
	}

	return preSanitized, nil
}
