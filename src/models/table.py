class Table:
    def __init__(self, table_id: int, table_number: int, status: str) -> None:
        self.id = table_id
        self.table_number = table_number
        self.status = status

    def __str__(self) -> str:
        return f"{"":>3}{self.table_number:<12} {self.status.capitalize()}"
