class Module:
    def __init__(self, module_id: int):
        self.__module_id = module_id

    def __repr__(self):
        return f"Module-{self.__module_id}"


class String:
    def __init__(self, string_id: int, num_modules: int):
        self.__string_id = string_id
        self.__modules = [Module(i+1) for i in range(num_modules)]

    def __repr__(self):
        return f"String-{self.__string_id}"
    
    @property
    def get_modules(self) -> list:
        return self.__modules


class PVSystem:
    """
    Represents the solar PV system
    """

    def __init__(self, system_id: int, system_type: str, num_strings: int, modules_per_string: int):
        self.__id = system_id
        self.__system_type = system_type

        self.__strings = [
            String(i+1, modules_per_string)
            for i in range(num_strings)
        ]

    @property
    def get_id(self) -> int:
        """
        Returns
            The ID of the PV system
        """
        return self.__id

    @property
    def get_system_type(self) -> str:
        """
        Returns
            The system types
        """
        return self.__system_type

    @property
    def get_strings(self) -> list:
        return self.__strings

    def view_layout(self):
        """
        Display PV system layout
        """

        print(f"PV System {self.__id} ({self.__system_type})")

        for string in self.__strings:
            print(string)

            for module in string.get_modules:
                print(f"   {module}")
