import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


# ================= SHOP NAME =================

def get_shop_name():
    conn = None

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT shop_name FROM shop_settings WHERE id = 1"
        )

        result = cursor.fetchone()

        if result and result[0]:
            return result[0]

    except Exception:
        pass

    finally:
        if conn:
            conn.close()

    return "Electrical Shop"


# ================= EXPENSE MANAGEMENT =================

def open_expenses():

    shop_name = get_shop_name()

    window = tk.Toplevel()
    window.title(f"Expense Management - {shop_name}")
    window.geometry("950x650")
    window.minsize(900, 600)
    window.configure(bg="#eef2f7")

    # ================= HEADING =================

    tk.Label(
        window,
        text=f"{shop_name.upper()} - EXPENSE MANAGEMENT",
        font=("Arial", 20, "bold"),
        bg="#eef2f7",
        fg="#1e3a5f"
    ).pack(pady=15)

    # ================= INPUT FIELDS =================

    frame = tk.Frame(window, bg="#eef2f7")
    frame.pack(pady=10)

    tk.Label(
        frame,
        text="Expense Name",
        font=("Arial", 11, "bold"),
        bg="#eef2f7"
    ).grid(row=0, column=0, padx=10, pady=8)

    name_entry = tk.Entry(
        frame,
        width=28,
        font=("Arial", 11)
    )
    name_entry.grid(row=0, column=1, padx=10)

    tk.Label(
        frame,
        text="Amount (₹)",
        font=("Arial", 11, "bold"),
        bg="#eef2f7"
    ).grid(row=1, column=0, padx=10, pady=8)

    amount_entry = tk.Entry(
        frame,
        width=28,
        font=("Arial", 11)
    )
    amount_entry.grid(row=1, column=1, padx=10)

    # ================= BUTTON FRAME =================

    button_frame = tk.Frame(
        window,
        bg="#eef2f7"
    )

    button_frame.pack(
        side="bottom",
        fill="x",
        pady=15
    )

    # ================= EXPENSE TABLE =================

    table_frame = tk.Frame(window, bg="#eef2f7")

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    table = ttk.Treeview(
        table_frame,
        columns=("ID", "Name", "Amount", "Date"),
        show="headings"
    )

    table.heading("ID", text="ID")
    table.heading("Name", text="Expense Name")
    table.heading("Amount", text="Amount (₹)")
    table.heading("Date", text="Date")

    table.column("ID", width=60, anchor="center")
    table.column("Name", width=250, anchor="center")
    table.column("Amount", width=150, anchor="center")
    table.column("Date", width=250, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # ================= LOAD EXPENSES =================

    def load_expenses():

        table.delete(*table.get_children())

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, expense_name, amount, expense_date
                FROM expenses
                ORDER BY id DESC
            """)

            records = cursor.fetchall()

            for row in records:

                table.insert(
                    "",
                    "end",
                    values=(
                        row[0],
                        row[1],
                        f"{float(row[2]):.2f}",
                        row[3]
                    )
                )

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                f"Unable to load expenses:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ================= CLEAR FIELDS =================

    def clear_fields():

        name_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)

        name_entry.focus()

    # ================= ADD EXPENSE =================

    def add_expense():

        name = name_entry.get().strip()
        amount = amount_entry.get().strip()

        if not name or not amount:

            messagebox.showwarning(
                "Missing Information",
                "Please enter expense name and amount."
            )
            return

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid amount greater than zero."
            )
            return

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO expenses (expense_name, amount)
                VALUES (?, ?)
            """, (name, amount))

            conn.commit()

            clear_fields()
            load_expenses()

            messagebox.showinfo(
                "Success",
                "Expense Saved Successfully!"
            )

        except Exception as e:

            if conn:
                conn.rollback()

            messagebox.showerror(
                "Error",
                f"Unable to save expense:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ================= DELETE EXPENSE =================

    def delete_expense():

        selected = table.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select an expense from the table."
            )
            return

        expense_id = table.item(
            selected[0]
        )["values"][0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this expense?"
        )

        if not confirm:
            return

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )

            conn.commit()

            load_expenses()

            messagebox.showinfo(
                "Success",
                "Expense Deleted Successfully!"
            )

        except Exception as e:

            if conn:
                conn.rollback()

            messagebox.showerror(
                "Error",
                f"Unable to delete expense:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ================= TOTAL EXPENSES =================

    def show_total():

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT SUM(amount) FROM expenses"
            )

            total = cursor.fetchone()[0] or 0

            messagebox.showinfo(
                "Total Expenses",
                f"{shop_name}\n\n"
                f"Total Shop Expenses: ₹{total:.2f}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Unable to calculate total:\n{e}"
            )

        finally:
            if conn:
                conn.close()

    # ================= BUTTONS =================

    tk.Button(
        button_frame,
        text="Add Expense",
        command=add_expense,
        bg="#2563eb",
        fg="black",
        activebackground="#1d4ed8",
        width=16,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=12, expand=True)

    tk.Button(
        button_frame,
        text="Delete Expense",
        command=delete_expense,
        bg="#dc2626",
        fg="black",
        activebackground="#b91c1c",
        width=16,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=12, expand=True)

    tk.Button(
        button_frame,
        text="Refresh",
        command=load_expenses,
        bg="#0891b2",
        fg="black",
        activebackground="#0e7490",
        width=14,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=12, expand=True)

    tk.Button(
        button_frame,
        text="Total Expenses",
        command=show_total,
        bg="#15803d",
        fg="black",
        activebackground="#166534",
        width=16,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=12, expand=True)

    tk.Button(
        button_frame,
        text="Clear Fields",
        command=clear_fields,
        bg="#64748b",
        fg="black",
        width=14,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    ).pack(side="left", padx=12, expand=True)

    # ================= INITIAL LOAD =================

    load_expenses()