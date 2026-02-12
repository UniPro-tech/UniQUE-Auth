package util

import (
	"crypto/sha256"
	"crypto/x509"
	"encoding/hex"
	"encoding/json"
	"errors"
	"math/rand"
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwe"
	"github.com/golang-jwt/jwt/v5"
	"github.com/oklog/ulid"
	"gorm.io/gorm"
)

// kidForKey computes the kid (SHA-256 thumbprint of PKIX DER) matching the JWKS endpoint.
func kidForKey(cfg config.Config) string {
	if len(cfg.KeyPairs) == 0 {
		return ""
	}
	// ensure the keypair appears initialized
	if cfg.KeyPairs[0].PublicKey.N == nil {
		return ""
	}
	rsaPub := &cfg.KeyPairs[0].PublicKey
	der, err := x509.MarshalPKIXPublicKey(rsaPub)
	if err != nil {
		return ""
	}
	thumb := sha256.Sum256(der)
	return hex.EncodeToString(thumb[:])
}

func hasValidKeyPair(cfg config.Config) bool {
	if len(cfg.KeyPairs) == 0 {
		return false
	}
	kp := cfg.KeyPairs[0]
	if kp.PublicKey.N == nil {
		return false
	}
	if kp.PrivateKey.D == nil {
		return false
	}
	return true
}

func GenerateTokens(db *gorm.DB, config config.Config, consent *model.Consent, scopes, nonce string) (accessToken, IDToken, RefreshToken string, err error) {
	scopes = AlphabeticScopeString(scopes)
	q := query.Use(db)

	t := time.Now()
	entropy := ulid.Monotonic(rand.New(rand.NewSource(t.UnixNano())), 0)
	accessTokenID := ulid.MustNew(ulid.Timestamp(t), entropy).String()

	entropy = ulid.Monotonic(rand.New(rand.NewSource(t.UnixNano())), 0)
	refreshTokenID := ulid.MustNew(ulid.Timestamp(t), entropy).String()

	entropy = ulid.Monotonic(rand.New(rand.NewSource(t.UnixNano())), 0)
	IDTokenID := ulid.MustNew(ulid.Timestamp(t), entropy).String()
	IDTokenString := ""

	if ContainsScope(scopes, "openid") {
		if !hasValidKeyPair(config) {
			return "", "", "", errors.New("no valid keypair configured")
		}
		IDTokenString, err = GenerateIDToken(q, IDTokenID, consent.UserID, consent.ApplicationID, nonce, scopes, config)
		if err != nil {
			return "", "", "", err
		}
	} else {
		IDTokenID = ""
	}

	err = q.OauthToken.Create(&model.OauthToken{
		ConsentID:       consent.ID,
		AccessTokenJti:  accessTokenID,
		RefreshTokenJti: refreshTokenID,
		IDTokenJti:      IDTokenID,
		ExpiresAt:       time.Now().Add(5 * 24 * time.Hour), // リフレッシュトークン有効期限: 5日
		CreatedAt:       time.Now(),
		UpdatedAt:       time.Now(),
	})
	if err != nil {
		return "", "", "", err
	}

	// Generate Access Token (use structured claims per OAuth2/OIDC)
	accessTokenClaims := jwt.NewWithClaims(jwt.SigningMethodRS256, AccessTokenClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   consent.UserID,
			Audience:  jwt.ClaimStrings{consent.ApplicationID},
			Issuer:    config.IssuerURL,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(5 * time.Hour)),
			ID:        accessTokenID,
		},
		Scope: scopes,
	})
	accessTokenClaims.Header["kid"] = kidForKey(config)
	if !hasValidKeyPair(config) {
		return "", "", "", errors.New("no valid keypair configured")
	}
	accessTokenString, err := accessTokenClaims.SignedString(&config.KeyPairs[0].PrivateKey)
	if err != nil {
		return "", "", "", err
	}

	// Generate Refresh Token
	// For simplicity, using a JWE containing the claims as the refresh token
	refreshClaims := RefreshTokenClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   consent.UserID,
			Audience:  jwt.ClaimStrings{consent.ApplicationID},
			Issuer:    config.IssuerURL,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(5 * 24 * time.Hour)),
			ID:        refreshTokenID,
		},
		Scope: scopes,
	}
	// marshal claims to plaintext bytes for JWE
	plaintext, err := json.Marshal(refreshClaims)
	if err != nil {
		return "", "", "", err
	}

	// create JWE with new signature: (alg, key, method, plaintext)
	if !hasValidKeyPair(config) {
		return "", "", "", errors.New("no valid keypair configured")
	}
	refreshTokenClaim, err := jwe.NewJWE(jwe.KeyAlgorithmRSAOAEP, &config.KeyPairs[0].PublicKey, jwe.EncryptionTypeA256GCM, plaintext)
	if err != nil {
		return "", "", "", err
	}

	// finalize/serialize the JWE to string
	refreshTokenString, err := refreshTokenClaim.CompactSerialize()
	if err != nil {
		return "", "", "", err
	}
	return accessTokenString, IDTokenString, refreshTokenString, nil
}

