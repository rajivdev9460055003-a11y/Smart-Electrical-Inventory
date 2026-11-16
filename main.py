
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from database import connect_db, backup_database
from shop_setting import open_shop_settings
from sales_records import open_sales_records
from stock_management import open_stock_management
from expenses import open_expenses
from billing import open_billing
from wire_calculator import open_wire_calculator
from inventory import open_inventory


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Electrical Shop Management System")
root.geometry("1100x850")
root.minsize(950, 750)
root.configure(bg="#f1f5f9")


# ================= COLOURS =================

NAVY = "#142d4e"
BLUE = "#2463a6"
BG = "#f1f5f9"
WHITE = "#ffffff"
GREEN = "#198754"
RED = "#dc3545"
TEXT = "#334155"


# ================= SHOP PROFILE =================

def get_shop_name():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT shop_name
            FROM shop_settings
            WHERE id = 1
        """)

        result = cursor.fetchone()

        if result and result[0]:
            return result[0]

        return "Electrical Shop"

    except Exception:
        return "Electrical Shop"

    finally:
        conn.close()


shop_name = get_shop_name()
root.title(f"{shop_name} - Management System")


# ================= HEADER =================

header = tk.Frame(root, bg=NAVY, height=115)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text=shop_name.upper(),
    font=("Arial", 27, "bold"),
    fg=WHITE,
    bg=NAVY
).pack(pady=(17, 4))

tk.Label(
    header,
    text="SMART ELECTRICAL INVENTORY & SHOP MANAGEMENT",
    font=("Arial", 11, "bold"),
    fg="#cbdcf0",
    bg=NAVY
).pack()


# ================= STATISTICS =================

tk.Label(
    root,
    text="SHOP OVERVIEW",
    font=("Arial", 17, "bold"),
    bg=BG,
    fg=NAVY
).pack(pady=(15, 8))

stats_frame = tk.Frame(root, bg=BG)
stats_frame.pack(fill="x", padx=18)

for column in range(5):
    stats_frame.columnconfigure(column, weight=1)


def get_statistics():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM products"
        )
        total_stock = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(grand_total), 0) FROM sales"
        )
        total_sales = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM products WHERE quantity <= 10"
        )
        low_stock = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        )
        total_expenses = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(grand_total), 0)
            FROM sales
            WHERE date(sale_date, 'localtime') =
                  date('now', 'localtime')
        """)
        today_sales = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(grand_total), 0)
            FROM sales
            WHERE strftime('%Y-%m', sale_date, 'localtime') =
                  strftime('%Y-%m', 'now', 'localtime')
        """)
        monthly_sales = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sales")
        total_bills = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(gst), 0) FROM sales"
        )
        total_gst = cursor.fetchone()[0]

        net_balance = total_sales - total_expenses

        return (
            total_products,
            total_stock,
            total_sales,
            low_stock,
            total_expenses,
            net_balance,
            today_sales,
            monthly_sales,
            total_bills,
            total_gst
        )

    finally:
        conn.close()


# ================= DASHBOARD CARDS =================

def create_card(parent, title, value, color, row, column):

    card = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground="#dbe3ed",
        highlightthickness=1
    )

    card.grid(
        row=row,
        column=column,
        padx=5,
        pady=6,
        sticky="nsew"
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 9, "bold"),
        bg=WHITE,
        fg="#64748b",
        wraplength=165
    ).pack(pady=(11, 5))

    value_label = tk.Label(
        card,
        text=value,
        font=("Arial", 15, "bold"),
        bg=WHITE,
        fg=color
    )

    value_label.pack(pady=(0, 11))

    return value_label


products_card = create_card(
    stats_frame, "TOTAL PRODUCTS", "0", NAVY, 0, 0
)

stock_card = create_card(
    stats_frame, "TOTAL STOCK", "0", GREEN, 0, 1
)

sales_card = create_card(
    stats_frame, "TOTAL SALES", "₹0.00", BLUE, 0, 2
)

low_stock_card = create_card(
    stats_frame, "LOW STOCK ITEMS", "0", RED, 0, 3
)

expenses_card = create_card(
    stats_frame, "TOTAL EXPENSES", "₹0.00", RED, 0, 4
)

balance_card = create_card(
    stats_frame, "SALES - EXPENSES", "₹0.00", GREEN, 1, 0
)

today_sales_card = create_card(
    stats_frame, "TODAY'S SALES", "₹0.00", BLUE, 1, 1
)

monthly_sales_card = create_card(
    stats_frame, "THIS MONTH'S SALES", "₹0.00", BLUE, 1, 2
)

bills_card = create_card(
    stats_frame, "TOTAL BILLS", "0", NAVY, 1, 3
)

gst_card = create_card(
    stats_frame, "TOTAL GST COLLECTED", "₹0.00", GREEN, 1, 4
)


# ================= REFRESH DASHBOARD =================

def refresh_dashboard():

    try:
        (
            products,
            stock,
            sales,
            low_stock,
            expenses,
            balance,
            today_sales,
            monthly_sales,
            total_bills,
            total_gst
        ) = get_statistics()

        products_card.config(text=str(products))
        stock_card.config(text=f"{stock:g}")
        sales_card.config(text=f"₹{sales:.2f}")
        low_stock_card.config(text=str(low_stock))
        expenses_card.config(text=f"₹{expenses:.2f}")

        balance_card.config(
            text=f"₹{balance:.2f}",
            fg=GREEN if balance >= 0 else RED
        )

        today_sales_card.config(text=f"₹{today_sales:.2f}")
        monthly_sales_card.config(text=f"₹{monthly_sales:.2f}")
        bills_card.config(text=str(total_bills))
        gst_card.config(text=f"₹{total_gst:.2f}")

    except Exception as e:
        messagebox.showerror("Dashboard Error", str(e))


# ================= LOW STOCK DETAILS =================

def show_low_stock_details():

    window = tk.Toplevel(root)
    window.title(f"Low Stock Details - {shop_name}")
    window.geometry("750x500")
    window.configure(bg=BG)

    tk.Label(
        window,
        text=f"{shop_name.upper()} - LOW STOCK DETAILS",
        font=("Arial", 19, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=18
    ).pack(fill="x")

    tk.Label(
        window,
        text="Products with available stock of 10 units or less",
        font=("Arial", 11),
        bg=BG,
        fg=TEXT
    ).pack(pady=12)

    table_frame = tk.Frame(window, bg=BG)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    table = ttk.Treeview(
        table_frame,
        columns=("Name", "Quantity", "Price"),
        show="headings"
    )

    table.heading("Name", text="Product Name")
    table.heading("Quantity", text="Available Quantity")
    table.heading("Price", text="Price (₹)")

    table.column("Name", width=300)
    table.column("Quantity", width=180, anchor="center")
    table.column("Price", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    status_label = tk.Label(
        window,
        text="",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=RED
    )
    status_label.pack(pady=5)

    def load_low_stock():

        table.delete(*table.get_children())

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name, quantity, price
                FROM products
                WHERE quantity <= 10
                ORDER BY quantity ASC
            """)

            products = cursor.fetchall()

            for name, quantity, price in products:
                table.insert(
                    "",
                    "end",
                    values=(
                        name,
                        f"{quantity:g}",
                        f"₹{price:.2f}"
                    )
                )

            if products:
                status_label.config(
                    text=f"Total Low Stock Products: {len(products)}",
                    fg=RED
                )
            else:
                status_label.config(
                    text="All products have sufficient stock!",
                    fg=GREEN
                )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            if conn:
                conn.close()

    tk.Button(
        window,
        text="Refresh Stock",
        command=load_low_stock,
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg=WHITE,
        width=18,
        cursor="hand2"
    ).pack(pady=12)

    load_low_stock()


