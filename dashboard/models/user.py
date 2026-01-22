class User:
    """
    User class to represent a user in the solar PV system.
    """
    def __init__(self, id: int, type: str, username: str, email: str, password: str):
        self.__id = id
        self.__type = type
        self.__username = username
        self.__email = email
        self.__password = password

    def login(self, username: str, password: str) -> bool:
        if self.__username == username and self.__password == password:
            return True
        else:
            return False

    def view_profile(self) -> dict:
        return {
            "Username": self.__username,
            "Email": self.__email,
            "Type": self.__type
        }

    def view_dashboard(self) -> str:
        return f"Welcome to the {self.__type} Dashboard!"
