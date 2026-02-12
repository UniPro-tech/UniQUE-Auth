package router

import (
	"math/rand"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/oklog/ulid"
	"gorm.io/gorm"
)

type AuthorizationRequest struct {
	ClientID            string  `form:"client_id" binding:"required"`
	RedirectURI         string  `form:"redirect_uri" binding:"required"`
	ResponseType        string  `form:"response_type" binding:"required,oneof=code token"`
	Scope               string  `form:"scope" binding:"required"`
	State               *string `form:"state"`
	Nonce               *string `form:"nonce"`
	Prompt              *string `form:"prompt"`
	CodeChallenge       *string `form:"code_challenge"`
	CodeChallengeMethod *string `form:"code_challenge_method" binding:"omitempty,oneof=plain S256"`
}

// AuthorizationGet godoc
// @Summary authorization endpoint
// @Schemes
// @Description OAuth 2.0 / OIDC における認可エンドポイントです。クライアントアプリケーションがユーザーの認可を取得するために使用します。
// @Tags authorization
// @Param client_id query string true "Client ID"
// @Param redirect_uri query string true "Redirect URI"
// @Param response_type query string true "Response Type"
// @Param scope query string true "Scope"
// @Param state query string false "State"
// @Param nonce query string false "Nonce"
// @Param code_challenge query string false "Code Challenge"
// @Param code_challenge_method query string false "Code Challenge Method"
// @Success 302 {string} string "Redirect to frontend authorization page"
// @Router /authorization [get]
func AuthorizationGet(c *gin.Context) {
	// Validate query parameters
	var req AuthorizationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=internal_server_error")
		return
	}
	q := query.Use(db)

	// If client_id, redirect_uri, response_type, scope are valid, redirect to frontend
	client, err := q.Application.Where(q.Application.ID.Eq(req.ClientID)).First()
	if err != nil || client == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=invalid_client")
		return
	}

	redirectURI, err := q.RedirectURI.Where(q.RedirectURI.URI.Eq(req.RedirectURI), q.RedirectURI.ApplicationID.Eq(req.ClientID)).First()
	if err != nil || redirectURI == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=invalid_redirect_uri")
		return
	}

	// Only "code" response type is supported for now
	if req.ResponseType != "code" {
		c.Redirect(302, config.FrontendURL+"/authorization?error=unsupported_response_type")
		return
	}

	// Validate scopes
	requestedScopes := map[string]bool{}
	for _, scope := range splitAndTrim(req.Scope) {
		requestedScopes[scope] = true
	}

	for _, allowedScope := range config.Scopes.AllowedScopes {
		delete(requestedScopes, allowedScope)
	}

	if len(requestedScopes) > 0 {
		c.Redirect(302, config.FrontendURL+"/authorization?error=invalid_scope")
		return
	}

	// save the request parameters in the session or database as needed
	err = q.AuthorizationRequest.Create(&model.AuthorizationRequest{
		ApplicationID:       req.ClientID,
		RedirectURI:         req.RedirectURI,
		ResponseType:        req.ResponseType,
		Scope:               req.Scope,
		State:               req.State,
		Nonce:               req.Nonce,
		Prompt:              derefPrompt(req.Prompt),
		CodeChallenge:       req.CodeChallenge,
		CodeChallengeMethod: req.CodeChallengeMethod,
		ExpiresAt:           time.Now().Add(20 * time.Minute),
	})

	if err != nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=internal_server_error")
		return
	}

	createdAuthorizationRequest, err := q.AuthorizationRequest.Where(
		q.AuthorizationRequest.ApplicationID.Eq(req.ClientID),
		q.AuthorizationRequest.RedirectURI.Eq(req.RedirectURI),
	).Order(q.AuthorizationRequest.CreatedAt.Desc()).First()

	if err != nil || createdAuthorizationRequest == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=internal_server_error")
		return
	}

	// Redirect to frontend authorization page with original query parameters
	cfg := c.MustGet("config").(*config.Config)
	// preserve original params so frontend can render without extra API calls
	v := url.Values{}
	v.Set("auth_request_id", createdAuthorizationRequest.ID)
	v.Set("client_id", req.ClientID)
	v.Set("redirect_uri", req.RedirectURI)
	v.Set("response_type", req.ResponseType)
	v.Set("scope", req.Scope)
	if req.State != nil {
		v.Set("state", *req.State)
	}
	if req.Nonce != nil {
		v.Set("nonce", *req.Nonce)
	}
	if req.CodeChallenge != nil {
		v.Set("code_challenge", *req.CodeChallenge)
	}
	if req.CodeChallengeMethod != nil {
		v.Set("code_challenge_method", *req.CodeChallengeMethod)
	}
	c.Redirect(302, strings.TrimRight(cfg.FrontendURL, "/")+"/authorization?"+v.Encode())
}

