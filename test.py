from app.cruds.token import create_access_token
from app.schemas import AccessToken

accesstoken_data = AccessToken(
    sub=100,
    for_=100,
    scope=['test']
)

print(create_access_token(
    db=None,
    token=accesstoken_data
))
