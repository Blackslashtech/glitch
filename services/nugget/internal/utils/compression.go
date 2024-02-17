package utils

import (
	"compress/gzip"
	"encoding/base64"
	"fmt"
	"io"
	"strings"
)

func Compress(data []byte) (string, error) {
	b := strings.Builder{}
	b64Enc := base64.NewEncoder(base64.URLEncoding, &b)
	gw := gzip.NewWriter(b64Enc)
	if _, err := gw.Write(data); err != nil {
		return "", fmt.Errorf("compressing: %w", err)
	}
	if err := gw.Close(); err != nil {
		return "", fmt.Errorf("closing gzip writer: %w", err)
	}
	if err := b64Enc.Close(); err != nil {
		return "", fmt.Errorf("closing base64 encoder: %w", err)
	}
	return b.String(), nil
}

func Decompress(data string) ([]byte, error) {
	base64Dec := base64.NewDecoder(base64.URLEncoding, strings.NewReader(data))

	gr, err := gzip.NewReader(base64Dec)
	if err != nil {
		return nil, fmt.Errorf("creating gzip reader: %w", err)
	}
	defer gr.Close()

	res, err := io.ReadAll(gr)
	if err != nil {
		return nil, fmt.Errorf("decoding: %w", err)
	}

	return res, nil
}
