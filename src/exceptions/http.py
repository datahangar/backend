from fastapi import HTTPException, status


def new_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def new_conflict_exception(msg: str = "Conflict with existing data") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=msg,
    )


def new_user_not_found_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
