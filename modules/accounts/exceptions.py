
# SessionRevokedError
# AuthKeyUnregisteredError
# AuthKeyNotFound

# TDesktopUnauthorized - unlogin
class AccountBannedException(Exception):
    def __init__(self, reason):
        self.reason = reason
