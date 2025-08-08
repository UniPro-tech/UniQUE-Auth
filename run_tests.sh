#!/bin/bash

# テスト用のネットワークを作成（存在しない場合）
docker network create unique_test 2>/dev/null || true

# テストを実行
docker-compose -f dev/docker-compose.test.yaml up --build --abort-on-container-exit

# 終了コードを取得
exit_code=$?

# コンテナを削除
docker-compose -f dev/docker-compose.test.yaml down

# テスト用のネットワークを削除
docker network rm unique_test 2>/dev/null || true

# 終了コードを返す
exit $exit_code