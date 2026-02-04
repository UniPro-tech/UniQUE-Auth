package router

import (
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
)

type UpdateLastLoginedRequest struct {
	SID string `json:"sid" binding:"required"`
}

// UpdateLastLogined godoc
// @Summary      Update Last Logined
// @Description  内部のLastLogined更新エンドポイント
// @Tags         internal
// @Success      201  {null}  ""
// @Failure      400  {object}  map[string]string
// @Router       /internal/update_last_logined [post]
func UpdateLastLogined(c *gin.Context) {
	req := UpdateLastLoginedRequest{}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	session, err := query.Session.Where(query.Session.ID.Eq(req.SID), query.Session.DeletedAt.IsNull()).First()
	if err != nil || session == nil {
		c.JSON(400, gin.H{"error": "invalid session id"})
		return
	}

	session.LastLoginAt = time.Now()
	if err := query.Session.Save(session); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	c.Status(201)
}