# ================= PROFIT & LOSS REPORT =================

def open_profit_loss():

    window = tk.Toplevel(root)
    window.title(f"Financial Report - {shop_name}")
    window.geometry("550x480")
    window.configure(bg=BG)

    tk.Label(
        window,
        text=shop_name.upper(),
        font=("Arial", 20, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=12
    ).pack(fill="x")

    tk.Label(
        window,
        text="SALES & EXPENSE REPORT",
        font=("Arial", 14, "bold"),
        bg=BG,
        fg=NAVY
    ).pack(pady=15)

    report_frame = tk.Frame(
        window,
        bg=WHITE,
        highlightbackground="#dbe3ed",
        highlightthickness=1
    )
    report_frame.pack(fill="both", expand=True, padx=30, pady=10)

    sales_label = tk.Label(
        report_frame,
        text="Total Sales: ₹0.00",
        font=("Arial", 15, "bold"),
        bg=WHITE,
        fg=BLUE
    )
    sales_label.pack(pady=18)

    expenses_label = tk.Label(
        report_frame,
        text="Total Expenses: ₹0.00",
        font=("Arial", 15, "bold"),
        bg=WHITE,
        fg=RED
    )
    expenses_label.pack(pady=18)

    balance_label = tk.Label(
        report_frame,
        text="Sales - Expenses: ₹0.00",
        font=("Arial", 17, "bold"),
        bg=WHITE,
        fg=GREEN
    )
    balance_label.pack(pady=20)

    status_label = tk.Label(
        report_frame,
        text="",
        font=("Arial", 11),
        bg=WHITE,
        fg=TEXT
    )
    status_label.pack(pady=5)

    def refresh_report():

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(grand_total), 0)
                FROM sales
            """)
            total_sales = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
            """)
            total_expenses = cursor.fetchone()[0]

            balance = total_sales - total_expenses

            sales_label.config(
                text=f"Total Sales: ₹{total_sales:.2f}"
            )

            expenses_label.config(
                text=f"Total Expenses: ₹{total_expenses:.2f}"
            )

            balance_label.config(
                text=f"Sales - Expenses: ₹{balance:.2f}",
                fg=GREEN if balance >= 0 else RED
            )

            if balance >= 0:
                status_label.config(
                    text="Sales are higher than expenses.",
                    fg=GREEN
                )
            else:
                status_label.config(
                    text="Expenses are higher than sales.",
                    fg=RED
                )

        except Exception as e:
            messagebox.showerror(
                "Report Error",
                str(e),
                parent=window
            )

        finally:
            if conn:
                conn.close()

    tk.Button(
        window,
        text="Refresh Report",
        command=refresh_report,
        font=("Arial", 11, "bold"),
        bg=BLUE,
        fg=WHITE,
        width=20,
        cursor="hand2"
    ).pack(pady=15)

    refresh_report()


