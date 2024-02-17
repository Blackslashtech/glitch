package service

import (
	"archive/tar"
	"archive/zip"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	"nugget/internal/uploads"
	"nugget/internal/utils"

	"github.com/sirupsen/logrus"
	"golang.org/x/net/websocket"
)

const (
	externalFilePrefix = "external"
)

const (
	uploadSizeLimit       = 128 * 1024
	jobFileSizeLimit      = 2 * 1024 * 1024
	maxSingleDownloadSize = 128 * 1024
)

type ConnectionContext struct {
	conn *websocket.Conn

	projectID     string
	projectDir    string
	baseDir       string
	secret        []byte
	captchaSolved bool

	logger *logrus.Entry
}

func NewConnectionContext(
	conn *websocket.Conn,
	baseDir string,
	connID string,
	secret []byte,
) *ConnectionContext {
	return &ConnectionContext{
		conn:    conn,
		baseDir: baseDir,
		secret:  secret,

		logger: logrus.WithFields(logrus.Fields{
			"component": "connection",
			"id":        connID,
		}),
	}
}

func (cc *ConnectionContext) runJob(jobDesc string) {
	decodedData, err := utils.Decompress(jobDesc)
	if err != nil {
		cc.externalErr("decompressing: %v", err)
		return
	}

	if len(decodedData) > jobFileSizeLimit {
		cc.externalErr("job file is too large: %d > %d", len(decodedData), jobFileSizeLimit)
		return
	}

	var result JobTemplateDefinition
	if err := json.Unmarshal(decodedData, &result); err != nil {
		cc.externalErr("unmarshalling job: %v", err)
		return
	}

	var filesToArchive []ArchiveFile
	for _, step := range result.Job.Steps {
		for _, artifact := range step.Artifacts {
			externalProject := ""
			artifactSrc := ""
			if artifact.SourceProject == "" || artifact.SourceProject == cc.projectID {
				artifact.SourceProject = ""
				artifactSrc = filepath.Join(cc.projectDir, artifact.Source)
			} else {
				externalProject = artifact.SourceProject
				artifactSrc = filepath.Join(cc.baseDir, artifact.SourceProject, artifact.Source)
			}

			var err error
			if artifactSrc, err = cc.sanitizePath(artifactSrc); err != nil {
				cc.externalErr("invalid artifact source path `%s`: %v", artifactSrc, err)
				continue
			}
			if utils.IsHidden(artifactSrc) {
				cc.externalErr("artifact source `%s` is hidden", artifactSrc)
				continue
			}

			filesToArchive = append(filesToArchive, ArchiveFile{
				Source:          artifactSrc,
				Destination:     filepath.Clean(artifact.Destination),
				ExternalProject: externalProject,
			})
		}
		cc.archiveFiles(step.Name, filesToArchive)
	}

	cc.send("job ok")
}

