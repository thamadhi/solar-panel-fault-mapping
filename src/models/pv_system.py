class Module:
    """
    Represents a PV Module whichs is part of a PVString.
    """

    def __init__(self, module_id: int):
        self.__module_id = module_id

    def __repr__(self):
        return f"Module-{self.__module_id}"


class PVString:
    """
    Represents a PV string within the system.
    """

    def __init__(self, string_id: int, num_modules: int):
        self.__string_id = string_id
        self.__modules = [Module(i + 1) for i in range(num_modules)]

    def __repr__(self):
        return f"String-{self.__string_id}"

    @property
    def get_modules(self) -> list:
        return self.__modules

    @property
    def get_id(self) -> int:
        return self.__string_id


class PVSystem:
    """
    Represents the solar PV system.
    """

    def __init__(self, system_id: int, system_type: str, modules_per_string: int):
        self.__id = system_id
        self.__system_type = system_type

        self.__strings = [
            PVString(1, modules_per_string),
            PVString(2, modules_per_string),
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

    @property
    def get_modules_per_string(self) -> int:
        return len(self.__strings[0].get_modules)

    @property
    def get_num_strings(self) -> int:
        return 2

    def view_layout(self):
        """
        Display PV system layout
        """

        print(f"PV System {self.__id} ({self.__system_type})")

        for string in self.__strings:
            print(string)
            for module in string.get_modules:
                print(f"   {module}")
