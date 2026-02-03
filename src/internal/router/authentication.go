package router

import (
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
)

type AuthenticationRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Type     string `json:"type" binding:"required,oneof=password mfa totp"`
}

// AuthenticationPost godoc
// @Summary authentication endpoint
// @Schemes
// @Description 内部用の認証エンドポイントです。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags authentication
// @Success 200 {string} string "OK"
// @Param request body AuthenticationRequest true "Authentication Request"
// @Accpect json
// @Router /internal/authentication [post]
func AuthenticationPost(c *gin.Context) {
	req := AuthenticationRequest{}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	switch req.Type {
	case "password":
		// Handle password authentication
		ok, err := passwordAuthentication(req.Username, req.Password)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		if !ok {
			c.JSON(401, gin.H{"error": "Invalid username or password"})
			return
		}
		c.JSON(200, gin.H{"message": "Password authentication successful"})
	case "mfa":
		// Handle MFA authentication
		// Not implemented yet
		c.JSON(400, gin.H{"error": "Invalid authentication type"})
	case "totp":
		// Handle TOTP authentication
		// Not implemented yet
		c.JSON(400, gin.H{"error": "Invalid authentication type"})
	default:
		c.JSON(400, gin.H{"error": "Invalid authentication type"})
	}
}

func passwordAuthentication(username, password string) (bool, error) {
	user, err := query.User.Where(query.User.CustomID.Eq(username)).First()
	if err != nil {
		return false, err
	}
	if user == nil {
		return false, nil
	}
	if ok, err := util.VerifyPassword(password, user.PasswordHash); err != nil || !ok {
		return false, err
	}
	return true, nil
}
