package router

import (
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/pem"
	"log/slog"
	"os"
	"path/filepath"

	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/gin-gonic/gin"
)

// WellKnownOpenIDConfiguration godoc
// @Summary OpenID Configuration
// @Description .well-known/openid-configuration エンドポイント
// @Produce json
// @Tags Metadata
// @Success 200 {object} map[string]interface{}
// @Router /.well-known/openid-configuration [get]
func WellKnownOpenIDConfiguration(c *gin.Context) {
	environmentConfigs := c.MustGet("config").(*config.Config)

	c.JSON(200, gin.H{
		"issuer":                                environmentConfigs.IssuerURL,
		"authorization_endpoint":                environmentConfigs.IssuerURL + "/authorization",
		"token_endpoint":                        environmentConfigs.IssuerURL + "/token",
		"userinfo_endpoint":                     environmentConfigs.IssuerURL + "/userinfo",
		"revocation_endpoint":                   environmentConfigs.IssuerURL + "/revocation",
		"jwks_uri":                              environmentConfigs.IssuerURL + "/.well-known/jwks.json",
		"response_types_supported":              []string{"code" /* TODO: Impliment "code token", etc... */},
		"subject_types_supported":               []string{"public"},
		"id_token_signing_alg_values_supported": []string{"RS256"},
		"scopes_supported":                      config.Scopes.AllowedScopes,
		"token_endpoint_auth_methods_supported": []string{"client_secret_basic" /* TODO: Impliment "client_secret_post",*/},
		"claims_supported": []string{
			"sub",
			"iss",
			"aud",
			"exp",
			"iat",
			"name",
			"preferred_username",
			"email",
		},
		"code_challenge_methods_supported": []string{"S256"},
		"grant_types_supported":            []string{"authorization_code", "refresh_token"},
	})
}

// WellKnownJWKS godoc
// @Summary JSON Web Key Set
// @Description .well-known/jwks.json エンドポイント
// @Produce json
// @Tags Metadata
// @Success 200 {object} map[string]interface{}
// @Router /.well-known/jwks.json [get]
func WellKnownJWKS(c *gin.Context) {
	// Get Keys Path from config
	environmentConfigs := c.MustGet("config").(*config.Config)

	jwks, err := generateJWKS(environmentConfigs.KeyConfig.PublicKeysPath, environmentConfigs.KeyConfig.KeyType)
	if err != nil {
		c.JSON(500, gin.H{"error": "internal_server_error"})
		return
	}
	c.JSON(200, jwks)
}

func generateJWKS(publicKeysPath, keyType string) (map[string]interface{}, error) {
	keys, err := loadPublicKeys(publicKeysPath, keyType)
	if err != nil {
		return nil, err
	}

	result := map[string]interface{}{
		"keys": keys,
	}
	return result, nil
}

func loadPublicKeys(publicKeysPath, keyType string) ([]interface{}, error) {
	// For simplicity, only RSA is implemented here.
	if keyType != "RSA" {
		slog.Warn("Unsupported key type: " + keyType)
		return nil, nil
	}

	rsaKeys, err := loadRSAPublicKeys(publicKeysPath)
	if err != nil {
		return nil, err
	}

	var result []interface{}
	for _, key := range rsaKeys {
		result = append(result, key)
	}
	return result, nil
}

func loadRSAPublicKeys(publicKeysPath string) ([]interface{}, error) {
	var result []interface{}

	files, err := os.ReadDir(publicKeysPath)
	if err != nil {
		return nil, err
	}

	for _, f := range files {
		if f.IsDir() {
			continue
		}
		ext := filepath.Ext(f.Name())
		if ext != ".pem" && ext != ".pub" && ext != ".crt" && ext != ".key" {
			continue
		}

		data, err := os.ReadFile(filepath.Join(publicKeysPath, f.Name()))
		if err != nil {
			return nil, err
		}

		// support files that may contain multiple PEM blocks
		for {
			var block *pem.Block
			block, data = pem.Decode(data)
			if block == nil {
				break
			}

			var pub interface{}
			var parseErr error
			pub, parseErr = x509.ParsePKIXPublicKey(block.Bytes)
			if parseErr != nil {
				// try PKCS1 (RSA) parsing
				var rsaKey *rsa.PublicKey
				rsaKey, parseErr = x509.ParsePKCS1PublicKey(block.Bytes)
				if parseErr == nil {
					pub = rsaKey
				}
			}
			if parseErr != nil {
				// skip non-public-key blocks
				continue
			}

			rsaPub, ok := pub.(*rsa.PublicKey)
			if !ok {
				continue
			}

			// marshal to PKIX DER to compute kid
			der, err := x509.MarshalPKIXPublicKey(rsaPub)
			if err != nil {
				continue
			}
			thumb := sha256.Sum256(der)
			kid := hex.EncodeToString(thumb[:])

			// n (modulus) and e (exponent) in base64url (no padding)
			n := base64.RawURLEncoding.EncodeToString(rsaPub.N.Bytes())

			// convert exponent to big-endian bytes
			eInt := rsaPub.E
			eBytes := []byte{}
			for x := eInt; x > 0; x >>= 8 {
				eBytes = append([]byte{byte(x & 0xff)}, eBytes...)
			}
			if len(eBytes) == 0 {
				eBytes = []byte{0}
			}
			e := base64.RawURLEncoding.EncodeToString(eBytes)

			jwk := map[string]interface{}{
				"kty": "RSA",
				"use": "sig",
				"alg": "RS256",
				"kid": kid,
				"n":   n,
				"e":   e,
			}
			result = append(result, jwk)
		}
	}

	return result, nil
}
