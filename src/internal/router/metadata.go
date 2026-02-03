package router

import (
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
