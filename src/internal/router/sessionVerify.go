package router

import (
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
)

type SessionVerifyRequest struct {
	jit string `form:"jit" binding:"required"`
}

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
// @Param jit query string true "JIT"
// @Accept json
// @Router /internal/session_verify [get]
func SessionVerifyGet(c *gin.Context) {
	req := SessionVerifyRequest{}
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	session, err := query.Session.Where(query.Session.ID.Eq(req.jit), query.Session.DeletedAt.IsNull(), query.Session.ExpiresAt.Gt(time.Now())).First()
	if err != nil {
		c.JSON(200, SessionVerifyResponse{Valid: false})
		return
	}
	c.JSON(200, SessionVerifyResponse{Valid: true, ExpiresAt: session.ExpiresAt})
}
