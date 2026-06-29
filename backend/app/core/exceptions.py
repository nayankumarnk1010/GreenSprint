class GreenSprintException(Exception):
    """
    Base application exception.
    """
    pass


class UserAlreadyExistsException(
    GreenSprintException
):
    """
    Raised when email already exists.
    """
    pass


class InvalidCredentialsException(
    GreenSprintException
):
    """
    Raised when login credentials are invalid.
    """
    pass


class UserNotFoundException(
    GreenSprintException
):
    """
    Raised when a user cannot be found.
    """
    pass