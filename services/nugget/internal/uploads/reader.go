package uploads

import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"nugget/internal/utils"
)

type Reader struct {
	zr    *zip.ReadCloser
	tr    *tar.Reader
	index int

	toClose io.Closer
}

func NewReader(path string) (*Reader, error) {
	if !utils.FileExists(path) {
		return nil, fmt.Errorf("file `%s` does not exist", path)
	}

	switch filepath.Ext(path) {
	case ".zip":
		zr, err := zip.OpenReader(path)
		if err != nil {
			return nil, fmt.Errorf("opening file %s in zip: %v", path, err)
		}

		return &Reader{
			zr:      zr,
			toClose: zr,
		}, nil

	case ".targz":
		f, err := os.Open(path)
		if err != nil {
			return nil, fmt.Errorf("opening file %s: %v", path, err)
		}

		gr, err := gzip.NewReader(f)
		if err != nil {
			return nil, fmt.Errorf("creating gzip reader: %v", err)
		}

		return &Reader{
			tr:      tar.NewReader(gr),
			toClose: CombinedCloser(gr, f),
		}, nil

	case ".tar":
		f, err := os.Open(path)
		if err != nil {
			return nil, fmt.Errorf("opening file %s: %v", path, err)
		}

		return &Reader{
			tr:      tar.NewReader(f),
			toClose: f,
		}, nil

	default:
		return nil, fmt.Errorf("file `%s` is not a valid archive", path)
	}
}

func (u *Reader) Next() (string, int64, io.Reader, error) {
	switch {
	case u.zr != nil:
		if u.index >= len(u.zr.File) {
			return "", 0, nil, io.EOF
		}

		f := u.zr.File[u.index]
		u.index++

		rc, err := f.Open()
		if err != nil {
			return "", 0, nil, fmt.Errorf("opening file %s in zip: %w", f.Name, err)
		}

		return f.Name, f.Modified.Unix(), rc, nil
	case u.tr != nil:
		f, err := u.tr.Next()
		if err != nil {
			return "", 0, nil, fmt.Errorf("opening file in tar: %w", err)
		}
		return f.Name, f.ModTime.Unix(), u.tr, nil
	}
	return "", 0, nil, errors.New("bad Reader")
}

func (u *Reader) Close() error {
	if err := u.toClose.Close(); err != nil {
		return fmt.Errorf("closing Reader: %v", err)
	}
	return nil
}
