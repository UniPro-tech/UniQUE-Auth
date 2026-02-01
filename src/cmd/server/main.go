package main

import (
	"log"

	"github.com/UniPro-tech/UniQUE-Auth/internal/db"
	"gorm.io/gorm/logger"
)

func main() {
	// Initialize database
	dbConnection, err := db.NewDB()
	dbConnection.Logger = dbConnection.Logger.LogMode(logger.Info)
	if err != nil {
		log.Fatal(err)
	}

	err = db.SetupDB(dbConnection)
	if err != nil {
		log.Fatal(err)
	}
}
