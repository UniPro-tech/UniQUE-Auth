package router

import (
	"net/http"
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type SessionsRequest struct {
	UserID string `form:"user_id" binding:"required"`
}

// SessionsGet godoc
// @Summary Get sessions for a user
// @Description 内部用: 指定ユーザーのセッション一覧を取得する。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Param user_id query string true "User ID"
// @Success 200 {array} SessionResponse "OK"
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /internal/sessions [get]
func SessionsGet(c *gin.Context) {
	req := SessionsRequest{}
	if err := c.ShouldBind(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.JSON(500, gin.H{"error": "database not available"})
		return
	}
	q := query.Use(db)

	sessions, err := q.Session.Where(q.Session.UserID.Eq(req.UserID), q.Session.DeletedAt.IsNull()).Order(q.Session.CreatedAt.Desc()).Find()
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	// Map to response type to avoid exposing gorm.DeletedAt in Swagger
	if sessions == nil {
		c.JSON(http.StatusOK, []SessionResponse{})
		return
	}

	resp := make([]SessionResponse, 0, len(sessions))
	for _, s := range sessions {
		if s == nil {
			continue
		}
		resp = append(resp, SessionResponse{
			ID:          s.ID,
			UserID:      s.UserID,
			IPAddress:   s.IPAddress,
			UserAgent:   s.UserAgent,
			ExpiresAt:   s.ExpiresAt,
			LastLoginAt: s.LastLoginAt,
			CreatedAt:   s.CreatedAt,
			UpdatedAt:   s.UpdatedAt,
		})
	}
	c.JSON(http.StatusOK, resp)
}

// SessionResponse is used for Swagger documentation to avoid gorm.DeletedAt parsing issues
type SessionResponse struct {
	ID          string    `json:"id"`
	UserID      string    `json:"user_id"`
	IPAddress   string    `json:"ip_address"`
	UserAgent   string    `json:"user_agent"`
	ExpiresAt   time.Time `json:"expires_at"`
	LastLoginAt time.Time `json:"last_login_at"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// SessionsDelete godoc
// @Summary Delete sessions for a user
// @Description 内部用: 指定ユーザーのセッションを削除（ソフトデリート）する。Kubernetes / Istio の認証ポリシーにより外部からのアクセスは制限されています。
// @Tags internal
// @Success 204 {string} string "No Content"
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /internal/sessions/:sid [delete]
func SessionsDelete(c *gin.Context) {
	sid := c.Param("sid")

	dbAny := c.MustGet("db")
	db, ok := dbAny.(*gorm.DB)
	if !ok || db == nil {
		c.JSON(500, gin.H{"error": "database not available"})
		return
	}
	q := query.Use(db)

	session, err := q.Session.Where(q.Session.ID.Eq(sid)).First()
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	if _, err := q.Session.Where(q.Session.ID.Eq(sid)).Delete(); err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	userID := ""
	if session != nil {
		userID = session.UserID
	}
	writeAuditLog(c, "DELETE", "sessions/"+sid, userID, "", sid, map[string]interface{}{
		"method":     c.Request.Method,
		"path":       c.Request.URL.Path,
		"status":     http.StatusNoContent,
		"ip":         c.ClientIP(),
		"user_agent": c.Request.UserAgent(),
	})

	c.Status(204)
}
