package router

import (
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
)

type ConsentPostRequest struct {
	AuthRequestID string `json:"auth_request_id" binding:"required"`
	SessionID     string `json:"session_id" binding:"required"`
	Approve       bool   `json:"approve" binding:"required"`
}

type ConsentPostResponse struct {
	AuthRequestID string `json:"auth_request_id"`
}

type ConsentGetRequest struct {
	AuthRequestID string `form:"auth_request_id" binding:"required"`
	SessionID     string `form:"session_id" binding:"required"`
}

type ConsentGetResponse struct {
	IsConsented bool `json:"is_consented"`
}

// ConsentPost godoc
// @Summary internal consent endpoint
// @Schemes
// @Description 内部用の認可エンドポイントです。同意したことを受け取ります。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Accept json
// @Produce json
// @Param request body ConsentPostRequest true "Consent Request"
// @Success 200 {object} ConsentPostResponse
// @Router /internal/authorization [post]
func ConsentPost(c *gin.Context) {
	req := ConsentPostRequest{}
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

	authReq.IsConsented = true
	authReq.SessionID = session.ID

	// codeの有効期限を5分に設定
	authReq.ExpiresAt = time.Now().Add(5 * time.Minute)

	// Generate authorization code or token based on response_type
	switch authReq.ResponseType {
	case "code":
		authReq.Code, err = util.GenerateAuthCode()
		if err != nil {
			c.JSON(500, gin.H{"error": "internal server error"})
			return
		}
	default:
		c.JSON(400, gin.H{"error": "unsupported response_type"})
		return
	}
	_, err = query.AuthorizationRequest.Update(query.AuthorizationRequest.ID.Eq(req.AuthRequestID), authReq)
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	consent, err := query.Consent.Where(query.Consent.ApplicationID.Eq(authReq.ApplicationID), query.Consent.UserID.Eq(session.UserID)).First()
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	if consent == nil {
		newConsent := &model.Consent{
			ApplicationID: authReq.ApplicationID,
			UserID:        session.UserID,
		}
		err := query.Consent.Create(newConsent)
		if err != nil {
			c.JSON(500, gin.H{"error": "internal server error"})
			return
		}
	} else {
		if !util.CompareScopes(consent.Scope, authReq.Scope) {
			// 既存の同意のスコープに追加する
			newScope := util.MergeScopes(consent.Scope, authReq.Scope)
			consent.Scope = newScope
			_, err := query.Consent.Update(query.Consent.ID.Eq(consent.ID), consent)
			if err != nil {
				c.JSON(500, gin.H{"error": "internal server error"})
				return
			}
		}
	}
	c.JSON(200, ConsentPostResponse{AuthRequestID: authReq.ID})
}

// ConsentGet godoc
// @Summary internal consent check endpoint
// @Schemes
// @Description 内部用の同意確認エンドポイントです。同意済みかどうかを確認します。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Accept json
// @Produce json
// @Param auth_request_id query string true "Authorization Request ID"
// @Param session_id query string true "Session ID"
// @Success 200 {object} ConsentGetResponse
// @Router /internal/authorization [get]
func ConsentGet(c *gin.Context) {
	authRequestID := c.Query("auth_request_id")
	sessionID := c.Query("session_id")
	authReq, err := query.AuthorizationRequest.Where(query.AuthorizationRequest.ID.Eq(authRequestID)).First()
	if authReq == nil {
		c.JSON(400, gin.H{"error": "invalid auth_request_id"})
		return
	}
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	session, err := query.Session.Where(query.Session.ID.Eq(sessionID)).First()
	if session == nil {
		c.JSON(400, gin.H{"error": "invalid session_id"})
		return
	}
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	consent, err := query.Consent.Where(
		query.Consent.ApplicationID.Eq(authReq.ApplicationID),
		query.Consent.UserID.Eq(session.UserID),
	).First()
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}

	if consent == nil || !util.CompareScopes(consent.Scope, authReq.Scope) {
		c.JSON(200, ConsentGetResponse{IsConsented: false})
		return
	}

	authReq.IsConsented = true
	authReq.SessionID = session.ID
	authReq.ExpiresAt = time.Now().Add(5 * time.Minute)
	switch authReq.ResponseType {
	case "code":
		authReq.Code, err = util.GenerateAuthCode()
		if err != nil {
			c.JSON(500, gin.H{"error": "internal server error"})
			return
		}
	default:
		c.JSON(400, gin.H{"error": "unsupported response_type"})
		return
	}

	c.JSON(200, ConsentGetResponse{IsConsented: authReq.IsConsented})
}
