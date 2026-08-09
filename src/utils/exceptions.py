class AppError(Exception):

    pass


class DatabaseConnectionError(AppError):

    def __init__(self):
        super().__init__(f"Failed to connect to the database")


class DuplicateItemError(AppError):

    def __init__(self):
        super().__init__(f"Item already exists.")


class InvalidSelection(AppError):

    def __init__(self, len_list: int):
        self.len_list = len_list
        super().__init__(f"The selection must be between 1 - {len_list}.")


class NotFoundError(AppError):

    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__(f"{item_name} not found.")


class InvalidDateFormatError(AppError):

    def __init__(self):
        super().__init__(f"Invalid date format. Please use YYYY-MM-DD.")
