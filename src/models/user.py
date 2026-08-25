from src.views.dashboard_view import Dashboard


class User:
    """
    Domain entity representing a system user in the OpenSunray platform.

    This class encapsulates user-related attributes and provides
    controlled read-only access via property decorators.
    """

    def __init__(self, id: int, type: str, username: str, email: str):
        self.__id = id
        self.__type = type
        self.__username = username
        self.__email = email

    @property
    def id(self) -> int:
        """
        Returns:
            int: Unique user identifier.
        """
        return self.__id

    @property
    def type(self) -> str:
        """
        Returns:
            str: User role within the system.
        """
        return self.__type

    @property
    def username(self) -> str:
        """
        Returns:
            str: Username of the user.
        """
        return self.__username

    @property
    def email(self) -> str:
        """
        Returns:
            str: Email address of the user.
        """
        return self.__email
