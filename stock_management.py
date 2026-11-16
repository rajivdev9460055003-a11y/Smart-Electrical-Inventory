
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


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


# ================= STOCK MANAGEMENT =================

def open_stock_management():

    shop_name = get_shop_name()

    window = tk.Toplevel()
    window.title(f"{shop_name} - Stock Management")
    window.geometry("800x500")

    tk.Label(
        window,
        text=f"{shop_name.upper()} - STOCK MANAGEMENT",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # ================= PRODUCT TABLE =================

    table = ttk.Treeview(
        window,
        columns=("ID", "Name", "Quantity", "Price"),
        show="headings"
    )

    for col in ("ID", "Name", "Quantity", "Price"):
        table.heading(col, text=col)

    table.column("ID", width=70)
    table.column("Name", width=280)
    table.column("Quantity", width=150)
    table.column("Price", width=150)

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    # ================= QUANTITY INPUT =================

    frame = tk.Frame(window)
    frame.pack(pady=10)

    tk.Label(
        frame,
        text="Stock Quantity:"
    ).grid(row=0, column=0, padx=5)

    quantity_entry = tk.Entry(frame)
    quantity_entry.grid(row=0, column=1, padx=10)

    # ================= LOAD STOCK =================

    def load_stock():

        table.delete(*table.get_children())

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, quantity, price
                FROM products
                ORDER BY name
            """)

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

        finally:
            conn.close()

    # ================= UPDATE STOCK =================

    def update_stock(operation):

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a product.",
                parent=window
            )
            return

        try:
            amount = float(quantity_entry.get())

            if amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Enter a valid quantity greater than zero.",
                parent=window
            )
            return

        product_id = table.item(selected[0])["values"][0]
        product_name = table.item(selected[0])["values"][1]

        if operation == "reduce":

            confirm = messagebox.askyesno(
                "Confirm Stock Reduction",
                f"Reduce {amount:g} units of {product_name}?",
                parent=window
            )

            if not confirm:
                return

        conn = connect_db()

        try:
            cursor = conn.cursor()

            if operation == "add":

                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity + ?
                    WHERE id = ?
                """, (amount, product_id))

            else:

                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - ?
                    WHERE id = ? AND quantity >= ?
                """, (amount, product_id, amount))

                if cursor.rowcount == 0:
                    messagebox.showerror(
                        "Insufficient Stock",
                        "Insufficient stock! Available quantity is not enough.",
                        parent=window
                    )
                    return

            conn.commit()

        except Exception as error:
            conn.rollback()

            messagebox.showerror(
                "Stock Update Error",
                str(error),
                parent=window
            )
            return

        finally:
            conn.close()

        quantity_entry.delete(0, tk.END)

        load_stock()

        messagebox.showinfo(
            "Success",
            "Stock Updated Successfully!",
            parent=window
        )

    # ================= BUTTONS =================

    tk.Button(
        frame,
        text="Add Stock",
        command=lambda: update_stock("add"),
        width=15
    ).grid(row=1, column=0, pady=15, padx=10)

    tk.Button(
        frame,
        text="Reduce Stock",
        command=lambda: update_stock("reduce"),
        width=15
    ).grid(row=1, column=1, pady=15, padx=10)

    tk.Button(
        frame,
        text="Refresh Stock",
        command=load_stock,
        width=15
    ).grid(row=1, column=2, pady=15, padx=10)

    load_stock()
