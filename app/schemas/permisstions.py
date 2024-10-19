from typing import List


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
    LOG_READ = 1 << 9


class RolePermission():
    def __init__(self, permission_bit=None, permisstions=None) -> None:
        self.parmission_bit: int = permission_bit
        self.permissions: List[Permissions] = permisstions
        if permission_bit:
            self.permissions = self.parse_permissionsbit()
        elif permisstions:
            self.parmission_bit = self.generate_permissionbit()

    # 権限をbit変換する関数
    def generate_permissionbit(self):
        mask = 0
        for perm in self.permissions:
            mask |= getattr(Permissions, perm, 0)
        return mask

    # 権限をbitから解析する関数
    def parse_permissionsbit(self):
        self.permissions = []
        for perm in dir(Permissions):
            if (
                not perm.startswith('__')
                and getattr(Permissions, perm)
                & self.parmission_bit
            ):
                self.permissions.append(perm)
        return self.permissions
