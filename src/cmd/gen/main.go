package main

import (
	"os"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"

	"gorm.io/gen"
)

func main() {
	//dsn := "user:password@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"
	dsn := os.Getenv("DB_DSN")

	db, err := gorm.Open(mysql.Open(dsn))
	if err != nil {
		panic(err)
	}

	g := gen.NewGenerator(gen.Config{
		OutPath: "./internal/query",
		Mode:    gen.WithDefaultQuery | gen.WithQueryInterface,
	})

	g.UseDB(db)

	// 🔥 全テーブル生成
	g.ApplyBasic(g.GenerateAllTable()...)

	g.Execute()
}
