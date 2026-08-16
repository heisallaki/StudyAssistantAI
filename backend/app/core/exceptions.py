class AppError(Exception):
    pass


class EmailAlreadyRegisteredError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class InactiveUserError(AppError):
    pass


class SubjectNotFoundError(AppError):
    pass


class TopicNotFoundError(AppError):
    pass