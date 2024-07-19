from fastapi import FastAPI
from .routers import apps, flugs, users, token, roles
from .routers.apps import (
    users as apps_users,
    list as apps_list
    )
from .routers.flugs import (
    users as flugs_users,
    list as flugs_list,
    roles as flugs_roles
    )
from .routers.roles import (
    list as roles_list
    )
from .routers.token import code
from .routers.users import (
    me as users_me,
    invite as users_invite,
    list as users_list,
    flugs as users_flugs,
    link_apps as users_link_apps
)
from .database import engine, Base


# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# apps配下
app.include_router(apps.router)
app.include_router(apps_list.router)
app.include_router(apps_users.router)

app.include_router(flugs.router)
app.include_router(flugs_users.router)
app.include_router(flugs_list.router)
app.include_router(flugs_roles.router)

app.include_router(roles.router)
app.include_router(roles_list.router)

app.include_router(token.router)
app.include_router(code.router)

app.include_router(users.router)
app.include_router(users_me.router)
app.include_router(users_invite.router)
app.include_router(users_list.router)
app.include_router(users_flugs.router)
app.include_router(users_link_apps.router)
