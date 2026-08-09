class MenuItem:
    def __init__(self, item_id: int, name: str, price: float) -> None:
        self.id = item_id
        self.name = name
        self.price = price

    def __str__(self) -> str:
        return f"{self.name.title():<15} ${self.price:.2f}"
