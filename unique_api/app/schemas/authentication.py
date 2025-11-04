from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AuthenticationRequest(BaseModel):
    """
    AuthenticationRequest: 認証リクエストを表すPydanticモデルのドキュメント文字列。

    説明:
        認証処理のためにクライアントから送信されるデータを表します。必須の資格情報と、
        オプションでセッション継続時間や「ログインを記憶する」フラグを含みます。

    属性:
        username (str):
            認証に使用するユーザーの一意識別子（例: ユーザー名やメールアドレス）。
        password (str):
            ユーザーのパスワード。
        max_age (Optional[int]):
            オプション。認証の最大有効期間を秒単位で指定します。デフォルトは 60 * 60 * 24 * 7 = 604800（7日）。
            None を許容する場合は無期限扱いにする等の上位ロジックを適用できます。
        remember_me (Optional[bool]):
            オプション。次回以降のログインを記憶するかどうかを示すフラグ。デフォルトは False。

    検証 (Validators):
        validate_max_age:
            max_age が None でなければ、非負の整数である必要があります。負の値の場合は ValueError を送出します。
        validate_remember_me:
            remember_me が None でなければ、bool 型である必要があります。型が不正な場合は ValueError を送出します。

    使用上の注意:
        - max_age は秒単位で扱うため、分や時間での指定を行う場合は換算が必要です。
        - フロントエンドから受け取る値の型によっては事前にパースや正規化が必要になることがあります。
    """

    username: str = Field(
        description="User's unique identifier for authentication",
    )
    password: str = Field(
        description="User's password for authentication",
    )
    # 60s * 60m * 24h * 7d = 604800s
    max_age: Optional[int] = Field(
        default=60 * 60 * 24 * 7,
        description="OPTIONAL. Maximum Authentication Age in seconds",
    )
    remember_me: Optional[bool] = Field(
        default=False,
        description="OPTIONAL. Whether to remember the user for future logins",
    )

    @field_validator("max_age")
    def validate_max_age(cls, v):
        if v is not None and v < 0:
            raise ValueError("max_age must be a non-negative integer")
        return v

    @field_validator("remember_me")
    def validate_remember_me(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ValueError("remember_me must be a boolean value")
        return v