func (cc *ConnectionContext) archiveFiles(name string, files []ArchiveFile) {
	tarPath, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, utils.GetHiddenFilename(name)+".tar"))
	if err != nil {
		cc.externalErr("invalid name `%s`: %v", name, err)
		return
	}

	zipPath, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, utils.GetFilename(name)))
	if err != nil {
		cc.externalErr("invalid name `%s`: %v", name, err)
		return
	}

	if utils.FileExists(tarPath) {
		if err := os.Remove(tarPath); err != nil {
			cc.externalErr("unable to delete old backup: %v", err)
			return
		}
	}

	toClose := make([]io.Closer, 0, 2)
	defer func() {
		for _, closer := range toClose {
			if err := closer.Close(); err != nil {
				cc.logger.Errorf("error closing %v: %v", closer, err)
			}
		}
	}()

	tFile, err := os.OpenFile(tarPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		cc.internalErr("opening backup file: %v", err)
		return
	}
	toClose = append(toClose, tFile)

	tw := tar.NewWriter(tFile)
	toClose = append(toClose, tw)

	cc.logger.Debugf("archiving %d files", len(files))
	for _, fn := range files {
		fp, err := cc.sanitizePath(fn.Source)
		if err != nil {
			cc.externalErr("invalid source path `%s`: %v", fn.Source, err)
			continue
		}

		info, err := os.Stat(fp)
		if errors.Is(err, os.ErrNotExist) {
			cc.externalErr("file `%s` not found", fp)
			continue
		}
		if err != nil {
			cc.externalErr("statting file `%s`: %v", fp, err)
			continue
		}
		if !info.Mode().IsRegular() {
			cc.externalErr("file `%s` is not a regular file", fp)
			continue
		}

		fh, _ := tar.FileInfoHeader(info, "")
		fh.Name = fn.Destination
		if fn.ExternalProject != "" {
			fh.Name = fmt.Sprintf("%s__%s__%s", externalFilePrefix, fn.ExternalProject, fn.Destination)
		}

		if err := tw.WriteHeader(fh); err != nil {
			cc.externalErr("writing header for file `%s`: %v", fp, err)
			break
		}

		fr, err := os.Open(fp)
		if err != nil {
			cc.externalErr("opening file `%s`: %v", fp, err)
			break
		}

		_, err = io.Copy(tw, fr)
		if closeErr := fr.Close(); closeErr != nil {
			cc.logger.Errorf("closing file `%s`: %v", fp, closeErr)
		}
		if err != nil {
			cc.externalErr("writing file `%s`: %v", fp, err)
			break
		}
	}

	if err := tw.Close(); err != nil {
		cc.externalErr("closing tar writer: %v", err)
		return
	}
	toClose = toClose[:len(toClose)-1]

	if err := tFile.Close(); err != nil {
		cc.internalErr("closing backup file: %v", err)
		return
	}
	toClose = toClose[:len(toClose)-1]

	cc.logger.Debugf("done archiving %d files, compressing", len(files))
	if err := cc.compressFiles(tarPath, zipPath); err != nil {
		cc.externalErr("compressing backup: %v", err)
		return
	}
}

func (cc *ConnectionContext) listFiles(path string) {
	_, children := cc.findArchiveFile(path)
	if len(children) > 0 {
		out := strings.Builder{}
		for _, c := range children {
			out.WriteString(c)
			out.WriteString(" ")
		}
		cc.send("files %s", out.String()[:out.Len()-1])
		return
	}

	cc.externalErr("no files found")
}

func (cc *ConnectionContext) compressFiles(inPath, outPath string) error {
	ur, err := uploads.NewReader(inPath)
	if err != nil {
		return fmt.Errorf("creating upload reader: %w", err)
	}
	defer func() {
		if err := ur.Close(); err != nil {
			cc.logger.Errorf("closing upload reader: %v", err)
		}
	}()

	outFile, err := os.OpenFile(outPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return fmt.Errorf("opening output file: %w", err)
	}
	defer func() {
		if err := outFile.Close(); err != nil {
			cc.logger.Errorf("closing output file: %v", err)
		}
	}()

	zw := zip.NewWriter(outFile)
	defer func() {
		if err := zw.Close(); err != nil {
			cc.logger.Errorf("closing zip writer: %v", err)
		}
	}()

	for {
		name, modTime, fr, err := ur.Next()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			cc.internalErr("reading next file: %v", err)
			break
		}

		name = strings.TrimLeft(name, "/")

		fileData, err := io.ReadAll(fr)
		if err != nil {
			cc.externalErr("reading file `%s`: %v", name, err)
			continue
		}

		if strings.HasPrefix(name, externalFilePrefix) {
			tokens := strings.SplitN(name, "__", 3)
			if len(tokens) < 3 {
				cc.externalErr("invalid external file `%s`", name)
				continue
			}

			externalProjectID := tokens[1]
			name = strings.TrimLeft(tokens[2], "/")

			if fileData, err = cc.encrypt(externalProjectID, fileData); err != nil {
				cc.externalErr("encrypting file `%s`: %v", name, err)
				continue
			}
		}

		header := &zip.FileHeader{
			Name:     name,
			Modified: time.Unix(modTime, 0),
			Method:   zip.Deflate,
		}
		fw, err := zw.CreateHeader(header)
		if err != nil {
			return fmt.Errorf("creating header for file `%s`: %w", name, err)
		}
		if _, err := fw.Write(fileData); err != nil {
			return fmt.Errorf("writing file `%s`: %w", name, err)
		}
	}

	return nil
}

