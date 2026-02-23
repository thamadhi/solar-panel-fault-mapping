class User:
    """
    User class to represent a user in the solar PV system.
    """
    def __init__(self, id: int, type: str, username: str, email: str):
        self.__id = id
        self.__type = type
        self.__username = username
        self.__email = email

    @property
    def id(self) -> int:
        return self.__id

    @property
    def type(self) -> str:
        return self.__type

    @property
    def username(self) -> str:
        return self.__username

    @property
    def email(self) -> str:
        return self.__email

    def view_profile(self) -> dict:
        return {
            "ID": self.__id,
            "Username": self.__username,
            "Email": self.__email,
            "Type": self.__type
        }

    def view_dashboard(self) -> str:
        return f"Welcome to the {self.__type} Dashboard!"