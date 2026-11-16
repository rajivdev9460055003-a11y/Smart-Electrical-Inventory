import sqlite3
import sys
import shutil
import os
from pathlib import Path


# ================= APPLICATION NAME =================

APP_NAME = "Smart Electrical Inventory & Loose-Wire Calculator"


# ================= DATABASE LOCATION =================

def get_database_path():

    # Normal VS Code / Python execution
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().with_name("shop.db")

    # Packaged application: use a writable user-data folder
    if sys.platform == "darwin":
        data_folder = (
            Path.home()
            / "Library"
            / "Application Support"
            / APP_NAME
        )

    elif os.name == "nt":
        data_folder = (
            Path(os.environ.get("LOCALAPPDATA", Path.home()))
            / APP_NAME
        )

    else:
        data_folder = (
            Path.home()
            / ".local"
            / "share"
            / APP_NAME
        )

    data_folder.mkdir(parents=True, exist_ok=True)

    database_path = data_folder / "shop.db"

    # Copy existing database on first application launch
    if not database_path.exists():

        bundled_database = (
            Path(sys._MEIPASS) / "shop.db"
        )

        if bundled_database.exists():
            shutil.copy2(
                bundled_database,
                database_path
            )

    return database_path


DB_NAME = get_database_path()


# ================= DATABASE CONNECTION =================

def connect_db():

    return sqlite3.connect(DB_NAME)


# ================= CREATE TABLES =================

def create_tables():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                mobile TEXT,
                subtotal REAL,
                gst REAL,
                grand_total REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_name TEXT,
                quantity REAL,
                price REAL,
                total REAL,
                FOREIGN KEY (sale_id) REFERENCES sales(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_name TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                previous_stock REAL NOT NULL,
                purchased_quantity REAL NOT NULL,
                new_stock REAL NOT NULL,
                purchase_price REAL,
                total_amount REAL,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        print("Database created successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ================= DATABASE BACKUP =================

def backup_database(destination_path):

    source_conn = None
    backup_conn = None

    try:
        destination = Path(destination_path)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        source_conn = connect_db()

        backup_conn = sqlite3.connect(destination)

        source_conn.backup(backup_conn)

        return True

    except Exception:
        raise

    finally:

        if backup_conn:
            backup_conn.close()

        if source_conn:
            source_conn.close()


# ================= MAIN =================

if __name__ == "__main__":
    create_tables()