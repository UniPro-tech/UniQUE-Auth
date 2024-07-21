
class Permissions:
    USER_CREATE = 1 << 0
    USER_DELETE = 1 << 1
    ROLE_MANAGE = 1 << 2
    FLUG_MANAGE = 1 << 3
    USER_MANAGE = 1 << 4
    INVITE = 1 << 5
    APP_MANAGE = 1 << 6
    APP_DEVELOP = 1 << 7
    SYSTEM = 1 << 8


# 権限をbit変換する関数
def generate_permissionbit(*args):
    mask = 0
    for perm in args:
        mask |= getattr(Permissions, perm, 0)
    return mask


# 権限をbitから解析する関数
def parse_permissionsbit(mask):
    permissions = []
    for perm in dir(Permissions):
        if not perm.startswith('__') and getattr(Permissions, perm) & mask:
            permissions.append(perm)
    return permissions
