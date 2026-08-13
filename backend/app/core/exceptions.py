class AppError(Exception):
    pass


class EmailAlreadyRegisteredError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class InactiveUserError(AppError):
    pass