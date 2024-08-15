from pydantic import BaseModel, Field
from typing import List


class UserBase(BaseModel):
    """
    Userの基底クラス
    Args:
        <id> <int>:
                ユーザーID
        <name> <str>:
                ユーザー名
        <display_name> <str>:
                表示名
        <is_bot> <bool>:
                ボットかどうか
    """
    id: int
    name: str = Field(...,
                      min_length=3, max_length=16,
                      pattern=r'^[a-zA-Z0-9_]+$'
                      )
    display_name: str = Field(...,
                              min_length=1, max_length=32,
                              pattern=r'^[a-zA-Z0-9_]+$'
                              )
    is_bot: bool = Field(default=False)


class CreateUser(UserBase):
    """
    Userの作成用クラス
    Args:
        <email> <str>:
                メールアドレス
        <password> <str>:
                パスワード
    """
    email: str = Field(...,
                       min_length=1, max_length=256,
                       pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                       )
    password: str = Field(...,
                          min_length=8, max_length=256,
                          pattern=r'^[a-zA-Z0-9_]+$'
                          )

    class Config:
        orm_mode = True


class User(UserBase):
    """
    Userのスキーマ
    Args:
        <description> <str>:
                ユーザーの説明
    """
    description: str = Field(max_length=1024)

    class Config:
        orm_mode = True


class Me(UserBase):
    """
    Meのスキーマ
    Args:
        <email> <str>:
                メールアドレス
        <email_verified> <bool>:
                メールアドレスが確認済みかどうか
        <is_enable> <bool>:
                アカウントが有効かどうか
        <created_at> <int>:
                作成日時
        <updated_at> <int>:
                更新日時
    """
    email: str = Field(...,
                       min_length=1, max_length=256,
                       pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                       )
    email_verified: bool = Field(default=False)
    is_enable: bool = Field(default=False)
    roles: List[int] = Field(default=[])
