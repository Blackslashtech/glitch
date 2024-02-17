package service

import (
	"fmt"

	"golang.org/x/net/websocket"
)

func (cc *ConnectionContext) send(format string, v ...any) {
	msg := fmt.Sprintf(format, v...)
	cc.logger.Debugf("sending message: %s", msg)
	if err := websocket.Message.Send(cc.conn, msg); err != nil {
		cc.logger.Debugf("Failed to send message: %s", err)
	}
}

func (cc *ConnectionContext) internalErr(format string, v ...any) {
	msg := fmt.Sprintf(format, v...)
	cc.logger.Errorf("internal error: %s", msg)
	cc.send("internal error")
}

func (cc *ConnectionContext) externalErr(format string, v ...any) {
	msg := fmt.Sprintf(format, v...)
	cc.logger.Warnf("external error: %s", msg)
	cc.send("error %s", msg)
}
