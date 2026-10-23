from fastapi import HTTPException, status


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidRequestError(APIException):
    def __init__(self, detail: str) -> None:
        super().__init__(422, detail)


class AuthenticationRequiredError(APIException):
    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            "Basic authentication is required",
            headers,
        )


class InvalidCredentialsError(APIException):
    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            headers,
        )


class SubjectNotFoundError(APIException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, "Subject not found")


class AssessmentNotFoundError(APIException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, "Assessment not found")


class ScoreNotFoundError(APIException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, "Score not found")


class StudentResultsNotFoundError(APIException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            "No results found for this student",
        )


class DuplicateSubjectError(APIException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            "A subject with this name already exists",
        )


class DuplicateAssessmentError(APIException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            "An assessment with this name already exists for the subject",
        )


class DuplicateScoreError(APIException):
    def __init__(self) -> None:
        super().__init__(
            status.HTTP_409_CONFLICT,
            "A score for this student and assessment already exists",
        )


class ScoreExceedsMaximumError(APIException):
    def __init__(self, max_score: float) -> None:
        super().__init__(
            422,
            f"Score cannot be greater than the maximum of {max_score}",
        )
