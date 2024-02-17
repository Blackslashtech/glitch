package service

import (
	"errors"
	"fmt"

	"nugget/internal/captcha"

	"golang.org/x/net/websocket"
)

const (
	captchaDifficulty = 6
)

func (cc *ConnectionContext) handleCaptcha() error {
	challenge, err := captcha.GenerateChallenge(captchaDifficulty)
	if err != nil {
		return fmt.Errorf("generating captcha challenge: %w", err)
	}
	cc.send("captcha %s", challenge)

	var resp string
	if err := websocket.Message.Receive(cc.conn, &resp); err != nil {
		return fmt.Errorf("receiving captcha response: %w", err)
	}

	ok, err := challenge.VerifyResponse(resp)
	if err != nil {
		return fmt.Errorf("verifying captcha response: %w", err)
	}
	if !ok {
		return errors.New("invalid captcha response")
	}
	cc.send("captcha ok")
	return nil
}
