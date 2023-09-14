package main

import (
	"crypto"
	"crypto/rsa"
	"crypto/sha512"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/patrickmn/go-cache"
)

type UserInfo struct {
	Id      string
	Capsule string
}

type Capsule struct {
	Pk string
}

type UserAuth struct {
	Token      string
	Expiration int
}

var API_SERVER_HOST string = os.Getenv("API_HOST")
var AUTH_API_SERVER_HOST string = os.Getenv("AUTH_HOST")
var apiServerURL *url.URL

var userCache *cache.Cache

func getSignatureHeaders(headers http.Header) (string, string, error) {
	signature := headers["X-Request-Signature"]
	if len(signature) != 1 {
		return "", "", errors.New("missing request signature")
	}

	user := headers["X-Request-User"]
	if len(user) != 1 {
		return signature[0], "", errors.New("missing request user")
	}

	headers.Del("X-Request-Signature")
	headers.Del("X-Request-User")

	return signature[0], user[0], nil
}

func getUserPublicKey(username string) (string, []byte, error) {
	pubKey, found := userCache.Get("key_" + username)
	userId, found2 := userCache.Get("id_" + username)
	if found && found2 {
		return userId.(string), pubKey.([]byte), nil
	}

	fmt.Printf("[.] requesting %s\n", AUTH_API_SERVER_HOST+"/user/"+username)
	userInfo, err := http.Get(AUTH_API_SERVER_HOST + "/user/" + username)
	if err != nil {
		return "", []byte(""), err
	}

	fmt.Printf("[.] parsing data\n")
	var userInfoJSON UserInfo
	err = json.NewDecoder(userInfo.Body).Decode(&userInfoJSON)
	if err != nil {
		return "", []byte(""), err
	}

	capsuleRaw, err := base64.StdEncoding.DecodeString(userInfoJSON.Capsule)
	if err != nil {
		return "", []byte(""), err
	}

	var capsuleJSON Capsule
	err = json.Unmarshal(capsuleRaw, &capsuleJSON)
	if err != nil {
		return "", []byte(""), err
	}

	key, err := hex.DecodeString(capsuleJSON.Pk)
	if err != nil {
		return "", []byte(""), err
	}

	userCache.Set("key_"+username, key, 15*time.Minute)
	userCache.Set("id_"+username, userInfoJSON.Id, 15*time.Minute)

	return userInfoJSON.Id, key, nil
}

func computeRequestHash(req *http.Request) ([]byte, error) {
	hashing := sha512.New()
	hashing.Write([]byte(req.Method))
	hashing.Write([]byte(req.URL.String()))
	body, err := io.ReadAll(req.Body)
	if err != nil {
		return []byte(""), err
	}
	hashing.Write([]byte(body))
	return hashing.Sum(nil), nil
}

func parseRsaPublicKeyFromDerStr(pubDer []byte) (*rsa.PublicKey, error) {
	pub, err := x509.ParsePKIXPublicKey(pubDer)
	if err != nil {
		return nil, err
	}

	return pub.(*rsa.PublicKey), nil
}

func getUserAuthToken(userId string) (string, error) {
	token, found := userCache.Get("auth_" + userId)
	if found {
		return token.(string), nil
	}

	fmt.Printf("[.] requesting %s\n", AUTH_API_SERVER_HOST+"/internal/token/"+userId)
	userAuth, err := http.Get(AUTH_API_SERVER_HOST + "/internal/token/" + userId)
	if err != nil {
		return "", err
	}

	if userAuth.StatusCode != 200 {
		return "", errors.New("invalid user id")
	}

	fmt.Printf("[.] parsing data\n")
	var userAuthJSON UserAuth
	err = json.NewDecoder(userAuth.Body).Decode(&userAuthJSON)
	if err != nil {
		return "", err
	}

	userCache.Set("auth_"+userId, userAuthJSON.Token, time.Duration(userAuthJSON.Expiration)*time.Second)

	return userAuthJSON.Token, nil
}

func handleRequest(rw http.ResponseWriter, req *http.Request) {
	fmt.Printf("[reverse auth proxy server] received request at %s\n", time.Now())

	// Get Signature headers
	signatureHex, user, err := getSignatureHeaders(req.Header)
	if err != nil {
		rw.WriteHeader(http.StatusBadRequest)
		_, _ = fmt.Fprint(rw, err)
		return
	}
	signature, err := hex.DecodeString(signatureHex)
	if err != nil {
		rw.WriteHeader(http.StatusBadRequest)
		_, _ = fmt.Fprint(rw, err)
		return
	}

	// Get user public key
	userId, publicKeyDer, err := getUserPublicKey(user)
	if err != nil {
		rw.WriteHeader(http.StatusProxyAuthRequired)
		_, _ = fmt.Fprint(rw, err)
		return
	}
	publicKey, err := parseRsaPublicKeyFromDerStr(publicKeyDer)
	if err != nil {
		rw.WriteHeader(http.StatusProxyAuthRequired)
		_, _ = fmt.Fprint(rw, err)
		return
	}

	hash, err := computeRequestHash(req)
	if err != nil {
		rw.WriteHeader(http.StatusProxyAuthRequired)
		_, _ = fmt.Fprint(rw, "error decoding request")
		return
	}
	fmt.Printf("[.] request hash: %s\n", hex.EncodeToString(hash))

	// Verify signature
	err = rsa.VerifyPKCS1v15(publicKey, crypto.SHA512, hash, signature)
	if err != nil {
		fmt.Printf("[.] request signature invalid\n")
		rw.WriteHeader(http.StatusProxyAuthRequired)
		_, _ = fmt.Fprint(rw, "unauthorized")
		return
	}
	fmt.Printf("[.] request signature valid\n")

	// Request JWT token
	jwtToken, err := getUserAuthToken(userId)
	if err != nil {
		rw.WriteHeader(http.StatusProxyAuthRequired)
		_, _ = fmt.Fprint(rw, err)
		return
	}
	fmt.Printf("[.] retrieved auth token\n")

	req.AddCookie(&http.Cookie{Name: "session", Value: jwtToken})

	req.Host = apiServerURL.Host
	req.URL.Host = apiServerURL.Host
	req.URL.Scheme = apiServerURL.Scheme
	req.URL.Path = strings.Replace(req.URL.Path, "/api", "", 1)
	req.RequestURI = ""

	fmt.Printf("[reverse auth proxy server] forwarding request at %s\n", time.Now())
	netClient := &http.Client{
		Timeout: time.Second * 5,
	}

	originServerResponse, err := netClient.Do(req)
	if err != nil {
		rw.WriteHeader(http.StatusBadGateway)
		_, _ = fmt.Fprint(rw, err)
		return
	}

	rw.WriteHeader(originServerResponse.StatusCode)
	io.Copy(rw, originServerResponse.Body)
}

func main() {
	_apiServerURL, err := url.Parse(API_SERVER_HOST)
	if len(API_SERVER_HOST) == 0 || err != nil {
		log.Fatal("invalid API server URL")
	}
	apiServerURL = _apiServerURL

	_, err = url.Parse(AUTH_API_SERVER_HOST)
	if len(AUTH_API_SERVER_HOST) == 0 || err != nil {
		log.Fatal("invalid AUTH server URL")
	}

	userCache = cache.New(5*time.Minute, 5*time.Minute)

	reverseProxy := http.HandlerFunc(handleRequest)

	log.Fatal(http.ListenAndServe(":8081", reverseProxy))
}
