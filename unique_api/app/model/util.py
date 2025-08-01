import ulid


# ULIDを生成する関数
# 残念ながらMySQLのStoredFunctionでULIDの関数を使ってもこっちから呼び出せない。
def generate_ulid():
    return str(ulid.new())
