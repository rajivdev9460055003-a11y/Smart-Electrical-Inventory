
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from pathlib import Path
import subprocess
import platform


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


# ================= SALES RECORDS =================

def open_sales_records():

    shop_name = get_shop_name()

    window = tk.Toplevel()
    window.title(f"Customer & Sales Management - {shop_name}")
    window.geometry("1100x650")

    tk.Label(
        window,
        text=f"{shop_name.upper()} - CUSTOMER & SALES HISTORY",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # SEARCH SECTION

    search_frame = tk.Frame(window)
    search_frame.pack(pady=10)

    tk.Label(
        search_frame,
        text="Search Customer:"
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=10)

    # SALES TABLE

    table = ttk.Treeview(
        window,
        columns=(
            "ID", "Customer", "Mobile",
            "Subtotal", "GST", "Grand Total", "Date"
        ),
        show="headings"
    )

    headings = {
        "ID": "Bill ID",
        "Customer": "Customer Name",
        "Mobile": "Mobile",
        "Subtotal": "Subtotal",
        "GST": "GST",
        "Grand Total": "Grand Total",
        "Date": "Sale Date"
    }

    for col, heading in headings.items():
        table.heading(col, text=heading)
        table.column(col, width=140)

    table.pack(fill="both", expand=True, padx=15, pady=10)

    # LOAD SALES

    def load_sales():

        table.delete(*table.get_children())

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, customer_name, mobile,
                       subtotal, gst, grand_total, sale_date
                FROM sales
                ORDER BY id DESC
            """)

            for row in cursor.fetchall():
                table.insert("", "end", values=row)

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            conn.close()

    # SEARCH CUSTOMER

    def search_customer():

        search_text = search_entry.get().strip()

        if not search_text:
            messagebox.showwarning(
                "Search",
                "Enter a customer name or mobile number."
            )
            return

        table.delete(*table.get_children())

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, customer_name, mobile,
                       subtotal, gst, grand_total, sale_date
                FROM sales
                WHERE customer_name LIKE ?
                   OR mobile LIKE ?
                ORDER BY id DESC
            """, (
                "%" + search_text + "%",
                "%" + search_text + "%"
            ))

            records = cursor.fetchall()

            for row in records:
                table.insert("", "end", values=row)

            if not records:
                messagebox.showinfo(
                    "Search Result",
                    "No customer records found."
                )

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            conn.close()

    # VIEW BILL DETAILS

    def view_bill_details():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Select a bill first."
            )
            return

        bill_id = table.item(selected[0])["values"][0]

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT product_name, quantity, price, total
                FROM sale_items
                WHERE sale_id = ?
            """, (bill_id,))

            items = cursor.fetchall()

        finally:
            conn.close()

        if not items:
            messagebox.showinfo(
                "Bill Details",
                "No product details found."
            )
            return

        details_window = tk.Toplevel(window)
        details_window.title(f"Bill Details - {bill_id}")
        details_window.geometry("650x350")

        tk.Label(
            details_window,
            text=f"{shop_name.upper()} - INVOICE #{bill_id}",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        details_table = ttk.Treeview(
            details_window,
            columns=("Product", "Quantity", "Rate", "Total"),
            show="headings"
        )

        for col in ("Product", "Quantity", "Rate", "Total"):
            details_table.heading(col, text=col)
            details_table.column(col, width=140)

        details_table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        for item in items:
            details_table.insert("", "end", values=item)

    # OPEN PDF INVOICE

    def open_pdf_invoice():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a bill first."
            )
            return

        bill_id = table.item(selected[0])["values"][0]

        pdf_path = (
            Path(__file__).parent
            / "Bills"
            / f"Invoice_{bill_id}.pdf"
        )

        if not pdf_path.exists():
            messagebox.showerror(
                "Invoice Not Found",
                f"PDF invoice not found:\n{pdf_path}"
            )
            return

        try:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", str(pdf_path)])

            elif platform.system() == "Windows":
                import os
                os.startfile(str(pdf_path))

            else:
                subprocess.Popen(["xdg-open", str(pdf_path)])

        except Exception as error:
            messagebox.showerror("Error", str(error))

    # PRINT PDF INVOICE

    def print_pdf_invoice():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a bill first."
            )
            return

        bill_id = table.item(selected[0])["values"][0]

        pdf_path = (
            Path(__file__).parent
            / "Bills"
            / f"Invoice_{bill_id}.pdf"
        )

        if not pdf_path.exists():
            messagebox.showerror(
                "Invoice Not Found",
                "PDF invoice not found."
            )
            return

        try:
            if platform.system() == "Darwin":
                subprocess.Popen(["lp", str(pdf_path)])

            elif platform.system() == "Windows":
                import os
                os.startfile(str(pdf_path), "print")

            else:
                subprocess.Popen(["lp", str(pdf_path)])

            messagebox.showinfo(
                "Print Invoice",
                "Invoice sent to the printer."
            )

        except Exception as error:
            messagebox.showerror(
                "Printing Error",
                f"Could not print invoice:\n{error}"
            )

    # TOTAL SALES

    def show_total():

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COALESCE(SUM(grand_total), 0) FROM sales"
            )

            total = cursor.fetchone()[0]

        finally:
            conn.close()

        messagebox.showinfo(
            "Total Sales",
            f"Total Sales Amount: ₹{total:.2f}"
        )

    # DAILY AND MONTHLY SALES REPORT

    def show_sales_report():

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(subtotal), 0),
                    COALESCE(SUM(gst), 0),
                    COALESCE(SUM(grand_total), 0)
                FROM sales
                WHERE date(sale_date, 'localtime') =
                      date('now', 'localtime')
            """)

            daily = cursor.fetchone()

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(subtotal), 0),
                    COALESCE(SUM(gst), 0),
                    COALESCE(SUM(grand_total), 0)
                FROM sales
                WHERE strftime('%Y-%m', sale_date, 'localtime') =
                      strftime('%Y-%m', 'now', 'localtime')
            """)

            monthly = cursor.fetchone()

        except Exception as error:
            messagebox.showerror("Report Error", str(error))
            return

        finally:
            conn.close()

        report_window = tk.Toplevel(window)
        report_window.title(f"{shop_name} - Sales Report")
        report_window.geometry("650x500")
        report_window.configure(bg="#eef2f7")

        tk.Label(
            report_window,
            text=f"{shop_name.upper()} - SALES REPORT",
            font=("Arial", 22, "bold"),
            bg="#17365d",
            fg="white",
            pady=15
        ).pack(fill="x")

        # DAILY REPORT

        daily_frame = tk.LabelFrame(
            report_window,
            text="TODAY'S SALES",
            font=("Arial", 14, "bold"),
            bg="white",
            padx=20,
            pady=15
        )
        daily_frame.pack(fill="x", padx=25, pady=20)

        daily_text = (
            f"Number of Bills: {daily[0]}\n"
            f"Subtotal: ₹{daily[1]:.2f}\n"
            f"GST Collected: ₹{daily[2]:.2f}\n"
            f"Total Sales: ₹{daily[3]:.2f}"
        )

        tk.Label(
            daily_frame,
            text=daily_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(anchor="w")

        # MONTHLY REPORT

        monthly_frame = tk.LabelFrame(
            report_window,
            text="CURRENT MONTH'S SALES",
            font=("Arial", 14, "bold"),
            bg="white",
            padx=20,
            pady=15
        )
        monthly_frame.pack(fill="x", padx=25, pady=15)

        monthly_text = (
            f"Number of Bills: {monthly[0]}\n"
            f"Subtotal: ₹{monthly[1]:.2f}\n"
            f"GST Collected: ₹{monthly[2]:.2f}\n"
            f"Total Sales: ₹{monthly[3]:.2f}"
        )

        tk.Label(
            monthly_frame,
            text=monthly_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(anchor="w")

        tk.Button(
            report_window,
            text="Close",
            command=report_window.destroy,
            width=15
        ).pack(pady=15)

    # BUTTONS

    button_frame = tk.Frame(window)
    button_frame.pack(pady=12)

    tk.Button(
        search_frame,
        text="Search",
        command=search_customer
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Show All",
        command=load_sales
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Refresh Records",
        command=load_sales
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="View Bill Details",
        command=view_bill_details
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Open PDF Invoice",
        command=open_pdf_invoice
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Print Invoice",
        command=print_pdf_invoice
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Total Sales",
        command=show_total
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Sales Report",
        command=show_sales_report
    ).pack(side="left", padx=5)

    load_sales()