func (cc *ConnectionContext) findArchiveFile(path string) (string, []string) {
	path = strings.Trim(path, "/")

	parts := strings.SplitN(path, "/", 2)
	if len(parts) < 1 {
		cc.externalErr("invalid path `%s`", path)
		return "", nil
	}
	if len(parts) < 2 {
		parts = append(parts, "")
	}

	archivePath, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, utils.GetFilename(parts[0])))
	if err != nil {
		cc.externalErr("invalid path `%s`: %v", path, err)
		return "", nil
	}
	archiveFilename := parts[1]

	if !utils.FileExists(archivePath) {
		cc.externalErr("archive `%s` not found", archivePath)
		return "", nil
	}

	zr, err := zip.OpenReader(archivePath)
	if err != nil {
		cc.externalErr("opening archive `%s`: %v", archivePath, err)
		return "", nil
	}
	defer func() {
		if err := zr.Close(); err != nil {
			cc.logger.Errorf("closing archive `%s`: %v", archivePath, err)
		}
	}()

	var children []string
	for _, f := range zr.File {
		if f.Name == archiveFilename {
			rc, err := f.Open()
			if err != nil {
				cc.externalErr("opening file `%s` in archive `%s`: %v", archiveFilename, archivePath, err)
				continue
			}

			data, err := io.ReadAll(io.LimitReader(rc, maxSingleDownloadSize))

			if closeErr := rc.Close(); closeErr != nil {
				cc.logger.Errorf("closing file `%s` in archive `%s`: %v", archiveFilename, archivePath, err)
			}

			if err != nil {
				cc.externalErr("reading file `%s` in archive `%s`: %v", archiveFilename, archivePath, err)
				continue
			}

			compressed, err := utils.Compress(data)
			if err != nil {
				cc.externalErr("compressing file `%s`: %v", f.Name, err)
				continue
			}

			return compressed, nil
		} else if strings.HasPrefix(f.Name, archiveFilename) {
			rest := strings.TrimPrefix(f.Name, archiveFilename)
			rest = strings.TrimPrefix(rest, "/")

			parts := strings.SplitN(rest, "/", 2)
			topDir := parts[0]
			if len(parts) > 1 {
				topDir += "/"
			}
			children = append(children, topDir)
		}
	}
	return "", children
}

func (cc *ConnectionContext) getFile(path string) {
	b64, _ := cc.findArchiveFile(path)
	if b64 == "" {
		cc.externalErr("file `%s` not found", path)
		return
	}

	cc.send("file %s %s", path, b64)
}

func (cc *ConnectionContext) upload(name string, b64data string) {
	name = utils.GetFilename(name)
	uploadPath, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, name))
	if err != nil {
		cc.externalErr("invalid path `%s`: %v", name, err)
		return
	}

	dstPath, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, utils.StripExt(name)))
	if err != nil {
		cc.externalErr("invalid path `%s`: %v", uploadPath, err)
		return
	}

	data, err := utils.Decompress(b64data)
	if err != nil {
		cc.externalErr("decompressing: %v", err)
		return
	}

	if len(data) > uploadSizeLimit {
		cc.externalErr("file is too large: %d > %d", len(data), uploadSizeLimit)
		return
	}

	if err := os.WriteFile(uploadPath, data, 0644); err != nil {
		cc.externalErr("writing file `%s`: %v", uploadPath, err)
		return
	}

	if err := cc.compressFiles(uploadPath, dstPath); err != nil {
		cc.externalErr("compressing file `%s`: %v", uploadPath, err)
		return
	}
	cc.send("upload ok: remote directory `%s` created", utils.GetFilename(dstPath))
}

func (cc *ConnectionContext) deleteFile(name string) {
	path, err := cc.sanitizeMyProjectPath(filepath.Join(cc.projectDir, name))
	if err != nil {
		cc.externalErr("invalid path `%s`: %v", name, err)
		return
	}
	if err := os.Remove(path); err != nil {
		cc.externalErr("deleting file `%s`: %v", path, err)
		return
	}
	cc.send("delete ok")
}
