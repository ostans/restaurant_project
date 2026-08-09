import os
import subprocess
from time import sleep
from datetime import date as date_type
from src import MenuService, TableService, OrderService, ReportService
from src.utils.exceptions import InvalidSelection, InvalidDateFormatError, NotFoundError


class RestaurantManagerCLI:
    """CLI interface for Restaurant Manager application"""

    def __init__(self) -> None:
        self.menu_service = MenuService()
        self.table_service = TableService()
        self.order_service = OrderService()
        self.report_service = ReportService()

    @staticmethod
    def clear():
        subprocess.run("cls" if os.name == "nt" else "clear")

    @staticmethod
    def get_user_input(options: list[str], dash: int = 30) -> str:
        for index, option in enumerate(options):
            print(f" {index + 1}. {option}")
        print(f" {"-"*dash}")
        return input(" Please select an option: ").strip()

    def show_main_menu(self):
        self.clear()

        print(f""" {"="*43}
        \r {" "*6}🍽️  Restaurant Management System
        \r {"="*43}
        \r  1. Show Menu
        \r  2. Show Table Status
        \r  3. Add New Order
        \r  4. Update Open Order Status
        \r  5. View Order Details & Total Price
        \r  6. Show Daily Sales Report
        \r  7. Manage Tables
        \r  8. Exit
        \r {"-"*43}""")

    # ----------------------------------------------------- Restaurant menu management ----------------------------------------------------- #

    def restaurant_menu(self):
        while True:
            self.clear()
            print(self.menu_service.show_menu())
            choice = input(f"""\r 1. Add new item
              \r 2. Edit items
              \r 3. Back to main menu
              \r {"-"*30}
              \r Please select an option (1-3): """)
            match choice:
                case "1":
                    self.add_new_item()
                case "2":
                    self.edit_items()
                case "3":
                    return
                case _:
                    print("\n❌ Invalid choice! Please try again.")
                    sleep(2)

    def add_new_item(self):
        while True:
            self.clear()
            print(f""" {"="*30}
                  \r {" "*8}➕ Add New Item
                  \r {"="*30}
                  \r  ❕Type "cancel" to cancel.❕
                  \r {"*"*30}""")
            name = input("  Name: ").strip()
            if name.lower() == "cancel":
                return
            price = input("  Price: ").strip()
            message = self.menu_service.add_item(name=name, price=price)
            print(f" {"-"*30}\n\n {message}")
            user_input = input(
                "\n If you want to add another item, press Enter.\n To return to the menu, type 'b': "
            )
            if user_input.lower() == "b":
                return

    def edit_items(self):
        while True:
            self.clear()
            print(self.menu_service.show_menu())
            user_input = input("\n Enetr Item ID number to edit or 'c' to cancel: ")
            if user_input.lower() == "c":
                return
            menu_length = self.menu_service.get_length()
            try:
                selected_item = int(user_input)
                if selected_item < 1 or selected_item > menu_length:
                    raise InvalidSelection(menu_length)
            except (ValueError, InvalidSelection):
                print(f"\n‼️ The selection must be a number between 1 - {menu_length}.")
                sleep(3)
                continue
            choice = input("""\n What do you want to do? 
                            \r  1. Change the name
                            \r  2. Change the price
                            \r  3. Delete Item from Menu
                            \r  4. Cancel
                            \r\n Enter your choice(1-3): """)
            match choice:
                case "1":
                    action = "edit_name"
                    new_name = input("\n Enter the new item name: ").strip()
                    new_price = None
                case "2":
                    action = "edit_price"
                    new_price = input("\n Enter the new item price: ").strip()
                    new_name = None
                case "3":
                    action = "delete_item"
                    new_name, new_price = None, None
                case "4":
                    continue
                case _:
                    new_name, new_price = None, None
                    action = "Invalid"

            message = self.menu_service.edit_item(
                action=action, index=selected_item - 1, name=new_name, price=new_price
            )

            print(f"\n{message}")
            sleep(4)

    # ----------------------------------------------------- Restaurant table management ----------------------------------------------------- #

    def mange_tables(self):
        while True:
            self.clear()
            choice = input(f""" {"="*35}
                \r {" "*8}🪑 Table Management
                \r {"="*35}
                \r  1. Add a new table
                \r  2. Remove a table
                \r  3. Back to main menu
                \r {"-"*35}
                \r Enter your choice: """)
            match choice:
                case "1":
                    self.add_table()
                case "2":
                    self.remove_table()
                case "3":
                    return
                case _:
                    print("\n❌ Invalid choice! Please try again.")
                    sleep(2)

    def show_table_list(self, header: bool = True, status: str = "all"):
        header_str = f""" {"="*27}
              \r {" "*8}🪑 Tables
              \r {"="*27}\n"""
        table_list = f"""  {"Numeber":<16} Status
              \r {"-"*27}
              \r{self.table_service.get_table_list(status)}"""
        if header:
            self.clear()
            print(header_str + table_list + f"\r { "-"*27}")
            input("\n Press Enter to Back ...")
        return table_list

    def add_table(self):
        while True:
            self.clear()
            print(f""" {"="*67}
                   \r {" "*25}➕ Add New Table
                   \r {"="*67}
                   \r ⚠️  This is the list of your tables. Do not add duplicate numbers ⚠️
                   \r {"*"*67}
                   \r{self.show_table_list(header=False)} {"-"*27}""")
            table_number = input(
                " Enter the new table number or 'c' to cancel: "
            ).strip()
            if table_number.lower() == "c":
                return
            message = self.table_service.add_table(table_number=table_number)
            print(f"\n{message}")
            user_input = input(
                "\n If you want to add another table, press Enter.\n To return, type 'b':"
            )
            if user_input.lower() == "b":
                return

    def remove_table(self):
        while True:
            self.clear()
            print(f""" {"="*51}
                    \r {" "*19}🪚 Remove Table
                    \r {"="*51}
                    \r  ⚠️  You cannot remove a table that is occupied. ⚠️
                    \r {"*"*51}
                    \r{self.show_table_list(header=False)} {"-"*27}""")
            table_number = input(
                " Ente table number you want to remove or 'c' to cancel: "
            )
            if table_number.lower() == "c":
                return
            message = self.table_service.remove_table(table_number)
            print(f"\n {message}")
            sleep(3)

    # ----------------------------------------------------- Restaurant orders management ----------------------------------------------------- #

    def add_new_order(self):
        header = f""" {"="*30}
                \r {" "*7}🧾 Add New Order
                \r {"="*30}\n"""

        available_tables = f"""
                \r 🟤 Available Tables 🟤\n
                \r {"-"*27}
                \r{self.show_table_list(header=False, status="available")} {"-"*27}"""

        menu_items = f"{self.menu_service.show_menu()}"

        while True:
            self.clear()
            print(header + available_tables)
            if "❌ No table 'available'" in available_tables:
                print(
                    f"""\n❕There is no table 'available'. Please add a new table first 
                      \r or change the status of orders to 'paid' or 'canceled' to free up tables."""
                )
                print(f"\n Returning to main menu in 5 seconds...")
                sleep(5)
                return
            table_number = input(
                "\n Enter table number or type 'c' to cancel: "
            ).strip()
            if table_number.lower() == "c":
                return

            order_id = self.order_service.add_order(table_number)

            if isinstance(order_id, str) and order_id.startswith("❌"):
                print(f"\n {order_id}")
                sleep(3)
                continue
            self.add_item_to_order(order_id)
            self.show_order_details(order_id)
            user_input = input(
                f" Press Enter to add another order or type 'b' to back: "
            ).strip()
            if user_input.lower() == "b":
                return

    def add_item_to_order(self, order_id):
        header = f""" {"="*37}
                \r {" "*7}🧾 Add Items to Order#{order_id}
                \r {"="*37}\n"""
        while True:
            self.clear()
            print(header)
            print(self.menu_service.show_menu())
            item = input("\n Enter item ID to add (or 0 to finish): ").strip()

            if item.lower() == "0":
                return

            menu_length = self.menu_service.get_length()
            try:
                selected_item = int(item)
                if selected_item < 1 or selected_item > menu_length:
                    raise InvalidSelection(menu_length)
            except (ValueError, InvalidSelection):
                print(
                    f"\n ‼️ The selection must be a number between 1 - {menu_length}."
                )
                sleep(3)
                continue

            item = self.menu_service.get_item(selected_item - 1)
            while True:
                try:
                    quantity = input(
                        f"\n Enter quantity for {item.name.title()} (to cancel type 'c'): "
                    ).strip()
                    if quantity.lower() == "c":
                        return
                    quantity = int(quantity)
                    if quantity <= 0:
                        raise ValueError
                except ValueError:
                    print(
                        "\n ‼️ Quantity must be a valid number and greater than zero."
                    )
                    continue
                break

            self.order_service.add_item(order_id, item.id, quantity)
            input(
                f"\n ✅ Add: {item.name.title()} (X{quantity}) \n\n Press Enter to continue ..."
            )

    def edit_order(self, order_id):
        while True:
            status = self.show_order_details(order_id)
            if not status:
                input("\n Press Enter to return to the list of orders ...")
                return
            options = ["Update status", "Back to list of orders"]
            if status == "open":
                options.insert(1, "Edit order items")
            choice = self.get_user_input(options)
            if choice == "1":
                self.update_order_status(order_id)
                continue
            elif choice == "2" and len(options) == 3:
                if status == "open":
                    self.edit_order_items(order_id)
                    continue
            elif (choice == "2" and len(options) == 2) or choice == "3":
                return

    def edit_order_items(self, order_id):
        while True:
            status = self.show_order_details(order_id)
            if not status:
                input("\n Press Enter to back...")
                return

            options = [
                "Add new item",
                "Remove item",
                "Edit item quantity",
                "Back",
            ]
            choice = self.get_user_input(options)

            match choice:
                case "1":
                    self.add_item_to_order(order_id)
                case "2":
                    item_num = input(" Enter item number to remove: ").strip()
                    message = self.order_service.remove_item(
                        order_id=order_id, item_num=item_num
                    )
                    print(f"\n {message}")
                    sleep(2)
                case "3":
                    item_num = input(" Enter item number to edit quantity: ").strip()
                    delta = input(
                        " Enter quantity change (e.g., +2 to add, -1 to remove): "
                    ).strip()
                    try:
                        delta = int(delta)
                    except ValueError:
                        print(
                            "\n ‼️ Invalid quantity change. Please enter a valid number."
                        )
                        sleep(2)
                        continue
                    message = self.order_service.update_item_quantity(
                        order_id=order_id, item_num=item_num, delta=delta
                    )
                    print(f"\n {message}")
                    sleep(2)
                case "4":
                    return
                case _:
                    print("\n❌ Invalid choice! Please try again.")
                    sleep(2)

    def show_orders(self, date=date_type.today()):
        header = f""" {"="*53}
                \r {" "*13}📖 List Of Orders {"for today" if date == date_type.today() else date }
                \r {"="*53}
                """
        while True:
            self.clear()
            print(header)

            orders = []
            try:
                orders = self.order_service.get_orders(date=date)
            except NotFoundError:
                print(" ❌ No orders found for the specified date.")

            except InvalidDateFormatError:
                print(" ❌ Invalid date format. Please use YYYY-MM-DD.")

            if orders:
                for order in orders:
                    print(f" 📄Order #{order.id} ({order.status}) ")
            print(f"\n {"-"*53}")

            options = [
                "Orders of specific date",
                "See details of specific order by ID",
                "Back to main menu",
            ]
            choice = self.get_user_input(options=options, dash=53)
            match choice:
                case "1":
                    date = input(
                        "\n Enter date (YYYY-MM-DD) or press Enter for today: "
                    ).strip()
                    self.show_orders(date=date)
                case "2":
                    order_id = input(f" Enter Order ID to see details: ").strip()
                    self.edit_order(order_id)
                    continue
                case "3":
                    return
                case _:
                    print("\n❌ Invalid choice! Please try again.")
                    sleep(2)
                    continue

            return

    def show_order_details(self, order_id):
        self.clear()
        try:
            order_id = int(order_id)
        except ValueError:
            print(f"\n\n ❌ Invalid Order ID. Please enter a valid number.")
            return

        print(f""" {"="*51}
                    \r {" "*19}🧾 Order #{order_id}
                    \r {"="*51}
                    \r  {"Num":<4} {"Item":<11} {"Quantity":<13} {"Price":<10} Total
                    \r {"-"*51}\n""")

        order_details = self.order_service.get_order_details(order_id)

        message = ""
        if order_details is None:
            message = f"\n\n\r {" "*14} ❌ Order #{order_id} Not Found\n\n\n"
            total, status, table_number, order_time = 0.0, None, "❌", "❌"
        else:
            total, status, table_number, order_time = (
                order_details["total"],
                order_details["order"].status,
                order_details["order"].table_number,
                order_details["order"].order_time,
            )

        if order_details and not order_details["items"]:
            message = f"\n\n\r {" "*19}❕ Not Found\n\n\n"
        elif order_details:
            for index, item in enumerate(order_details["items"]):
                message += f"   {index+1:<2} {item.item_name.title():<15} {item.quantity:<10} {item.unit_price:<10.2f} {item.line_total:.2f}\n"

        message += f"\n {"-"*51}\n\n"

        message += f""" Total: {total}
            \r Status: {status.capitalize() if status else "❌"}
            \r Table: {table_number}
            \r Order Time: {order_time}\n
            \r {"-"*51}
            """
        print(message)
        return status

    def show_open_orders(self):
        header = f""" {"="*53}
                \r {" "*12}📑 Open Orders
                \r {"="*53}"""
        while True:
            self.clear()
            print(header)
            orders = []
            try:
                orders = self.order_service.get_orders(status="open")
            except NotFoundError:
                print(" ❌ No open orders found.")
                input("\n Press Enter to go back...")
                return

            for order in orders:
                print(
                    f" 📄Order #{f"{order.id}":<7} Table: {f"{order.table_number}":<7} {order.order_time} "
                )
            print(f"\n {"-"*53}")

            order_id = input(
                " Enter Order ID to Update Status (or 'b' to go back): "
            ).strip()

            if order_id.lower() == "b":
                return

            self.update_order_status(order_id)

    def update_order_status(self, order_id=None):
        status = self.show_order_details(order_id)
        if not status:
            input("\n Press Enter to return to the list of orders ...")
            return
        print(""" ⚠️  Warnings:
            \r      1. You cannot change the "status" of a 'canceled' or 'paid' order to 'open'.
            \r      2. If you change the "status" of an order from 'canceled' to 'paid' 
            \r         or from 'paid' to 'canceled',
            \r         it will affect the daily sales report.
            """)
        print(f" Select new status for Order #{order_id}: ")
        options = ["Paid", "Canceled", "Cancel to update status"]
        choice = self.get_user_input(options)
        match choice:
            case "1":
                new_status = "paid"
            case "2":
                new_status = "canceled"
            case "3":
                return
            case _:
                print("\n❌ Invalid choice!")
                sleep(3)
                return
        message = self.order_service.update_order_status(order_id, new_status)
        print(f"\n {message}")
        sleep(3)
        return

    # ----------------------------------------------------- Restaurant reports management ----------------------------------------------------- #

    def show_daily_sales_report(self, start_date=None, end_date=None):
        while True:
            self.clear()
            print(f""" {"="*53}
                \r {" "*16}📊 Daily Sales Report
                \r {"="*53}
                """)

            daily_sales_report = None
            try:
                daily_sales_report = self.report_service.daily_sales_report(
                    start_date, end_date
                )
            except InvalidDateFormatError:
                print("\n\n ❌ Invalid date format. Please use YYYY-MM-DD.\n\n")
            except ValueError as e:
                print(f"\n\n {e}\n\n")

            if daily_sales_report:
                print(f""" Date: {daily_sales_report["date"]}\n
                    \r Total Orders: {daily_sales_report["total_orders"]}
                    \r Paid Orders: {daily_sales_report["paid_orders"]}
                    \r Canceled Orders: {daily_sales_report["canceled_orders"]}\n
                    \r Total Sales: ${daily_sales_report["total_sales"]:.2f}
                    """)

            print(f" {"-"*53}")
            options = ["Enter a date", "Enter a date range", "Back to main menu"]
            choice = self.get_user_input(options, dash=53)
            match choice:
                case "1":
                    date_input = input(
                        " Enter date (YYYY-MM-DD) for the report or press Enter for today: "
                    ).strip()
                    self.show_daily_sales_report(date_input)
                    return
                case "2":
                    start_date_input = input(" Enter start date (YYYY-MM-DD): ").strip()
                    end_date_input = input(" Enter end date (YYYY-MM-DD): ").strip()
                    self.show_daily_sales_report(start_date_input, end_date_input)
                    return
                case _:
                    return

    def run(self):
        while True:
            self.show_main_menu()
            choice = input(" Please select an option (1-8): ").strip()
            match choice:
                case "1":
                    self.restaurant_menu()
                case "2":
                    self.show_table_list()
                case "3":
                    self.add_new_order()
                case "4":
                    self.show_open_orders()
                case "5":
                    self.show_orders()
                case "6":
                    self.show_daily_sales_report()
                case "7":
                    self.mange_tables()
                case "8":
                    print("\n \t Goodbye ! \n")
                    break
                case _:
                    print("\n❌ Invalid choice! Please try again.")
                    sleep(2)
