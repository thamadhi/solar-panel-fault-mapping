class User:
    """
    User class to represent a user in the solar PV system.
    """
    def __init(self, id: int, type: str, username: str, email: str, password: str):
        self.__id = id
        self.__type = type
        self.__username = username
        self.__email = email
        self.__password = password

    def login(self, username: str, password: str) -> bool:
        pass

    def view_profile(self):
        pass

    def view_dashboard(self):
        pass