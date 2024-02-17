package captcha

import (
	"crypto/md5"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	_ "embed"
	"encoding/hex"
	"encoding/pem"
	"fmt"
)

//go:embed checker-pub.pem
var publicKeyData []byte

var publicKey *rsa.PublicKey

func init() {
	block, _ := pem.Decode(publicKeyData)
	key, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		panic(err)
	}
	publicKey = key.(*rsa.PublicKey)
}

type Challenge struct {
	Nonce      []byte
	Hash       string
	Difficulty int
	Answer     []byte
}

func (c *Challenge) VerifyResponse(response string) (bool, error) {
	dec, err := hex.DecodeString(response)
	if err != nil {
		return false, fmt.Errorf("decoding response: %w", err)
	}
	gotHash := fmt.Sprintf("%x", calculateHash(append(c.Nonce, dec...)))
	if gotHash[:c.Difficulty] != c.Hash {
		return false, nil
	}
	return true, nil
}

func (c *Challenge) String() string {
	return fmt.Sprintf("%x:%s:%x", c.Nonce, c.Hash, c.Answer)
}

func GenerateChallenge(difficulty int) (*Challenge, error) {
	challenge := make([]byte, 16)
	_, err := rand.Read(challenge)
	if err != nil {
		return nil, fmt.Errorf("generating challenge: %w", err)
	}

	encryptedBytes, err := rsa.EncryptPKCS1v15(
		rand.Reader,
		publicKey,
		challenge[8:],
	)
	if err != nil {
		panic(err)
	}

	return &Challenge{
		Nonce:      challenge[:8],
		Hash:       fmt.Sprintf("%x", calculateHash(challenge))[:difficulty],
		Difficulty: difficulty,
		Answer:     encryptedBytes,
	}, nil
}

func calculateHash(data []byte) []byte {
	const iterations = 3

	for i := 0; i < iterations; i++ {
		h := md5.Sum(data)
		data = h[:]
	}
	return data
}
