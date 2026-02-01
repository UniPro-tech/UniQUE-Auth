package main

import (
	"log"
	"net/http"

	"github.com/UniPro-tech/UniQUE-Auth/internal/db"
	"gorm.io/gorm/logger"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize database
	dbConnection, err := db.NewDB()
	dbConnection.Logger = dbConnection.Logger.LogMode(logger.Info)
	if err != nil {
		log.Fatal(err)
	}

	// loggerとrecoveryミドルウェア付きGinルーター作成
	r := gin.Default()

	// ヘルスチェックエンドポイント
	r.GET("/health", func(c *gin.Context) {
		// JSONレスポンスを返す
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
		})
	})

	// Start server
	r.Run()
}
