class PVSystem:
    """
    Represents the solar PV system
    """

    def __init__(self, __id: int, system_type: str, no_of_modules: int, modules: list):
        self.__ID = __id
        self.__type = system_type
        self.__no_of_Modules = no_of_modules
        self.__modules = modules

    @property
    def get_id(self) -> int:
        """
        Returns
            The ID of the PV system
        """
        return self.__ID

    @property
    def get_system_type(self) -> str:
        """
        Returns
            The system types
        """
        return self.__type

    @property
    def get_no_of_modules(self) -> int:
        """
        Returns
            The number of modules in the system
        """
        return self.__no_of_Modules

    @property
    def get_modules(self) -> int:
        """
        Returns
            The number of modules in the system
        """
        return self.__modules

    def view_module_layout(self):
        print("PV Module layout:")
        for i, module in enumerate(self.__modules, start=1):
            print(f"{i}. {module}")