# ================= DATABASE BACKUP =================

def backup_shop_database():

    file_path = filedialog.asksaveasfilename(
        parent=root,
        title="Save Database Backup",
        defaultextension=".db",
        initialfile=(
            f"Shop_Backup_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        ),
        filetypes=[
            ("SQLite Database", "*.db")
        ]
    )

    if not file_path:
        return

    try:
        backup_database(file_path)

        messagebox.showinfo(
            "Backup Successful",
            f"Database backup saved successfully!\n\n{file_path}",
            parent=root
        )

    except Exception as e:
        messagebox.showerror(
            "Backup Failed",
            f"Unable to create database backup:\n{e}",
            parent=root
        )


# ================= NAVIGATION =================

tk.Label(
    root,
    text="MANAGE YOUR SHOP",
    font=("Arial", 17, "bold"),
    bg=BG,
    fg=NAVY
).pack(pady=(14, 8))

button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=4)

for column in range(2):
    button_frame.columnconfigure(column, weight=1)


def create_button(text, command, row, column):

    button = tk.Button(
        button_frame,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=NAVY,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        width=27,
        height=2,
        cursor="hand2",
        highlightbackground="#dbe3ed",
        highlightthickness=1
    )

    button.grid(
        row=row,
        column=column,
        padx=12,
        pady=6,
        sticky="ew"
    )

    button.bind(
        "<Enter>",
        lambda event: button.config(bg="#dceafe")
    )

    button.bind(
        "<Leave>",
        lambda event: button.config(bg=WHITE)
    )


create_button("Inventory Management", open_inventory, 0, 0)
create_button("Loose Wire Calculator", open_wire_calculator, 0, 1)

create_button("Billing System", open_billing, 1, 0)
create_button("Stock Management", open_stock_management, 1, 1)

create_button("Sales Records", open_sales_records, 2, 0)
create_button("Expense Management", open_expenses, 2, 1)

create_button("Low Stock Details", show_low_stock_details, 3, 0)
create_button("Profit & Loss Report", open_profit_loss, 3, 1)

create_button("Refresh Dashboard", refresh_dashboard, 4, 0)
create_button("Shop Profile & Settings", open_shop_settings, 4, 1)

create_button("Backup Database", backup_shop_database, 5, 0)


# ================= FOOTER =================

tk.Label(
    root,
    text=f"{shop_name} | Python • Tkinter • SQLite",
    font=("Arial", 10),
    bg=BG,
    fg="#64748b"
).pack(side="bottom", pady=10)


# ================= START DASHBOARD =================

refresh_dashboard()

root.mainloop()
