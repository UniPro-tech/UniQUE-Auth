package router

import (
	"encoding/base64"

	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type ConsentRequestBody struct {
	AuthRequestID string `json:"auth_request_id" binding:"required"`
	SessionID     string `json:"session_id" binding:"required"`
	Approve       bool   `json:"approve" binding:"required"`
}

type ConsentResponse struct {
	AuthRequestID string `json:"auth_request_id"`
}

// ConsentPost godoc
// @Summary internal consent endpoint
// @Schemes
// @Description 内部用の認可エンドポイントです。同意したことを受け取ります。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Accept json
// @Produce json
// @Param request body ConsentRequestBody true "Consent Request"
// @Success 200 {object} ConsentResponse
// @Router /internal/authorization [post]
func ConsentPost(c *gin.Context) {
	req := ConsentRequestBody{}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	authReq, err := query.AuthorizationRequest.Where(query.AuthorizationRequest.ID.Eq(req.AuthRequestID)).First()
	if authReq == nil {
		c.JSON(400, gin.H{"error": "invalid auth_request_id"})
		return
	}
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	session, err := query.Session.Where(query.Session.ID.Eq(req.SessionID)).First()
	if session == nil {
		c.JSON(400, gin.H{"error": "invalid session_id"})
		return
	}
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	if !req.Approve {
		query.AuthorizationRequest.Delete(authReq)
		c.JSON(200, gin.H{"message": "consent denied"})
		return
	}

	// Generate authorization code or token based on response_type
	switch authReq.ResponseType {
	case "code":
		code, err := uuid.NewRandom()
		if err != nil {
			c.JSON(500, gin.H{"error": "internal server error"})
			return
		}
		authReq.Code = base64.URLEncoding.EncodeToString([]byte(code.String()))
	default:
		c.JSON(400, gin.H{"error": "unsupported response_type"})
		return
	}
	_, err = query.AuthorizationRequest.Update(query.AuthorizationRequest.ID.Eq(req.AuthRequestID), authReq)
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	c.JSON(200, ConsentResponse{AuthRequestID: authReq.ID})
}
