from src import Database, log, log_function
from src.models.table import Table
from src.utils.exceptions import DuplicateItemError


class TableService(Database):
    def __init__(self) -> None:
        super().__init__()
        self.log = log.bind(service="TableService")

    @log_function
    def _fetch_table_list(self) -> list[Table]:
        results = self.execute(
            "SELECT id, table_number, status FROM tables ORDER BY table_number ASC ",
            fetch="all",
        )
        if not results:
            return []
        table_list = [
            Table(
                table_id=row["id"],
                table_number=row["table_number"],
                status=row["status"],
            )
            for row in results
        ]
        return table_list

    @log_function
    def add_table(self, table_number: int):
        try:
            table_number = int(table_number)
            row = self.execute(
                "INSERT INTO tables (table_number) VALUES (%s) RETURNING id, table_number, status",
                (table_number,),
                fetch="one",
            )
            return f"✅ Table number '{table_number}'Added Successfully."
        except DuplicateItemError:
            self.log.error(
                f"There is a table with number {table_number}. Cannot add duplicate."
            )
            return f"‼️ There is a table with number '{table_number}'. Cannot add duplicate."
        except ValueError:
            return "❌ The table number must be an integer."

    @log_function
    def get_table_list(self, status="all"):
        table_list = []
        if status == "all":
            table_list = self._fetch_table_list()
        else:
            results = self.execute(
                "SELECT id, table_number, status FROM tables WHERE status=%s ORDER BY table_number ASC ",
                (status,),
                fetch="all",
            )
            if not results:
                return f"  ❌ No table '{status}'\n"

            table_list = [
                Table(
                    table_id=row["id"],
                    table_number=row["table_number"],
                    status=row["status"],
                )
                for row in results
            ]
        tables_str = ""
        for table in table_list:
            tables_str += f"  {str(table)}\n"

        return tables_str

    def remove_table(self, table_number):
        try:
            table_number = int(table_number)
        except ValueError:
            return f"‼️ '{table_number}' is not an integer. "
        table = self.get_table_by_number(table_number)
        if not table:
            return f"❌ There is no table with number '{table_number}'."
        if table.status == "occupied":
            return (
                f"😡 Table number '{table_number}' is occupied. You cannot remove it."
            )
        self.execute("DELETE FROM tables WHERE table_number = %s", (table_number,))
        return f"✅ Table number '{table_number}' removed successfully."

    def get_table_by_number(self, table_number: int):

        table = self.execute(
            "SELECT id, table_number, status FROM tables WHERE table_number = %s",
            (table_number,),
            fetch="one",
        )
        if not table:
            return None
        table = Table(
            table_id=table["id"],
            table_number=table["table_number"],
            status=table["status"],
        )
        return table

    def get_table_status(self, table_number):
        try:
            table_number = int(table_number)
        except ValueError:
            return f"‼️ '{table_number}' is not an integer. "
        table = self.get_table_by_number(table_number)
        if not table:
            return None
        return table.status
