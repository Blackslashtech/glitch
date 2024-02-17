package service

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/sha256"
	"fmt"
)

func (cc *ConnectionContext) keyFromProjectID(projectID string) []byte {
	h := hmac.New(sha256.New, cc.secret)
	h.Write([]byte(projectID))
	return h.Sum(nil)[:aes.BlockSize]
}

// Encryption logic is checked by the checker, don't change it.
func (cc *ConnectionContext) encrypt(projectID string, data []byte) ([]byte, error) {
	data = pad(data)

	buf := make([]byte, len(data)+aes.BlockSize)
	iv := buf[:aes.BlockSize]
	dst := buf[aes.BlockSize:]

	block, err := aes.NewCipher(cc.keyFromProjectID(projectID))
	if err != nil {
		return nil, fmt.Errorf("creating cipher: %w", err)
	}

	cipher.NewCBCEncrypter(block, iv).CryptBlocks(dst, data)

	return buf, nil
}

func pad(data []byte) []byte {
	padLen := aes.BlockSize - len(data)%aes.BlockSize
	pad := make([]byte, padLen)
	for i := range pad {
		pad[i] = byte(padLen)
	}
	return append(data, pad...)
}
