package router

import (
	"github.com/UniPro-tech/UniQUE-Auth/internal/query"
	"github.com/UniPro-tech/UniQUE-Auth/internal/util"
	"github.com/gin-gonic/gin"
)

type UserInfoResponse struct {
	Sub               string `json:"sub"`
	Name              string `json:"name,omitempty"`
	Bio               string `json:"bio,omitempty"`
	PreferredUsername string `json:"preferred_username,omitempty"`
	Email             string `json:"email,omitempty"`
	EmailVerified     bool   `json:"email_verified,omitempty"`
	Birthdate         string `json:"birthdate,omitempty"`
	Website           string `json:"website,omitempty"`
	Twitter           string `json:"twitter,omitempty"`
	AffiliationPeriod string `json:"affiliation_period,omitempty"`
	UpdatedAt         int64  `json:"updated_at,omitempty"`
}

// UserInfoGet godoc
// @Summary      UserInfo Endpoint
// @Description  OAuth2 UserInfo Endpoint
// @Tags         userinfo
// @Accept       json
// @Produce      json
// @Success      200  {object}  UserInfoResponse
// @Failure      400  {object}  map[string]string
// @Router       /userinfo [get]
func UserInfoGet(c *gin.Context) {
	// Authorization Headerからアクセストークンを取得
	accessToken := c.GetHeader("Authorization")
	if accessToken == "" {
		c.JSON(400, gin.H{"error": "missing access token"})
		return
	}

	// アクセストークンの検証
	_, userID, scope, err := util.ValidateAccessToken(accessToken, c)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	// ユーザー情報の取得
	user, err := query.User.Where(query.User.ID.Eq(userID), query.User.Status.Eq("active")).First()
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	if user == nil {
		c.JSON(400, gin.H{"error": "user not found"})
		return
	}

	profile, err := query.Profile.Where(query.Profile.UserID.Eq(userID)).First()
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	if profile == nil {
		c.JSON(400, gin.H{"error": "profile not found"})
		return
	}

	c.JSON(200, UserInfoResponse{
		Sub:               user.ID,
		Name:              profile.DisplayName,
		Bio:               profile.Bio,
		PreferredUsername: user.CustomID,
		Email: func() string {
			if util.ContainsScope(scope, "email") {
				return user.Email
			}
			return ""
		}(),
		EmailVerified: func() bool {
			if util.ContainsScope(scope, "email") {
				return user.EmailVerified
			}
			return false
		}(),
		Birthdate: func() string {
			if util.ContainsScope(scope, "profile") {
				return profile.Birthdate.Format("2006-01-02")
			}
			return ""
		}(),
		Website: func() string {
			if util.ContainsScope(scope, "profile") {
				return profile.WebsiteURL
			}
			return ""
		}(),
		Twitter: func() string {
			if util.ContainsScope(scope, "profile") {
				return profile.TwitterHandle
			}
			return ""
		}(),
		AffiliationPeriod: user.AffiliationPeriod,
		UpdatedAt:         profile.UpdatedAt.Unix(),
	})
}