type OIDCTokenClaims struct {
	jwt.RegisteredClaims
	Nonce string `json:"nonce,omitempty"`
	// Standard Profile Claims
	Name              string `json:"name"`
	Email             string `json:"email,omitempty"`
	EmailVerified     bool   `json:"email_verified,omitempty"`
	PreferredUsername string `json:"preferred_username,omitempty"`
	Website           string `json:"website,omitempty"`
	Birthdate         string `json:"birthdate,omitempty"`
	UpdatedAt         int64  `json:"updated_at,omitempty"`
}

type AccessTokenClaims struct {
	jwt.RegisteredClaims
	Scope string `json:"scope,omitempty"`
}

type RefreshTokenClaims struct {
	jwt.RegisteredClaims
	Scope string `json:"scope,omitempty"`
}

func GenerateIDToken(q *query.Query, jti, userID, clientID, nonce, scopes string, config config.Config) (string, error) {
	user, err := q.User.Where(q.User.ID.Eq(userID)).First()
	if err != nil {
		return "", err
	}
	if user == nil {
		return "", errors.New("user not found")
	}
	profile, err := q.Profile.Where(q.Profile.UserID.Eq(userID)).First()
	if err != nil {
		return "", err
	}
	if profile == nil {
		return "", errors.New("profile not found")
	}
	IDTokenClaims := jwt.NewWithClaims(jwt.SigningMethodRS256, OIDCTokenClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   userID,
			Audience:  jwt.ClaimStrings{clientID},
			Issuer:    config.IssuerURL,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(5 * time.Hour)),
			ID:        jti,
		},
		Nonce: nonce,
		Name:  profile.DisplayName,
		Email: func() string {
			if ContainsScope(scopes, "email") {
				return user.Email
			}
			return ""
		}(),
		EmailVerified: func() bool {
			if ContainsScope(scopes, "email") {
				return user.EmailVerified
			}
			return false
		}(),
		PreferredUsername: user.CustomID,
		Website: func() string {
			if ContainsScope(scopes, "profile") {
				return profile.WebsiteURL
			}
			return ""
		}(),
		Birthdate: func() string {
			if ContainsScope(scopes, "profile") {
				return profile.Birthdate.String()
			}
			return ""
		}(),
		UpdatedAt: profile.UpdatedAt.Unix(),
	})
	IDTokenClaims.Header["kid"] = kidForKey(config)
	if !hasValidKeyPair(config) {
		return "", errors.New("no valid keypair configured")
	}
	IDTokenString, err := IDTokenClaims.SignedString(&config.KeyPairs[0].PrivateKey)
	return IDTokenString, err
}

func ValidateAccessToken(tokenString string, c *gin.Context) (jit, sub, scope string, err error) {
	config := *c.MustGet("config").(*config.Config)

	// Parse and validate token
	token, err := jwt.ParseWithClaims(tokenString, &AccessTokenClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Verify the signing method
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, errors.New("unexpected signing method")
		}
		// Return the public key for verification
		if !hasValidKeyPair(config) {
			return nil, errors.New("no valid keypair configured")
		}
		return &config.KeyPairs[0].PublicKey, nil
	})
	if err != nil {
		return "", "", "", err
	}

	// Validate claims
	if claims, ok := token.Claims.(*AccessTokenClaims); ok && token.Valid {
		tokenSet, err := query.OauthToken.Where(query.OauthToken.AccessTokenJti.Eq(claims.ID), query.OauthToken.DeletedAt.IsNull()).First()
		if err != nil {
			return "", "", "", err
		}
		if tokenSet == nil {
			return "", "", "", errors.New("invalid token")
		}
		return claims.ID, claims.Subject, claims.Scope, nil
	} else {
		return "", "", "", errors.New("invalid token claims")
	}
}

type SessionTokenClaims struct {
	jwt.RegisteredClaims
	UserID string `json:"user_id"`
}

func GenerateSessionJWT(sessionID, userID string, config config.Config) (string, error) {
	// Generate Session JWT
	sessionTokenClaims := jwt.NewWithClaims(jwt.SigningMethodRS256, SessionTokenClaims{
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   "SID_" + sessionID,
			Issuer:    config.IssuerURL,
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
		},
		UserID: userID,
	})
	sessionTokenClaims.Header["kid"] = kidForKey(config)
	if !hasValidKeyPair(config) {
		return "", errors.New("no valid keypair configured")
	}
	sessionTokenString, err := sessionTokenClaims.SignedString(&config.KeyPairs[0].PrivateKey)
	if err != nil {
		return "", err
	}
	return sessionTokenString, nil
}
