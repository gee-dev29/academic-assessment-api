import sqlite3
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.database import get_connection
from app.exceptions import AuthenticationRequiredError, InvalidCredentialsError
from app.repositories.users import verify_user_credentials

basic_auth = HTTPBasic(auto_error=False)


def require_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
    connection: Annotated[sqlite3.Connection, Depends(get_connection)],
) -> str:
    if credentials is None:
        raise AuthenticationRequiredError(
            headers={"WWW-Authenticate": "Basic"}
        )

    if not verify_user_credentials(
        connection, credentials.username, credentials.password
    ):
        raise InvalidCredentialsError(headers={"WWW-Authenticate": "Basic"})

    return credentials.username
