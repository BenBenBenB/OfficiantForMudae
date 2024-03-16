class MessageBoxNotFoundException(Exception):
    pass


class InvalidTimersUpMessageException(Exception):
    pass


class InvalidTimersUp(Exception):
    def __init__(self, expected_username: str, received_username: str) -> None:
        message = f"Problem getting TU for user. Expected '{expected_username}' but received '{received_username}'"
        super().__init__(message)
