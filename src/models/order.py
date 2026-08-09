class Order:
    def __init__(self, id, table_number, order_time, status):
        self.id = id
        self.table_number = table_number
        self.order_time = order_time
        self.status = status

    def __str__(self):
        return f"Order ID: {self.id}, Table Number: {self.table_number}, Order Time: {self.order_time}, Status: {self.status}"


class OrderItem:
    def __init__(self, id, order_id, item_id, item_name, quantity, unit_price):
        self.id = id
        self.order_id = order_id
        self.item_id = item_id
        self.item_name = item_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.line_total: float = quantity * unit_price

    def __str__(self):
        return f"Order ID: {self.order_id}, Item ID: {self.item_id}, Item Name: {self.item_name}, Quantity: {self.quantity}, Unit Price: {self.unit_price}"
