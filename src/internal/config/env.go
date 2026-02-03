package config

import (
	"os"
)

type Config struct {
	AppName     string
	Version     string
	FrontendURL string
	IssuerURL   string
	KeyConfig   KeyPairConfig
}

type KeyPairConfig struct {
	KeyType         string
	PublicKeysPath  string
	PrivateKeysPath string
}

// envが設定されていない場合のデフォルト値
var (
	Version   = "latest"
	GitCommit = "unknown"
	GitBranch = "unknown"
)

var (
	AppName     = "UniQUE-Auth"
	FrontendURL = "http://localhost:3000"
	IssuerURL   = "http://localhost:8080"
	KeyPath     = KeyPairConfig{
		KeyType:         "RSA",
		PublicKeysPath:  "../keys/public",
		PrivateKeysPath: "../keys/private",
	}
)

func LoadConfig() *Config {
	version := Version

	if Version == "latest" {
		version = GitBranch + "@" + GitCommit
	} else {
		version = Version + "+" + GitCommit
	}

	// envから設定を読み込む
	AppNameEnv := os.Getenv("CONFIG_APP_NAME")
	if AppNameEnv == "" {
		AppNameEnv = AppName
	}
	FrontendURLEnv := os.Getenv("CONFIG_FRONTEND_URL")
	if FrontendURLEnv == "" {
		FrontendURLEnv = FrontendURL
	}
	IssuerURLEnv := os.Getenv("CONFIG_ISSUER_URL")
	if IssuerURLEnv == "" {
		IssuerURLEnv = IssuerURL
	}
	KeyPathEnv := KeyPairConfig{
		KeyType:         os.Getenv("CONFIG_KEY_TYPE"),
		PublicKeysPath:  os.Getenv("CONFIG_KEY_PUBLIC_PATH"),
		PrivateKeysPath: os.Getenv("CONFIG_KEY_PRIVATE_PATH"),
	}
	if KeyPathEnv.PublicKeysPath == "" {
		KeyPathEnv.PublicKeysPath = KeyPath.PublicKeysPath
	}
	if KeyPathEnv.PrivateKeysPath == "" {
		KeyPathEnv.PrivateKeysPath = KeyPath.PrivateKeysPath
	}
	if KeyPathEnv.KeyType == "" {
		KeyPathEnv.KeyType = KeyPath.KeyType
	}
	return &Config{
		AppName:     AppNameEnv,
		FrontendURL: FrontendURLEnv,
		IssuerURL:   IssuerURLEnv,
		Version:     version,
		KeyConfig:   KeyPathEnv,
	}
}
