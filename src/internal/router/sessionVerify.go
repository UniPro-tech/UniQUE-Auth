package router

import (
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
)

type SessionVerifyResponse struct {
	Valid     bool      `json:"valid"`
	ExpiresAt time.Time `json:"expires_at,omitempty"`
}

// SessionVerifyPost godoc
// @Summary session verify endpoint
// @Schemes
// @Description 内部用のセッション検証エンドポイントです。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Success 200 {object} SessionVerifyResponse "OK"
// @Param session_jwt query string true "Session JWT"
// @Accept json
// @Router /internal/session_verify [get]
func SessionVerifyGet(c *gin.Context) {
	sessionJWT := c.Query("session_jwt")
	session, err := util.ValidateSessionToken(sessionJWT, c)
	if err != nil {
		c.JSON(200, SessionVerifyResponse{Valid: false})
		return
	}
	c.JSON(200, SessionVerifyResponse{Valid: true, ExpiresAt: session.ExpiresAt})
}
