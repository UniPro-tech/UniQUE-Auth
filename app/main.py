from fastapi import FastAPI
from app.routers import apps, flags, users, token, roles
from app.routers.apps import (
    users as apps_users,
    list as apps_list
    )
from app.routers.flags import (
    users as flags_users,
    list as flags_list,
    roles as flags_roles
    )
from app.routers.roles import (
    list as roles_list
    )
from app.routers.token import code
from app.routers.users import (
    me as users_me,
    invite as users_invite,
    list as users_list,
    flags as users_flags,
    link_apps as users_link_apps
)
from app.database import engine, Base


# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    root_path="/api/v1"
)

# apps配下
app.include_router(apps.router)
app.include_router(apps_list.router)
app.include_router(apps_users.router)

app.include_router(flags.router)
app.include_router(flags_users.router)
app.include_router(flags_list.router)
app.include_router(flags_roles.router)

app.include_router(roles.router)
app.include_router(roles_list.router)

app.include_router(token.router)
app.include_router(code.router)

app.include_router(users.router)
app.include_router(users_me.router)
app.include_router(users_invite.router)
app.include_router(users_list.router)
app.include_router(users_flags.router)
app.include_router(users_link_apps.router)
