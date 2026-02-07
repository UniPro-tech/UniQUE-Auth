package main

import (
	"log"
	"net/http"

	"github.com/UniPro-tech/UniQUE-Auth/docs"
	"github.com/UniPro-tech/UniQUE-Auth/internal/config"
	"github.com/UniPro-tech/UniQUE-Auth/internal/db"
	"github.com/UniPro-tech/UniQUE-Auth/internal/router"
	swaggerfiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"gorm.io/gorm/logger"

	"github.com/gin-gonic/gin"
)

type HealthResponse struct {
	Status string `json:"status"`
}

// @BasePath /

// HealthCheck godoc
// @Summary health check endpoint
// @Schemes
// @Description システムの稼働状況を確認するためのエンドポイントです。
// @Tags system info
// @Accept json
// @Produce json
// @Success 200 {object} HealthResponse
// @Router /health [get]
func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, HealthResponse{
		Status: "ok",
	})
}

func main() {
	environmentConfigs := config.LoadConfig()

	// Initialize database
	dbConnection, err := db.NewDB()
	dbConnection.Logger = dbConnection.Logger.LogMode(logger.Info)
	if err != nil {
		log.Fatal(err)
	}

	// loggerとrecoveryミドルウェア付きGinルーター作成
	r := gin.Default()

	// Swagger Info
	docs.SwaggerInfo.BasePath = "/"
	docs.SwaggerInfo.Title = environmentConfigs.AppName + " Auth API"
	docs.SwaggerInfo.Version = environmentConfigs.Version

	// Add contexts
	r.Use(func(c *gin.Context) {
		c.Set("config", environmentConfigs)
		c.Set("db", dbConnection)
		c.Next()
	})

	// Routes
	r.GET("/health", healthCheck)
	r.GET("/authorization", router.AuthorizationGet)
	r.GET("/.well-known/openid-configuration", router.WellKnownOpenIDConfiguration)
	r.GET("/.well-known/jwks.json", router.WellKnownJWKS)
	r.POST("/token", router.TokenPost)
	r.GET("/userinfo", router.UserInfoGet)

	// Internal routes
	r.POST("/internal/authentication", router.AuthenticationPost)
	r.GET("/internal/consents", router.ConsentList)
	r.POST("/internal/consents", router.ConsentCreate)
	r.DELETE("/internal/consents/:id", router.ConsentDeleteByID)
	r.POST("/internal/password_hash", router.PasswordHashPost)

	// Start server
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))
	r.Run()
}
