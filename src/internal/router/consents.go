package router

import (
	"net/http"
	"time"

	"github.com/UniPro-tech/UniQUE-Auth/internal/model"
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/gin-gonic/gin"
	"gorm.io/gen"
)

type ConsentCreateRequest struct {
	UserID        string `json:"user_id" binding:"required"`
	ApplicationID string `json:"application_id" binding:"required"`
	Scope         string `json:"scope" binding:"required"`
}

// ConsentResponse is used for Swagger responses to avoid depending on gorm.DeletedAt
type ConsentResponse struct {
	ID            string     `json:"id"`
	UserID        string     `json:"user_id"`
	ApplicationID string     `json:"application_id"`
	Scope         string     `json:"scope"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`
	DeletedAt     *time.Time `json:"deleted_at"`
}

// ConsentList godoc
// @Summary list or search consents
// @Description 一覧取得およびクエリ条件による検索を行う。
// @Tags internal
// @Accept json
// @Produce json
// @Param user_id query string false "User ID"
// @Param application_id query string false "Application ID"
// @Param scope query string false "Scope"
// @Success 200 {array} router.ConsentResponse
// @Router /internal/consents [get]
func ConsentList(c *gin.Context) {
	userID := c.Query("user_id")
	appID := c.Query("application_id")
	scope := c.Query("scope")

	var (
		results []*model.Consent
		err     error
	)

	if userID == "" && appID == "" && scope == "" {
		results, err = query.Consent.Find()
		if err != nil {
			c.JSON(500, gin.H{"error": "internal server error"})
			return
		}
		c.JSON(200, results)
		return
	}

	// build conditions
	conds := []gen.Condition{}
	if userID != "" {
		conds = append(conds, query.Consent.UserID.Eq(userID))
	}
	if appID != "" {
		conds = append(conds, query.Consent.ApplicationID.Eq(appID))
	}
	if scope != "" {
		conds = append(conds, query.Consent.Scope.Eq(scope))
	}

	// perform query
	if len(conds) > 0 {
		results, err = query.Consent.Where(conds...).Find()
	} else {
		results, err = query.Consent.Find()
	}
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	c.JSON(200, results)
}

// ConsentCreate godoc
// @Summary create consent
// @Tags internal
// @Accept json
// @Produce json
// @Param request body ConsentCreateRequest true "Create Consent"
// @Success 201 {object} router.ConsentResponse
// @Router /internal/consents [post]
func ConsentCreate(c *gin.Context) {
	req := ConsentCreateRequest{}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	newConsent := &model.Consent{
		UserID:        req.UserID,
		ApplicationID: req.ApplicationID,
		Scope:         req.Scope,
	}
	if err := query.Consent.Create(newConsent); err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	c.JSON(http.StatusCreated, newConsent)
}

// ConsentDeleteByID godoc
// @Summary delete consent by id
// @Tags internal
// @Accept json
// @Produce json
// @Param id path string true "Consent ID"
// @Success 200 {object} map[string]string
// @Router /internal/consents/{id} [delete]
func ConsentDeleteByID(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(400, gin.H{"error": "id required"})
		return
	}
	consent, err := query.Consent.Where(query.Consent.ID.Eq(id)).First()
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	if consent == nil {
		c.JSON(404, gin.H{"error": "consent not found"})
		return
	}
	_, err = query.Consent.Delete(consent)
	if err != nil {
		c.JSON(500, gin.H{"error": "internal server error"})
		return
	}
	c.JSON(200, gin.H{"message": "deleted"})
}
