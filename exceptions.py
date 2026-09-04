class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthError(Exception):
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)
