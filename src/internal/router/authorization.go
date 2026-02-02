package router

import (
	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
)

type AuthorizationRequest struct {
	ClientID            string  `form:"client_id" binding:"required"`
	RedirectURI         string  `form:"redirect_uri" binding:"required"`
	ResponseType        string  `form:"response_type" binding:"required,oneof=code token"`
	Scope               string  `form:"scope" binding:"required"`
	State               *string `form:"state"`
	Nonce               *string `form:"nonce"`
	CodeChallenge       *string `form:"code_challenge"`
	CodeChallengeMethod *string `form:"code_challenge_method" binding:"omitempty,oneof=plain S256"`
}

// AuthorizationGet godoc
// @Summary authorization endpoint
// @Schemes
// @Description do authorization
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

	// If client_id, redirect_uri, response_type, scope are valid, redirect to frontend
	client, err := query.Application.Where(query.Application.ID.Eq(req.ClientID)).First()
	if err != nil || client == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=invalid_client")
		return
	}

	redirectURI, err := query.RedirectURI.Where(query.RedirectURI.URI.Eq(req.RedirectURI), query.RedirectURI.ApplicationID.Eq(req.ClientID)).First()
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
	err = query.AuthorizationRequest.Create(&model.AuthorizationRequest{
		ApplicationID:       req.ClientID,
		RedirectURI:         req.RedirectURI,
		ResponseType:        req.ResponseType,
		Scope:               req.Scope,
		State:               derefPtr(req.State),
		Nonce:               derefPtr(req.Nonce),
		CodeChallenge:       derefPtr(req.CodeChallenge),
		CodeChallengeMethod: derefPtr(req.CodeChallengeMethod),
	})

	if err != nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=internal_server_error")
		return
	}

	createdAuthorizationRequest, err := query.AuthorizationRequest.Where(
		query.AuthorizationRequest.ApplicationID.Eq(req.ClientID),
		query.AuthorizationRequest.RedirectURI.Eq(req.RedirectURI),
	).Order(query.AuthorizationRequest.CreatedAt.Desc()).First()

	if err != nil || createdAuthorizationRequest == nil {
		c.Redirect(302, config.FrontendURL+"/authorization?error=internal_server_error")
		return
	}

	// Redirect to frontend authorization page with original query parameters
	config := c.MustGet("config").(config.Config)
	c.Redirect(302, config.FrontendURL+"/authorization?auth_request_id="+createdAuthorizationRequest.ID)
}

// AuthorizationPost godoc
// @Summary authorization endpoint
// @Schemes
// @Description do authorization
// @Tags authorization
// @Accept json
// @Produce json
// @Success 200 {string} string "OK"
// @Router /authorization [post]
func AuthorizationPost(c *gin.Context) {
	// TODO: Implement authorization logic from Frontend
	c.JSON(200, gin.H{"message": "OK"})
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
