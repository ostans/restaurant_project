<div align="center">

# 🍽️ Restaurant Management System

A complete **command-line application** for managing the day‑to‑day operations of a restaurant — menu, tables, orders, and daily sales reports — all backed by a **PostgreSQL** database.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)

</div>

---

## ✨ Features

- 📜 **Menu Management** — add, rename, reprice, and soft‑delete menu items.
- 🪑 **Table Management** — add/remove tables and track their real‑time status.
- 🧾 **Order Management** — create orders, add items, adjust quantities, and remove items on open orders.
- 🔄 **Order Status** — move orders between `open`, `paid`, and `canceled`.
- 📊 **Daily Sales Reports** — view sales for a single day or a custom date range:
  - Total / paid / canceled orders
  - Total revenue (from paid orders only)
- ⚠️ **Smart Validation** — prevents duplicate menu items, removes only available tables, prevents conflicting order statuses, and validates all user input.
- 🕒 **Automatic Table Status** — tables become `occupied` when an order is opened and return to `available` once the order is paid or canceled.
- 📝 **Structured Logging** — every operation is logged with `loguru` to daily rotating, compressed log files.

---

## 🧱 Tech Stack

| Layer     | Technology                           |
| --------- | ------------------------------------ |
| Language  | Python 3.10+                         |
| Database  | PostgreSQL                           |
| DB Driver | `psycopg2-binary`                    |
| Logging   | `loguru`                             |
| Config    | `python-dotenv` (`.env` file)        |
| Interface | Terminal CLI (no external framework) |

---

## ⚙️ Installation & Setup

### 1. Prerequisites

- **Python 3.10+**
- **PostgreSQL** installed and running locally

### 2. Clone the repository

```bash
git clone <your-repo-url>
cd restaurant_project
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root (copy from the example below):

```bash
NAME=restaurant_db
PG_USER=postgres
PASSWORD=your_password
HOST=localhost
PORT=5432
```

> The `.env` file is already ignored by Git (see `.gitignore`).

### 6. Set up the database schema

Create the database (if it doesn’t exist) and apply the schema:

```bash
createdb restaurant_db
psql -U postgres -d restaurant_db -f schema.sql
```

The `schema.sql` file creates four tables: `menu_items`, `tables`, `orders`, and `order_details`.

---

## 🗄️ Database Schema

```
┌──────────────────┐      ┌──────────────────┐
│    menu_items    │      │      tables      │
├──────────────────┤      ├──────────────────┤
│ id (PK)          │      │ id (PK)          │
│ name             │      │ table_number (UK)│
│ price            │      │ status           │
│ is_available     │      └──────────────────┘
└──────────────────┘              │
        │                         │
        │                         │ 1   N
        │ 1                    ┌──▼──────────────┐
        │ N                    │     orders      │
┌───────▼──────────┐           ├─────────────────┤
│  order_details   │           │ id (PK)         │
├──────────────────┤           │ table_id (FK)   │
│ id (PK)          │           │ order_time      │
│ order_id (FK)    │           │ status          │
│ item_id (FK)     │           └─────────────────┘
│ item_name        │
│ quantity         │
│ unit_price       │
└──────────────────┘
```

**Notes:**

- `menu_items` uses a **partial unique index** so only _available_ items must have unique names.
- `order_details` stores a snapshot of `item_name` and `unit_price` so historical orders stay accurate even if the menu changes later.
- Removing a table sets the related `orders.table_id` to `NULL`; deleting an order cascades to its details.

---

## 🚀 Usage

Start the application from the project root:

```bash
python app.py
```

> `app.py` simply bootstraps the `RestaurantManagerCLI` and gracefully handles `KeyboardInterrupt` and fatal errors.

### Main Menu

```
===========================================
      🍽️  Restaurant Management System
===========================================
  1. Show Menu
  2. Show Table Status
  3. Add New Order
  4. Update Open Order Status
  5. View Order Details & Total Price
  6. Show Daily Sales Report
  7. Manage Tables
  8. Exit
-------------------------------------------
```

### Option Walkthrough

| No. | Option                       | What it does                                         |
| --- | ---------------------------- | ---------------------------------------------------- |
| 1   | **Show Menu**                | View / add / edit / delete menu items                |
| 2   | **Show Table Status**        | List all tables and their availability               |
| 3   | **Add New Order**            | Pick an available table, add items, set quantities   |
| 4   | **Update Open Order Status** | Mark an open order as `paid` or `canceled`           |
| 5   | **View Order Details**       | Inspect items, quantities, line totals & grand total |
| 6   | **Daily Sales Report**       | Sales summary for today or a custom date / range     |
| 7   | **Manage Tables**            | Add or remove tables                                 |
| 8   | **Exit**                     | Close the application                                |

**Typical workflow:**

1. Add menu items and tables.
2. Open a new order against an available table.
3. Add items and quantities to the order.
4. When the guest pays, mark the order as `paid` — the table automatically becomes `available` again.
5. Run the daily sales report to see the day's revenue.

Dates are entered in `YYYY-MM-DD` format. You can type `c` or `cancel` in most screens to go back.

---

## 📁 Project Structure

```
restaurant_project/
├── app.py                          # Entry point
├── requirements.txt                # Python dependencies
├── schema.sql                      # PostgreSQL schema
├── .env                            # Environment configuration (not committed)
├── .gitignore
├── LICENSE                         # GPL-3.0 license
├── log/                            # Daily rotating log files
└── src/
    ├── __init__.py                 # Package exports
    ├── cli/
    │   └── restaurant_manager_cli.py   # CLI interface (menus & user interaction)
    ├── config/
    │   └── logger.py               # Loguru setup (rotation, retention, compression)
    ├── database/
    │   └── database.py             # Database connection & query execution
    ├── models/
    │   ├── menu.py                 # MenuItem model
    │   ├── order.py                # Order & OrderItem models
    │   └── table.py                # Table model
    ├── services/
    │   ├── menu_service.py         # Menu business logic
    │   ├── order_service.py        # Order business logic
    │   ├── report_service.py       # Sales report logic
    │   └── table_service.py        # Table business logic
    └── utils/
        ├── decorators.py           # log_function timing decorator
        └── exceptions.py           # Custom exception hierarchy
```

### Architecture

The project follows a clean **layered architecture**:

- **Presentation** (`cli/`) — handles all user interaction and menu navigation.
- **Business Logic** (`services/`) — encapsulates the rules for menus, tables, orders, and reports.
- **Data** (`models/`) — plain Python objects representing database rows.
- **Data Access** (`database/`) — wraps PostgreSQL connections and queries.
- **Cross-cutting** (`config/`, `utils/`) — logging, decorators, and exceptions.

---

## 📝 Logging

The application uses **Loguru** for structured logging:

- Logs are written to `log/YYYY-MM-DD.log`.
- Logs **rotate** daily at midnight.
- Logs are **retained for 7 days**.
- Old logs are **compressed** to `.zip`.

Every service method is wrapped with the `@log_function` decorator, which records the start/end time and execution duration of each operation.

---

## 🖥️ System Requirements

| Component | Requirement                     |
| --------- | ------------------------------- |
| OS        | Linux, macOS, or Windows        |
| Python    | 3.10+                           |
| Database  | PostgreSQL (any recent version) |

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for modern restaurant management**

</div>
