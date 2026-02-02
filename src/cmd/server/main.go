package main

import (
	"log"
	"net/http"

	"github.com/UniPro-tech/UniQUE-Auth/docs"
	"github.com/UniPro-tech/UniQUE-Auth/internal/db"
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
// @Description do health check
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
	// Initialize database
	dbConnection, err := db.NewDB()
	dbConnection.Logger = dbConnection.Logger.LogMode(logger.Info)
	if err != nil {
		log.Fatal(err)
	}

	// loggerとrecoveryミドルウェア付きGinルーター作成
	r := gin.Default()
	docs.SwaggerInfo.BasePath = "/"

	r.GET("/health", healthCheck)

	// Start server
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))
	r.Run()
}
