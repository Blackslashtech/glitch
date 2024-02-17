package service

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func (cc *ConnectionContext) ProcessCommand(cmd string) {
	defer func() {
		if err := recover(); err != nil {
			cc.internalErr("panic: %v", err)
		}
	}()

	parts := strings.Split(cmd, " ")
	switch parts[0] {
	case "captcha":
		if err := cc.handleCaptcha(); err != nil {
			cc.externalErr("captcha failed: %v", err)
			return
		}
		cc.captchaSolved = true

	case "upload":
		if len(parts) != 3 {
			cc.externalErr("upload command requires exactly 2 arguments")
			return
		}

		if cc.projectDir == "" {
			cc.externalErr("project not set")
			return
		}

		if !cc.captchaSolved {
			cc.externalErr("captcha not solved")
			return
		}
		cc.captchaSolved = false

		cc.upload(parts[1], parts[2])

	case "download":
		if len(parts) != 2 {
			cc.externalErr("download command requires exactly 1 argument")
			return
		}

		if cc.projectDir == "" {
			cc.externalErr("project not set")
			return
		}

		cc.getFile(parts[1])

	case "list":
		if len(parts) != 2 {
			cc.externalErr("list command requires exactly 1 argument")
			return
		}

		if cc.projectDir == "" {
			cc.externalErr("project not set")
			return
		}

		cc.listFiles(parts[1])

	case "delete":
		if len(parts) != 2 {
			cc.externalErr("delete command requires exactly 1 argument")
			return
		}

		if cc.projectDir == "" {
			cc.externalErr("project not set")
			return
		}

		cc.deleteFile(parts[1])

	case "job":
		if len(parts) != 2 {
			cc.externalErr("job command requires exactly 1 argument")
			return
		}

		if cc.projectDir == "" {
			cc.externalErr("project not set")
			return
		}

		if !cc.captchaSolved {
			cc.externalErr("captcha not solved")
			return
		}
		cc.captchaSolved = false

		cc.runJob(parts[1])

	case "project":
		if len(parts) != 3 {
			cc.externalErr("project command requires exactly 2 arguments")
			return
		}

		projectID := parts[1]
		projectPassword := parts[2]
		projectDir, err := cc.sanitizePath(filepath.Join(cc.baseDir, projectID))
		if err != nil {
			cc.externalErr("invalid project ID `%s`: %v", projectID, err)
			return
		}
		info, err := os.Stat(projectDir)
		if errors.Is(err, os.ErrNotExist) {
			if err := os.Mkdir(projectDir, 0755); err != nil {
				cc.externalErr("creating project directory `%s`: %v", projectDir, err)
				return
			}

			cc.projectDir = projectDir
			cc.projectID = projectID
			cc.logger = cc.logger.WithField("project", projectID)

			cc.send("project created")
			cc.send("project-password %x", cc.keyFromProjectID(projectID))
			return
		}

		if !info.IsDir() {
			cc.externalErr("project `%s` is not a directory", projectDir)
			return
		}

		if projectPassword != fmt.Sprintf("%x", cc.keyFromProjectID(projectID)) {
			cc.externalErr("invalid project password")
			return
		}

		cc.projectDir = projectDir
		cc.projectID = projectID
		cc.logger = cc.logger.WithField("project", projectID)

		cc.send("project set")

	default:
		cc.externalErr("unknown command `%s`", parts[0])
		return
	}
}
