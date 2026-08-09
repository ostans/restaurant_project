from src import Database, log, log_function
from src.models.menu import MenuItem
from src.utils.exceptions import DuplicateItemError


class MenuService(Database):
    def __init__(self) -> None:
        super().__init__()
        self.log = log.bind(service="MenuService")

    @log_function
    def _fetch_menu_items(self) -> list[MenuItem]:
        results = self.execute(
            "SELECT id, name, price FROM menu_items WHERE is_available = TRUE ORDER BY id ASC ",
            fetch="all",
        )
        if not results:
            return []
        menu_items_list = [
            MenuItem(item_id=row["id"], name=row["name"], price=row["price"])
            for row in results
        ]
        return menu_items_list

    @log_function
    def show_menu(self) -> str:
        menu_items_list = self._fetch_menu_items()
        if not menu_items_list:
            return "The menu is currently empty."
        else:
            menu_str = f""" {"="*30}
            \r {" "*11}📜 MENU  
            \r  {"ID":<4} {"Name":<15} Price
            \r {"="*30}\n"""
            for index, item in enumerate(menu_items_list):
                menu_str += f"  {index + 1:<4} {item.__str__()}\n"

            menu_str += f" {"-"*30}"
            return menu_str

    @log_function
    def add_item(self, name: str, price: str):
        try:
            if not name or not price:
                return "❌ Name and price cannot be empty."

            price = float(price)

            row = self.execute(
                """INSERT INTO menu_items (name, price) VALUES (%s, %s)
                ON CONFLICT (name)
                DO UPDATE SET price = EXCLUDED.price, is_available = TRUE
                RETURNING id, name, price""",
                (name.lower(), price),
                fetch="one",
            )

            self.log.info(f"Adding menu item: {name}, ${price:.2f}")

            return f"✅ Menu item '{name.capitalize()}' added successfully."

        except DuplicateItemError:
            self.log.error(f"Menu item '{name}' already exists.")
            return f"‼️ Menu item '{name}' already exists.\n Cannot add duplicate. if you want to change the price, please use the edit menu."
        except ValueError:
            self.log.error(
                f"Invalid price '{price}' for menu item '{name}'. Must be a number."
            )
            return f"❌ Invalid price '{price}'. Please enter a valid number."

    @log_function
    def edit_item(self, action: str, index: int, name: str = None, price: float = None):
        menu_items_list = self._fetch_menu_items()
        item = menu_items_list[index]
        previous_name = item.name
        if action == "edit_name":
            if not name:
                return "‼️ Name cannot be empty."
            try:
                self.execute(
                    "UPDATE menu_items SET name = %s WHERE id = %s",
                    (name.lower(), item.id),
                )
            except DuplicateItemError:
                self.log.error(f"Menu item '{name}' already exists.")
                return f"‼️ You cannot rename the item '{item.name.title()}' to '{name.title()}'. This item already exists."
            item.name = name
            self.log.info(f"Editing menu item ID {item.id}: changing name to '{name}'")
            return f"✅ Menu item '{previous_name.title()}' updated to '{name}'."
        elif action == "edit_price":
            if not price:
                return "❌ Price cannot be empty."
            try:
                price = float(price)
            except ValueError:
                return f"❌ Invalid price '{price}'. Please enter a valid number."

            self.execute(
                "UPDATE menu_items SET price = %s WHERE id = %s", (price, item.id)
            )
            item.price = price
            self.log.info(
                f"Editing menu item ID {item.id}: changing price to ${price:.2f}"
            )
            return f"Menu item '{item.name.title()}' price updated to ${price:.2f}."
        elif action == "delete_item":
            self.execute(
                "UPDATE menu_items SET is_available = FALSE WHERE id = %s", (item.id,)
            )
            self.log.info(f"Deleting menu item ID {item.id}")
            return f"✅ Menu item '{previous_name.title()}' deleted successfully."
        else:
            self.log.error(f"Invalid action '{action}' for editing menu items.")
            return f"❌ Invalid choice! Please try again."

    def get_length(self):
        return len(self._fetch_menu_items())

    def get_item(self, index: int):
        menu_items_list = self._fetch_menu_items()
        return menu_items_list[index]
