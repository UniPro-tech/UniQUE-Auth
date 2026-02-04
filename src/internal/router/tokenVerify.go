package router

import (
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
)

type TokenVerifyRequest struct {
	jit string `form:"jit" binding:"required"`
}

type TokenVerifyResponse struct {
	Valid bool `json:"valid"`
}

// TokenVerifyGet godoc
// @Summary token verify endpoint
// @Schemes
// @Description 内部用のトークン検証エンドポイントです。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Success 200 {object} TokenVerifyResponse "OK"
// @Param jit query string true "JIT"
// @Accept json
// @Router /internal/token_verify [get]
func TokenVerifyGet(c *gin.Context) {
	req := TokenVerifyRequest{}
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	tokenset, err := query.OauthToken.Where(query.OauthToken.AccessTokenJti.Eq(req.jit), query.OauthToken.DeletedAt.IsNull()).First()
	if err != nil || tokenset == nil {
		c.JSON(400, gin.H{"error": "invalid token"})
		return
	}

	c.JSON(200, TokenVerifyResponse{Valid: true})
}
