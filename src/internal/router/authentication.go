package router

import (
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
)

type AuthenticationRequest struct {
	Username  string `json:"username"`
	Password  string `json:"password"`
	IPAddress string `json:"ip_address"`
	UserAgent string `json:"user_agent"`
	Type      string `json:"type" binding:"required,oneof=password mfa totp"`
	Remember  bool   `json:"remember" default:"false"`
}

type AuthenticationResponse struct {
	SessionJWT string `json:"session_jwt"`
}

// AuthenticationPost godoc
// @Summary authentication endpoint
// @Schemes
// @Description 内部用の認証エンドポイントです。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Success 200 {object} AuthenticationResponse "OK"
// @Param request body AuthenticationRequest true "Authentication Request"
// @Accept json
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
		user, err := passwordAuthentication(req.Username, req.Password)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		if user == nil {
			c.JSON(401, gin.H{"error": "Invalid username or password"})
			return
		}
		err = query.Session.Create(&model.Session{
			UserID:      user.ID,
			IPAddress:   req.IPAddress,
			UserAgent:   req.UserAgent,
			ExpiresAt:   CalculateSessionExpiry(req.Remember),
			LastLoginAt: time.Now(),
		})
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		session, err := query.Session.Where(query.Session.UserID.Eq(user.ID)).Order(query.Session.CreatedAt.Desc()).First()
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		if session == nil {
			c.JSON(500, gin.H{"error": "Failed to create session"})
			return
		}
		// Return session ID as a token
		sessionJWT, err := util.GenerateSessionJWT(session.ID, c.MustGet("config").(config.Config))
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		c.JSON(200, AuthenticationResponse{
			SessionJWT: sessionJWT,
		})
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

func passwordAuthentication(username, password string) (*model.User, error) {
	user, err := query.User.Where(query.User.CustomID.Eq(username)).First()
	if err != nil {
		return nil, err
	}
	if user == nil {
		return nil, nil
	}
	if ok, err := util.VerifyPassword(password, user.PasswordHash); err != nil || !ok {
		return nil, err
	}
	return user, nil
}

// CalculateSessionExpiry calculates the session expiry time based on the remember flag.
func CalculateSessionExpiry(remember bool) (expiryTime time.Time) {
	if remember {
		return time.Now().Add(30 * 24 * time.Hour) // 30 days
	}
	return time.Now().Add(7 * 24 * time.Hour) // 7 days
}
