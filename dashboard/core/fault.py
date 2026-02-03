from abc import ABC


class Fault(ABC):
    """
    Abstract class for Fault which groups the common
    properties and behaviours for different types of faults
    """

    def __init__(self, __id: int, __fault_type: str) -> None:
        """
        Initializes a fault

        __id : int
            Unique fault identifier
        __fault_type : str
            Fault category name
        """
        self.__id = __id
        self.__fault_type = __fault_type


    @property
    def get_id(self) -> int:
        """Returns the id for a fault"""
        return self.__id
    

    @property
    def get_fault_type(self) -> str:
        """Returns the type of fault as a string"""
        return self.__fault_type


class Hotspot(Fault):
    """
    Represents a hotspot fault
    """

    def __init__(self, __id: int) -> None:
        super().__init__(__id, "Hotspot")
        self.__image_data = []


    def add_image(self, img):
        """
        Used to add an image into the list of images
        
        Args:
            img: The image being added
        """
        self.__image_data.append(img)


    def get_image_array(self):
        return self.__image_data


class ShortCircuit(Fault):
    """
    Represents a short circuit fault
    """

    def __init__(self, __id: int) -> None:
        super().__init__(__id, "Short Circuit")
        self.__string_data = []   # Store electrical readings


    def add_reading(self, reading: str):
        self.__string_data.append(reading)


    def get_reading_array(self):
        return self.__string_data


class OpenCircuit(Fault):
    """
    Represents an open circuit fault
    """

    def __init__(self, __id: int) -> None:
        super().__init__(__id, "Open Circuit")
        self.__string_data = []


    def add_reading(self, reading: str):
        self.__string_data.append(reading)


    def get_reading_array(self):
        return self.__string_data


class Shadowing(Fault):
    """
    Represents a shadowing fault
    """

    def __init__(self, __id: int) -> None:
        super().__init__(__id, "Shadowing")
        self.__string_data = []
        self.__image_data = []


    def add_reading(self, reading: str):
        self.__string_data.append(reading)


    def add_image(self, img):
        self.__image_data.append(img)


    def get_reading_array(self):
        return self.__string_data


    def get_image_array(self):
        return self.__image_data
