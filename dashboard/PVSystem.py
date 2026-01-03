class PVSystem:
    def __init__(self, __id: int, system_type: str, no_of_modules: int, modules: list):
        self.__ID = __id
        self.__type = system_type
        self.__no_of_Modules = no_of_modules
        self.__modules = modules

    def get_modules(self):
        return self.__modules

    def view_module_layout(self):
        print("PV Module layout:")  # Temporary for now, need to make it visual
        for i, module in enumerate(self.__modules, start=1):
            print(f"{i}. {module}")
