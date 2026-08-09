from src import Database, log, log_function
from src.models.order import Order, OrderItem
from src.utils.exceptions import NotFoundError


class OrderService(Database):

    def __init__(self) -> None:
        super().__init__()
        self.log = log.bind(service="OrderService")

    @log_function
    def get_orders(self, status=None, date=None):
        query = """
            SELECT o.id, o.order_time, o.status, t.table_number
            FROM orders o
            LEFT JOIN tables t ON o.table_id = t.id
        """
        conditions = []
        params = []

        if date:
            conditions.append("o.order_time::date = %s")
            params.append(date)

        if status:
            conditions.append("o.status = %s")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY o.order_time DESC"

        results = self.execute(query, params, fetch="all")

        if not results:
            raise NotFoundError("Orders")

        orders = []
        for order in results:
            table_number = (
                order["table_number"] if order["table_number"] is not None else "N/A"
            )
            orders.append(
                Order(
                    id=order["id"],
                    table_number=table_number,
                    order_time=order["order_time"].strftime("%Y-%m-%d %H:%M"),
                    status=order["status"],
                )
            )

        return orders

    @log_function
    def add_order(self, table_number):

        table_row = self.execute(
            "SELECT id, status FROM tables WHERE table_number = %s",
            (table_number,),
            fetch="one",
        )
        if not table_row:
            return f"❌ Table number '{table_number}' not found. Please check the table number and try again."

        if table_row["status"] == "occupied":
            order = self.execute(
                "SELECT id FROM orders WHERE table_id = %s AND status = 'open'",
                (table_row["id"],),
                fetch="one",
            )
            if order:
                return f"❌ Table number '{table_number}' is currently occupied by order #{order['id']}. Please choose another table."
            return f"❌ Table number '{table_number}' is currently occupied. Please choose another table."

        row = self.execute(
            "INSERT INTO orders (table_id, status) VALUES (%s, 'open') RETURNING id",
            (table_row["id"],),
            fetch="one",
        )
        self.execute(
            "UPDATE tables SET status = 'occupied' WHERE id = %s", (table_row["id"],)
        )
        self.log.success(f"Added new Order#{row["id"]}")

        return row["id"]

    @log_function
    def add_item(self, order_id, item_id, quantity):
        menu_row = self.execute(
            "SELECT name, price FROM menu_items WHERE id = %s", (item_id,), fetch="one"
        )

        if menu_row is None:
            self.log.warning(f"Menu item with ID '{item_id}' not found.")
            return f"❌ Menu item with ID '{item_id}' not found. Please check the item ID and try again."

        status = self.get_order_status(order_id)

        if status != "open":
            self.log.warning(
                f"Cannot add item to order #{order_id} as it is already '{status}'."
            )
            return (
                f"❌ Cannot add item to order #{order_id} as it is already '{status}'."
            )

        row = self.execute(
            """INSERT INTO order_details (order_id, item_id, item_name, quantity, unit_price) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_id, item_id)
            DO UPDATE SET quantity = order_details.quantity + EXCLUDED.quantity
            RETURNING id""",
            (order_id, item_id, menu_row["name"], quantity, menu_row["price"]),
            fetch="one",
        )
        self.log.success(
            f"Add: {menu_row["name"].title()} (X{quantity}) to Order#{order_id}"
        )
        return row["id"]

    @log_function
    def update_item_quantity(self, order_id, item_num, delta):

        row = self._get_order_item_row(order_id, item_num)

        if row is None:
            self.log.warning(
                f"Item number '{item_num}' not found in order #{order_id}."
            )
            return f"❌ Item number '{item_num}' not found in order #{order_id}."

        status = self.get_order_status(order_id)
        if status != "open":
            self.log.warning(
                f"Cannot update item quantity for order #{order_id} as it is already '{status}'."
            )
            return f"❌ Cannot update item quantity for order #{order_id} as it is already '{status}'."

        new_quantity = row["quantity"] + delta

        if new_quantity <= 0:
            self.remove_item(order_id=order_id, item_num=item_num)
            return

        self.execute(
            "UPDATE order_details SET quantity = %s WHERE id = %s",
            (new_quantity, row["id"]),
        )

        self.log.success(
            f"✅ {row["item_name"].capitalize()} quantity updated to {new_quantity} in order #{order_id}."
        )
        return f"✅ {row["item_name"].capitalize()} quantity updated to {new_quantity} in order #{order_id}."

    @log_function
    def get_order_details(self, order_id):

        order_row = self.execute(
            f"""SELECT o.id, o.status, to_char(o.order_time, 'YYYY-MM-DD HH24:MI') AS order_time, t.table_number
                       FROM orders o
                       LEFT JOIN tables t ON o.table_id = t.id
                       WHERE o.id = %s;""",
            (order_id,),
            fetch="one",
        )
        if not order_row:
            self.log.error(f"Order#{order_id} was not found")
            return None

        response = {
            "order": Order(
                id=order_row["id"],
                table_number=order_row["table_number"],
                order_time=order_row["order_time"],
                status=order_row["status"],
            ),
        }

        item_rows = self.execute(
            """SELECT id, order_id, item_id, item_name, quantity, unit_price
                       FROM order_details
                       WHERE order_id = %s
                       ORDER BY id;""",
            (order_id,),
            fetch="all",
        )
        if not item_rows:
            response.update({"items": [], "total": 0.0})
            return response

        items = [
            OrderItem(
                id=row["id"],
                order_id=row["order_id"],
                item_id=row["item_id"],
                item_name=row["item_name"],
                quantity=row["quantity"],
                unit_price=row["unit_price"],
            )
            for row in item_rows
        ]

        total = sum(item.line_total for item in items)
        response.update({"items": items, "total": total})

        return response

    @log_function
    def update_order_status(self, order_id, new_status: str):

        if not self.is_order_exists(order_id):
            self.log.error(f"Order#{order_id} was not found")
            return f"❌ Order with ID #{order_id} was not found."

        if new_status.lower() not in [
            "paid",
            "canceled",
        ]:
            self.log.info(f"Wrong status for Order#{order_id} to update: {new_status}")
            return f""" ‼️ You cannot change the order status of Order ID #{order_id} to '{new_status.capitalize()}'.
                    \r Only 'Paid' or 'Canceled' are allowed."""

        current_status = self.get_order_status(order_id)
        if current_status == new_status.lower():
            self.log.info(
                f"Order #{order_id} is already '{new_status}'. No changes made."
            )
            return f"❌ Order #{order_id} is already '{new_status.capitalize()}'. No changes made."
        self.execute(
            "UPDATE orders SET status=%s WHERE id=%s", (new_status.lower(), order_id)
        )

        table_row = self.execute(
            """SELECT table_number FROM tables
            WHERE id = (SELECT table_id FROM orders WHERE id=%s)""",
            (order_id,),
            fetch="one",
        )

        table_status_changed = False
        if table_row and current_status == "open":
            self.execute(
                "UPDATE tables SET status=%s WHERE table_number=%s",
                ("available", table_row["table_number"]),
            )
            table_status_changed = True

        self.log.success(
            f"""Order #{order_id} new status: {new_status}
            {f"Table #{table_row["table_number"]} new status: available" if table_status_changed else ""}"""
        )
        return f"""✅ Order #{order_id} status updated to '{new_status.capitalize()}'.
                \r {f"🪑 Table #{table_row["table_number"]} is now Available again." if table_status_changed else ""}"""

    @log_function
    def get_order_status(self, order_id):
        row = self.execute(
            "SELECT status FROM orders WHERE id=%s", (order_id,), fetch="one"
        )
        if not row:
            self.log.error(f"Order with ID #{order_id} was not found.")
            return f"❌ Order with ID #{order_id} was not found."
        return row["status"]

    def is_order_exists(self, order_id):
        row = self.execute(
            "SELECT id FROM orders WHERE id=%s", (order_id,), fetch="one"
        )
        return True if row else False

    def remove_item(self, order_id, item_num):
        row = self._get_order_item_row(order_id, item_num)

        if row is None:
            self.log.error(f"Item number '{item_num}' not found in order #{order_id}.")
            return f"❌ Item number '{item_num}' not found in order #{order_id}."

        self.execute("DELETE FROM order_details WHERE id = %s;", (row["id"],))

        self.log.success(
            f"{row["item_name"].capitalize()} removed from order #{order_id}."
        )

        return f"✅ {row["item_name"].capitalize()} removed from order #{order_id}."

    def _get_order_item_row(self, order_id, item_num):
        row = self.execute(
            """SELECT * FROM (
                           SELECT *, ROW_NUMBER() OVER (ORDER BY id) AS item_number
                           FROM order_details
                           WHERE order_id = %s
                       ) sub
                       WHERE item_number = %s;""",
            (order_id, item_num),
            fetch="one",
        )
        if not row:
            return None
        return row
