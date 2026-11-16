import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from database import connect_db

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


# ================= SHOP PROFILE =================

def get_shop_profile():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_settings (
                id INTEGER PRIMARY KEY,
                shop_name TEXT,
                address TEXT,
                mobile TEXT,
                gstin TEXT,
                email TEXT,
                logo_path TEXT
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO shop_settings (id)
            VALUES (1)
        """)

        conn.commit()

        cursor.execute("""
            SELECT shop_name, address, mobile,
                   gstin, email, logo_path
            FROM shop_settings
            WHERE id = 1
        """)

        data = cursor.fetchone()

        if data:
            return {
                "shop_name": data[0] or "Electrical Shop",
                "address": data[1] or "",
                "mobile": data[2] or "",
                "gstin": data[3] or "",
                "email": data[4] or "",
                "logo_path": data[5] or ""
            }

    finally:
        conn.close()

    return {}


# ================= INVOICE FOLDER =================

def get_invoice_folder():

    app_name = "Smart Electrical Inventory & Loose-Wire Calculator"

    if getattr(sys, "frozen", False):

        if sys.platform == "darwin":
            data_folder = (
                Path.home()
                / "Library"
                / "Application Support"
                / app_name
            )

        elif os.name == "nt":
            data_folder = (
                Path(os.environ.get("LOCALAPPDATA", Path.home()))
                / app_name
            )

        else:
            data_folder = (
                Path.home()
                / ".local"
                / "share"
                / app_name
            )

        bill_folder = data_folder / "Bills"

    else:
        bill_folder = Path(__file__).resolve().parent / "Bills"

    bill_folder.mkdir(parents=True, exist_ok=True)

    return bill_folder


# ================= MAIN BILLING WINDOW =================

def open_billing():

    shop_profile = get_shop_profile()

    window = tk.Toplevel()
    window.title("Billing System")
    window.geometry("950x750")
    window.configure(bg="#f1f5f9")

    # ================= SHOP HEADING =================

    tk.Label(
        window,
        text=shop_profile.get("shop_name", "Electrical Shop"),
        font=("Arial", 24, "bold"),
        fg="#17365d",
        bg="#f1f5f9"
    ).pack(pady=(15, 3))

    tk.Label(
        window,
        text="CUSTOMER BILLING SYSTEM",
        font=("Arial", 14, "bold"),
        bg="#f1f5f9"
    ).pack(pady=5)

    # ================= CUSTOMER DETAILS =================

    customer_frame = tk.LabelFrame(
        window,
        text="Customer Details",
        padx=10,
        pady=10
    )

    customer_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    tk.Label(
        customer_frame,
        text="Customer Name"
    ).grid(row=0, column=0)

    name_entry = tk.Entry(
        customer_frame,
        width=25
    )

    name_entry.grid(
        row=0,
        column=1,
        padx=10
    )

    tk.Label(
        customer_frame,
        text="Mobile Number"
    ).grid(row=0, column=2)

    mobile_entry = tk.Entry(
        customer_frame,
        width=20
    )

    mobile_entry.grid(
        row=0,
        column=3,
        padx=10
    )

    # ================= PRODUCT DETAILS =================

    product_frame = tk.LabelFrame(
        window,
        text="Product Details",
        padx=10,
        pady=10
    )

    product_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    tk.Label(
        product_frame,
        text="Product"
    ).grid(row=0, column=0)

    product_entry = ttk.Combobox(
        product_frame,
        width=18,
        state="readonly"
    )

    product_entry.grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Label(
        product_frame,
        text="Quantity"
    ).grid(row=0, column=2)

    quantity_entry = tk.Entry(
        product_frame,
        width=10
    )

    quantity_entry.grid(
        row=0,
        column=3,
        padx=5
    )

    tk.Label(
        product_frame,
        text="Rate (₹)"
    ).grid(row=0, column=4)

    rate_entry = tk.Entry(
        product_frame,
        width=10
    )

    rate_entry.grid(
        row=0,
        column=5,
        padx=5
    )

    # ================= LOAD PRODUCTS =================

    product_data = {}

    def load_products():

        product_data.clear()

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name, quantity, price
                FROM products
                ORDER BY name
            """)

            products = cursor.fetchall()

        finally:
            conn.close()

        product_names = []

        for name, stock, price in products:

            product_data[name] = {
                "stock": float(stock),
                "price": float(price)
            }

            product_names.append(name)

        product_entry["values"] = product_names

    # ================= SELECT PRODUCT =================

    def select_product(event=None):

        product = product_entry.get()

        if product not in product_data:
            return

        rate = product_data[product]["price"]

        rate_entry.delete(0, tk.END)
        rate_entry.insert(0, f"{rate:.2f}")

    product_entry.bind(
        "<<ComboboxSelected>>",
        select_product
    )

    try:
        load_products()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            f"Unable to load products:\n{error}"
        )

        window.destroy()
        return

    # ================= PRODUCT TABLE =================

    table = ttk.Treeview(
        window,
        columns=("Product", "Quantity", "Rate", "Total"),
        show="headings"
    )

    for col in ("Product", "Quantity", "Rate", "Total"):

        table.heading(
            col,
            text=col
        )

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    # ================= ADD PRODUCT =================

    def add_product():

        product = product_entry.get().strip()

        if product not in product_data:

            messagebox.showerror(
                "Error",
                "Please select a product."
            )

            return

        try:
            quantity = float(quantity_entry.get())

            if quantity <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Quantity",
                "Enter a valid quantity greater than zero."
            )

            return

        try:
            rate = float(rate_entry.get())

            if rate < 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Rate",
                "Enter a valid selling rate."
            )

            return

        available_stock = product_data[product]["stock"]

        already_added = sum(
            float(table.item(item)["values"][1])
            for item in table.get_children()
            if table.item(item)["values"][0] == product
        )

        remaining_stock = available_stock - already_added

        if quantity > remaining_stock:

            messagebox.showerror(
                "Insufficient Stock",
                f"Available stock for {product}: {remaining_stock}"
            )

            return

        total = quantity * rate

        table.insert(
            "",
            "end",
            values=(
                product,
                quantity,
                f"{rate:.2f}",
                f"{total:.2f}"
            )
        )

        product_entry.set("")

        quantity_entry.delete(0, tk.END)
        rate_entry.delete(0, tk.END)

    ttk.Button(
        product_frame,
        text="Add Product",
        command=add_product
    ).grid(
        row=1,
        column=2,
        columnspan=2,
        pady=12
    )

    # ================= GST SECTION =================

    gst_frame = tk.Frame(
        window,
        bg="#f1f5f9"
    )

    gst_frame.pack(pady=5)

    tk.Label(
        gst_frame,
        text="GST Rate (%):",
        bg="#f1f5f9"
    ).pack(side="left")

    gst_entry = tk.Entry(
        gst_frame,
        width=8
    )

    gst_entry.insert(0, "0")

    gst_entry.pack(
        side="left",
        padx=5
    )

    # ================= BILL OUTPUT =================

    bill_output = tk.Text(
        window,
        height=9,
        width=100
    )

    bill_output.pack(
        padx=20,
        pady=10
    )

    # ================= GENERATE PDF =================

    def generate_pdf(
        filename,
        invoice_no,
        customer,
        mobile,
        bill_date,
        items,
        subtotal,
        gst_rate,
        gst_amount,
        grand_total
    ):

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ShopTitle",
            parent=styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#17365d"),
            alignment=TA_CENTER
        )

        story = []

        # Shop Logo

        logo = shop_profile.get("logo_path", "")

        if logo and Path(logo).is_file():

            try:
                logo_image = Image(
                    logo,
                    width=65,
                    height=65
                )

                logo_image.hAlign = "CENTER"

                story.append(logo_image)
                story.append(Spacer(1, 5))

            except Exception:
                pass

        # Shop Name

        story.append(
            Paragraph(
                escape(shop_profile.get(
                    "shop_name",
                    "Electrical Shop"
                )),
                title_style
            )
        )

        story.append(
            Paragraph(
                "INVOICE / TAX BILL",
                ParagraphStyle(
                    "InvoiceHeading",
                    parent=styles["Heading2"],
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#2463a6")
                )
            )
        )

        story.append(Spacer(1, 12))

        # Shop Details

        shop_details = []

        if shop_profile.get("address"):
            shop_details.append([
                "Address:",
                escape(shop_profile["address"])
            ])

        if shop_profile.get("mobile"):
            shop_details.append([
                "Mobile:",
                escape(shop_profile["mobile"])
            ])

        if shop_profile.get("gstin"):
            shop_details.append([
                "GSTIN:",
                escape(shop_profile["gstin"])
            ])

        if shop_profile.get("email"):
            shop_details.append([
                "Email:",
                escape(shop_profile["email"])
            ])

        if shop_details:

            shop_table = Table(
                shop_details,
                colWidths=[80, 400]
            )

            shop_table.setStyle(TableStyle([

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )

            ]))

            story.append(shop_table)

        story.append(Spacer(1, 15))

        # Customer Details

        details = [
            ["Invoice Number:", str(invoice_no)],
            ["Customer Name:", escape(customer)],
            ["Mobile Number:", escape(mobile)],
            ["Date:", bill_date]
        ]

        details_table = Table(
            details,
            colWidths=[130, 350]
        )

        details_table.setStyle(TableStyle([

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ]))

        story.append(details_table)

        story.append(Spacer(1, 20))

        # Product Table

        data = [[
            "Product",
            "Quantity",
            "Rate (Rs.)",
            "Total (Rs.)"
        ]]

        for product, qty, rate, total in items:

            data.append([
                Paragraph(
                    escape(str(product)),
                    styles["Normal"]
                ),
                str(qty),
                f"{float(rate):.2f}",
                f"{float(total):.2f}"
            ])

        product_table = Table(
            data,
            colWidths=[200, 80, 100, 100]
        )

        product_table.setStyle(TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#17365d")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "RIGHT"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ]))

        story.append(product_table)

        story.append(Spacer(1, 20))

        # GST and Total

        totals = [
            ["Subtotal:", f"Rs. {subtotal:.2f}"],
            [f"GST ({gst_rate}%):", f"Rs. {gst_amount:.2f}"],
            ["GRAND TOTAL:", f"Rs. {grand_total:.2f}"]
        ]

        totals_table = Table(
            totals,
            colWidths=[300, 180]
        )

        totals_table.setStyle(TableStyle([

            (
                "ALIGN",
                (1, 0),
                (1, -1),
                "RIGHT"
            ),

            (
                "FONTNAME",
                (0, -1),
                (-1, -1),
                "Helvetica-Bold"
            ),

            (
                "BACKGROUND",
                (0, -1),
                (-1, -1),
                colors.HexColor("#dce6f1")
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                10
            )

        ]))

        story.append(totals_table)

        story.append(Spacer(1, 40))

        # Footer

        story.append(
            Paragraph(
                "<b>Thank you for shopping with us!</b>",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    alignment=TA_CENTER
                )
            )
        )

        pdf = SimpleDocTemplate(
            str(filename),
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=35
        )

        pdf.build(story)

    # ================= GENERATE BILL =================

    def generate_bill():

        customer = name_entry.get().strip()
        mobile = mobile_entry.get().strip()

        if not customer:

            messagebox.showerror(
                "Error",
                "Please enter customer name."
            )

            return

        if not mobile.isdigit() or len(mobile) != 10:

            messagebox.showerror(
                "Invalid Mobile",
                "Enter a valid 10-digit mobile number."
            )

            return

        items = table.get_children()

        if not items:

            messagebox.showerror(
                "Error",
                "Add at least one product."
            )

            return

        try:
            gst_rate = float(gst_entry.get())

            if not 0 <= gst_rate <= 100:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid GST",
                "Enter a valid GST percentage."
            )

            return

        item_details = [
            table.item(item)["values"]
            for item in items
        ]

        subtotal = sum(
            float(item[3])
            for item in item_details
        )

        gst_amount = subtotal * gst_rate / 100
        grand_total = subtotal + gst_amount

        bill_date = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        # ================= SAVE SALE =================

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sales
                (
                    customer_name,
                    mobile,
                    subtotal,
                    gst,
                    grand_total
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                customer,
                mobile,
                subtotal,
                gst_amount,
                grand_total
            ))

            sale_id = cursor.lastrowid

            # Deduct stock and save sale items

            for product, qty, rate, total in item_details:

                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - ?
                    WHERE name = ? COLLATE NOCASE
                    AND quantity >= ?
                """, (
                    float(qty),
                    str(product).strip(),
                    float(qty)
                ))

                if cursor.rowcount == 0:

                    raise ValueError(
                        f"{product} not found or insufficient stock!"
                    )

                cursor.execute("""
                    INSERT INTO sale_items
                    (
                        sale_id,
                        product_name,
                        quantity,
                        price,
                        total
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sale_id,
                    product,
                    float(qty),
                    float(rate),
                    float(total)
                ))

            conn.commit()

        except Exception as error:

            conn.rollback()

            messagebox.showerror(
                "Billing Error",
                str(error)
            )

            return

        finally:
            conn.close()

        # ================= TXT INVOICE =================

        shop_name = shop_profile.get(
            "shop_name",
            "Electrical Shop"
        )

        bill = f"""
{shop_name}
INVOICE / TAX BILL
--------------------------------------------------

Address: {shop_profile.get('address', '')}
Mobile: {shop_profile.get('mobile', '')}
GSTIN: {shop_profile.get('gstin', '')}
Email: {shop_profile.get('email', '')}

--------------------------------------------------

Invoice Number: {sale_id}
Customer Name: {customer}
Customer Mobile: {mobile}
Date: {bill_date}

--------------------------------------------------
Product          Qty       Rate          Total
--------------------------------------------------
"""

        for product, qty, rate, total in item_details:

            bill += (
                f"{str(product):<16} "
                f"{qty:<9} "
                f"{float(rate):<13.2f} "
                f"{float(total):.2f}\n"
            )

        bill += f"""
--------------------------------------------------
Subtotal:                         Rs. {subtotal:.2f}
GST ({gst_rate}%):                     Rs. {gst_amount:.2f}

GRAND TOTAL:                      Rs. {grand_total:.2f}
--------------------------------------------------

          THANK YOU FOR SHOPPING!
"""

        bill_output.delete("1.0", tk.END)
        bill_output.insert(tk.END, bill)

        # ================= SAVE INVOICE FILES =================

        try:

            bill_folder = get_invoice_folder()

            filename = f"Invoice_{sale_id}"

            txt_path = bill_folder / f"{filename}.txt"
            pdf_path = bill_folder / f"{filename}.pdf"

            # Save TXT

            with open(
                txt_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(bill)

            # Generate PDF

            generate_pdf(
                pdf_path,
                sale_id,
                customer,
                mobile,
                bill_date,
                item_details,
                subtotal,
                gst_rate,
                gst_amount,
                grand_total
            )

        except Exception as error:

            messagebox.showwarning(
                "Invoice Saving Error",
                f"Sale was saved, but the invoice files could not be created:\n{error}"
            )

            return

        # ================= SUCCESS MESSAGE =================

        messagebox.showinfo(
            "Success",
            f"Invoice generated successfully!\n\n"
            f"Shop: {shop_name}\n"
            f"Invoice Number: {sale_id}\n\n"
            f"TXT: {txt_path}\n"
            f"PDF: {pdf_path}"
        )

    # ================= GENERATE BUTTON =================

    tk.Button(
        window,
        text="GENERATE BILL",
        command=generate_bill,
        bg="#198754",
        fg="white",
        font=("Arial", 13, "bold"),
        padx=20,
        pady=8
    ).pack(pady=12)