// derefPrompt returns a valid enum value for prompt; default to 'none' when not provided.
func derefPrompt(s *string) string {
	if s == nil || *s == "" {
		return "none"
	}
	return *s
}

// AuthorizationPost handles user's consent submission from the frontend form.
// It creates a Consent, marks the AuthorizationRequest as consented and generates
// an authorization code, then redirects to /consented which will forward to the client.
func AuthorizationPost(c *gin.Context) {
	clientID := c.PostForm("client_id")
	redirectURI := c.PostForm("redirect_uri")
	scope := c.PostForm("scope")
	authReqID := c.PostForm("auth_request_id")

	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "database not available"})
		return
	}
	q := query.Use(db)

	// locate authorization request
	var authReq *model.AuthorizationRequest
	var err error
	if authReqID != "" {
		authReq, err = q.AuthorizationRequest.Where(q.AuthorizationRequest.ID.Eq(authReqID)).First()
	} else {
		authReq, err = q.AuthorizationRequest.Where(
			q.AuthorizationRequest.ApplicationID.Eq(clientID),
			q.AuthorizationRequest.RedirectURI.Eq(redirectURI),
		).Order(q.AuthorizationRequest.CreatedAt.Desc()).First()
	}
	if err != nil || authReq == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid authorization request"})
		return
	}

	// get session from cookie or Authorization header
	token := ""
	if authHeader := c.GetHeader("Authorization"); authHeader != "" {
		if strings.HasPrefix(authHeader, "Bearer ") {
			token = strings.TrimPrefix(authHeader, "Bearer ")
		}
	}
	if token == "" {
		if cookie, err := c.Cookie("session_jwt"); err == nil {
			token = cookie
		}
	}
	if token == "" {
		c.Redirect(302, "/signin?error=unauthorized")
		return
	}

	cfg := c.MustGet("config").(*config.Config)
	// parse session JWT
	parsed, err := jwt.Parse(token, func(t *jwt.Token) (interface{}, error) {
		return &cfg.KeyPairs[0].PublicKey, nil
	}, jwt.WithValidMethods([]string{"RS256"}))
	if err != nil || !parsed.Valid {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid session token"})
		return
	}
	claims, ok := parsed.Claims.(jwt.MapClaims)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid session claims"})
		return
	}
	sub, _ := claims["sub"].(string)
	userID, _ := claims["user_id"].(string)
	sessionID := strings.TrimPrefix(sub, "SID_")

	// create consent record
	newConsent := &model.Consent{
		UserID:        userID,
		ApplicationID: authReq.ApplicationID,
		Scope:         scope,
	}
	if err := q.Consent.Create(newConsent); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create consent"})
		return
	}

	// generate authorization code
	t := time.Now()
	e := ulid.Monotonic(rand.New(rand.NewSource(t.UnixNano())), 0)
	code := ulid.MustNew(ulid.Timestamp(t), e).String()

	// update authorization request: set code, session and consented flag on the model and save
	authReq.Code = &code
	authReq.IsConsented = true
	if sessionID != "" {
		authReq.SessionID = &sessionID
	}
	if err := q.AuthorizationRequest.Save(authReq); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to update auth request"})
		return
	}

	writeAuditLog(c, "CONSENT", "authorization_requests/"+authReq.ID, userID, authReq.ApplicationID, sessionID, map[string]interface{}{
		"method":     c.Request.Method,
		"path":       c.Request.URL.Path,
		"status":     http.StatusMovedPermanently,
		"ip":         c.ClientIP(),
		"user_agent": c.Request.UserAgent(),
		"consent_id": newConsent.ID,
	})

	// redirect to /consented which will forward to the client's redirect_uri
	config := c.MustGet("config").(*config.Config)
	redirectTo := strings.TrimRight(config.IssuerURL, "/") + "/consented?authorization_id=" + authReq.ID
	c.Redirect(http.StatusMovedPermanently, redirectTo)
}

// splitAndTrim splits a space-separated string into a slice of strings and trims spaces.
func splitAndTrim(s string) []string {
	var result []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == ' ' {
			if start < i {
				result = append(result, s[start:i])
			}
			start = i + 1
		}
	}
	if start < len(s) {
		result = append(result, s[start:])
	}
	return result
}

// derefPtr safely dereferences a string pointer, returning an empty string if nil.
func derefPtr(s *string) string {
	if s != nil {
		return *s
	}
	return ""
}
