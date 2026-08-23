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


class DocumentNotFoundError(AppError):
    pass


class UnsupportedFileTypeError(AppError):
    pass


class FileTooLargeError(AppError):
    pass


class ConversationNotFoundError(AppError):
    pass


class NoTextToIndexError(AppError):
    pass


class QuizNotFoundError(AppError):
    pass