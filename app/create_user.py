import getpass
import sqlite3

from app import database
from app.repositories.users import create_user


def main() -> None:
    database.create_tables()
    username = input("Username: ")
    password = getpass.getpass("Password (at least 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    connection = sqlite3.connect(database.DATABASE_PATH)
    try:
        create_user(connection, username, password)
    except sqlite3.IntegrityError as error:
        raise SystemExit(f"Username {username.strip()!r} already exists") from error
    except ValueError as error:
        raise SystemExit(str(error)) from error
    finally:
        connection.close()

    print(f"User {username.strip()!r} created.")


if __name__ == "__main__":
    main()
