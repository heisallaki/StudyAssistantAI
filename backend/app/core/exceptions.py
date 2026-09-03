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


class QuizNotReadyForAttemptError(AppError):
    pass


class QuizAttemptNotFoundError(AppError):
    pass


class QuizAttemptAlreadyCompletedError(AppError):
    pass


class QuizAttemptQuestionNotFoundError(AppError):
    pass


class FlashcardDeckNotFoundError(AppError):
    pass


class FlashcardNotFoundError(AppError):
    pass


class FlashcardGenerationFailedError(AppError):
    pass


class StudyGoalNotFoundError(AppError):
    pass


class StudySessionNotFoundError(AppError):
    pass


class DeadlineNotFoundError(AppError):
    pass


class PlannerRecommendationFailedError(AppError):
    pass