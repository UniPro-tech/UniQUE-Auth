package router

import (
	"encoding/base64"
	"encoding/json"
	"errors"

	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwe"
	"gorm.io/gorm"
)

type TokenGetRequest struct {
	GrantType    string `form:"grant_type" binding:"required,oneof=authorization_code refresh_token client_credentials"`
	Code         string `form:"code"`
	RedirectURI  string `form:"redirect_uri"`
	ClientID     string `form:"client_id"`
	ClientSecret string `form:"client_secret"`
	RefreshToken string `form:"refresh_token"`
}

type TokenGetResponse struct {
	AccessToken  string `json:"access_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	RefreshToken string `json:"refresh_token,omitempty"`
	IDToken      string `json:"id_token,omitempty"`
}

// TokenPost godoc
// @Summary      Token Endpoint
// @Description  OAuth2 Token Endpoint
// @Tags         oauth2
// @Accept       application/x-www-form-urlencoded
// @Produce      json
// @Param        grant_type     formData  string  true   "Grant Type"  Enums(authorization_code, refresh_token, client_credentials)
// @Param        code           formData  string  false  "Authorization Code"
// @Param        redirect_uri   formData  string  false  "Redirect URI"
// @Param        client_id      formData  string  false  "Client ID"
// @Param        client_secret  formData  string  false  "Client Secret"
// @Param        refresh_token  formData  string  false  "Refresh Token"
// @Success      200  {object}  TokenGetResponse
// @Failure      400  {object}  map[string]string
// @Router       /token [post]
func TokenPost(c *gin.Context) {
	req := TokenGetRequest{}
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	switch req.GrantType {
	case "authorization_code":
		checkClientAuthentication(c, &req)
		handleAuthorizationCodeGrant(c, &req)
	case "refresh_token":
		handleRefreshTokenGrant(c, &req)
	default:
		c.JSON(400, gin.H{"error": "unsupported grant_type"})
	}
}

func handleAuthorizationCodeGrant(c *gin.Context, req *TokenGetRequest) {
	// get DB + query instance
	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.JSON(500, gin.H{"error": "database not available"})
		return
	}
	q := query.Use(db)

	// get authorization request by authorization code
	authReq, err := q.AuthorizationRequest.Where(q.AuthorizationRequest.Code.Eq(req.Code)).First()
	if err != nil || authReq == nil {
		c.JSON(400, gin.H{"error": "invalid authorization code"})
		return
	}

	if authReq.RedirectURI != req.RedirectURI {
		c.JSON(400, gin.H{"error": "redirect_uri does not match"})
		return
	}

	// generate tokens and respond
	if authReq.SessionID == nil || *authReq.SessionID == "" {
		c.JSON(400, gin.H{"error": "invalid session"})
		return
	}

	session, err := q.Session.Where(q.Session.ID.Eq(*authReq.SessionID)).First()
	if err != nil || session == nil {
		c.JSON(400, gin.H{"error": "invalid session"})
		return
	}
	consent, err := q.Consent.Where(q.Consent.UserID.Eq(session.UserID), q.Consent.ApplicationID.Eq(authReq.ApplicationID)).First()
	if err != nil || consent == nil {
		c.JSON(400, gin.H{"error": "invalid consent"})
		return
	}
	accessToken, idToken, refreshToken, err := util.GenerateTokens(db, *c.MustGet("config").(*config.Config), consent, authReq.Scope, derefPtr(authReq.Nonce))
	if err != nil {
		c.JSON(400, gin.H{"error": "failed to generate tokens", "detail": err.Error()})
		return
	}
	c.JSON(200, TokenGetResponse{
		AccessToken:  accessToken,
		TokenType:    "Bearer",
		ExpiresIn:    3600,
		RefreshToken: refreshToken,
		IDToken:      idToken,
	})
}

func handleRefreshTokenGrant(c *gin.Context, req *TokenGetRequest) {
	config := *c.MustGet("config").(*config.Config)
	// perse refresh token
	jweObj, err := jwe.ParseEncrypted(req.RefreshToken)
	if err != nil {
		c.JSON(400, gin.H{"error": "invalid refresh token"})
		return
	}

	// Try to decrypt with each private key until one succeeds
	var decryptedObj []byte
	var decErr error
	for _, kp := range config.KeyPairs {
		decryptedObj, decErr = jweObj.Decrypt(&kp.PrivateKey)
		if decErr == nil {
			break
		}
	}
	if decErr != nil {
		c.JSON(400, gin.H{"error": "invalid refresh token"})
		return
	}

	// parse decrypted payload into refresh token claims to extract JTI
	var claims util.RefreshTokenClaims
	if err := json.Unmarshal(decryptedObj, &claims); err != nil {
		c.JSON(400, gin.H{"error": "invalid refresh token payload"})
		return
	}

	// get tokenset by JTI from decrypted claims
	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.JSON(500, gin.H{"error": "database not available"})
		return
	}
	q := query.Use(db)

	tokenset, err := q.OauthToken.Where(q.OauthToken.RefreshTokenJti.Eq(claims.ID)).First()

	if err != nil || tokenset == nil {
		c.JSON(400, gin.H{"error": "invalid refresh token"})
		return
	}

	// get consent
	consent, err := q.Consent.Where(q.Consent.ID.Eq(tokenset.ConsentID)).First()
	if err != nil || consent == nil {
		c.JSON(400, gin.H{"error": "invalid consent"})
		return
	}

	accessToken, idToken, refreshToken, err := util.GenerateTokens(db, config, consent, claims.Scope, "")
	if err != nil {
		c.JSON(400, gin.H{"error": "failed to generate tokens", "detail": err.Error()})
		return
	}

	c.JSON(200, TokenGetResponse{
		AccessToken:  accessToken,
		TokenType:    "Bearer",
		ExpiresIn:    3600,
		RefreshToken: refreshToken,
		IDToken:      idToken,
	})
}

func checkClientAuthentication(c *gin.Context, req *TokenGetRequest) {
	// check client_secret
	if clientVerifyBasic := c.GetHeader("Authorization"); clientVerifyBasic != "" {
		// if authorization header
		clientID, clientSecret, err := parseBasicAuth(clientVerifyBasic)
		if err != nil {
			c.JSON(400, gin.H{"error": "not valid authorization header"})
			return
		}
		dbAny := c.MustGet("db")
		db, ok := dbAny.(*gorm.DB)
		if !ok || db == nil {
			c.JSON(500, gin.H{"error": "database not available"})
			return
		}
		q := query.Use(db)

		application, err := q.Application.Where(q.Application.ID.Eq(clientID), q.Application.ClientSecret.Eq(clientSecret)).Find()
		if err != nil || application == nil {
			c.JSON(400, gin.H{"error": "invalid client credentials"})
			return
		}
	} else {
		// if form body
		dbAny := c.MustGet("db")
		db, ok := dbAny.(*gorm.DB)
		if !ok || db == nil {
			c.JSON(500, gin.H{"error": "database not available"})
			return
		}
		q := query.Use(db)

		application, err := q.Application.Where(q.Application.ID.Eq(req.ClientID), q.Application.ClientSecret.Eq(req.ClientSecret)).Find()
		if err != nil || application == nil {
			c.JSON(400, gin.H{"error": "invalid client credentials"})
			return
		}
	}
}

func parseBasicAuth(authHeader string) (string, string, error) {
	base64Decoded, err := base64.StdEncoding.DecodeString(authHeader[len("Basic "):])
	if err != nil {
		return "", "", err
	}
	parts := string(base64Decoded)
	for i := 0; i < len(parts); i++ {
		if parts[i] == ':' {
			return parts[:i], parts[i+1:], nil
		}
	}
	return "", "", errors.New("invalid basic auth format")
}
