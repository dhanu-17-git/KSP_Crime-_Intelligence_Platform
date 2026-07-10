class AppError(Exception):
    status_code = 500
    error_code = "APP_ERROR"

    def __init__(self, message: str = "Application error") -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(AppError):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(AppError):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    error_code = "CONFLICT"


class DatabaseOperationError(AppError):
    status_code = 500
    error_code = "DATABASE_ERROR"
