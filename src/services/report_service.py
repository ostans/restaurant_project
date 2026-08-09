from datetime import timedelta, datetime, date as date_type

from src import Database


class ReportService(Database):

    def daily_sales_report(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = date_type.today()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        if end_date is not None and isinstance(end_date, str):
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").date() + timedelta(
                days=1
            )
        else:
            end_datetime = start_date + timedelta(days=1)

        if start_date > end_datetime:
            raise ValueError("‼️ Start date must be before end")
        if start_date > date_type.today():
            raise ValueError("‼️ Start date must be today or in the past")
        if end_datetime > date_type.today() + timedelta(days=1):
            raise ValueError("‼️ End date must be today or in the past")

        total_orders = self.execute(
            """
            SELECT COUNT(*) AS total_orders
            FROM orders
            WHERE order_time::date >= %s AND order_time::date < %s """,
            (start_date, end_datetime),
            fetch="one",
        )["total_orders"]

        paid_orders = self.execute(
            """
            SELECT COUNT(*) AS paid_orders
            FROM orders
            WHERE status = 'paid' AND order_time::date >= %s AND order_time::date < %s""",
            (start_date, end_datetime),
            fetch="one",
        )["paid_orders"]

        canceled_orders = self.execute(
            """
            SELECT COUNT(*) AS cancelled_orders
            FROM orders
            WHERE status = 'canceled' AND order_time::date >= %s AND order_time::date < %s""",
            (start_date, end_datetime),
            fetch="one",
        )["cancelled_orders"]

        total_sales = self.execute(
            """
            SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
            FROM order_details oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'paid' AND order_time::date >= %s AND order_time::date < %s""",
            (start_date, end_datetime),
            fetch="one",
        )["total_sales"]

        date = (
            f"{start_date.strftime("%Y-%m-%d")}{f" - {end_date}" if end_date else ""}"
        )

        report = {
            "date": date,
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "canceled_orders": canceled_orders,
            "total_sales": total_sales,
        }

        return report
