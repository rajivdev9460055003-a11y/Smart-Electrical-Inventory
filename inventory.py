
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db


def open_inventory():

    window = tk.Toplevel()
    window.title("Inventory Management - OSWAL ELECTRICALS")
    window.geometry("1000x650")
    window.configure(bg="#eef2f7")

    tk.Label(
        window,
        text="INVENTORY MANAGEMENT",
        font=("Arial", 20, "bold"),
        bg="#17365d",
        fg="white",
        pady=15
    ).pack(fill="x")

    # INPUT SECTION
    frame = tk.Frame(window, bg="#eef2f7")
    frame.pack(pady=15)

    tk.Label(frame, text="Product Name:", bg="#eef2f7").grid(
        row=0, column=0, padx=10, pady=8
    )
    name_entry = tk.Entry(frame, width=25)
    name_entry.grid(row=0, column=1, padx=10)

    tk.Label(frame, text="Quantity:", bg="#eef2f7").grid(
        row=1, column=0, padx=10, pady=8
    )
    quantity_entry = tk.Entry(frame, width=25)
    quantity_entry.grid(row=1, column=1, padx=10)

    tk.Label(frame, text="Price (₹):", bg="#eef2f7").grid(
        row=2, column=0, padx=10, pady=8
    )
    price_entry = tk.Entry(frame, width=25)
    price_entry.grid(row=2, column=1, padx=10)

    # CLEAR INPUT FIELDS
    def clear_fields():
        name_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        table.selection_remove(table.selection())

    # SEARCH SECTION
    search_frame = tk.Frame(window, bg="#eef2f7")
    search_frame.pack(pady=10)

    tk.Label(
        search_frame,
        text="Search Product:",
        bg="#eef2f7"
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=25)
    search_entry.pack(side="left", padx=8)

    # PRODUCT TABLE
    table_frame = tk.Frame(window)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    table = ttk.Treeview(
        table_frame,
        columns=("Name", "Quantity", "Price"),
        show="headings"
    )

    table.heading("Name", text="Product Name")
    table.heading("Quantity", text="Quantity")
    table.heading("Price", text="Price (₹)")

    table.column("Name", width=300)
    table.column("Quantity", width=150)
    table.column("Price", width=150)

    table.pack(fill="both", expand=True)

    # LOAD PRODUCTS
    def load_products():

        table.delete(*table.get_children())

        conn = connect_db()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, quantity, price FROM products ORDER BY name"
            )

            for product_id, name, quantity, price in cursor.fetchall():
                table.insert(
                    "",
                    "end",
                    iid=str(product_id),
                    values=(name, quantity, price)
                )

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            conn.close()

    # SEARCH PRODUCT
    def search_product():

        search_text = search_entry.get().strip()

        table.delete(*table.get_children())

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, name, quantity, price
                FROM products
                WHERE name LIKE ?
                ORDER BY name
                """,
                ('%' + search_text + '%',)
            )

            records = cursor.fetchall()

            for product_id, name, quantity, price in records:
                table.insert(
                    "",
                    "end",
                    iid=str(product_id),
                    values=(name, quantity, price)
                )

            if search_text and not records:
                messagebox.showinfo(
                    "Search",
                    "No matching product found."
                )

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            conn.close()

    # ADD NEW PRODUCT
    def add_product():

        name = name_entry.get().strip()
        quantity = quantity_entry.get().strip()
        price = price_entry.get().strip()

        if not name or not quantity or not price:
            messagebox.showwarning(
                "Missing Information",
                "Please fill all fields."
            )
            return

        try:
            quantity_value = float(quantity)
            price_value = float(price)

            if quantity_value <= 0:
                raise ValueError("Quantity must be greater than zero.")

            if price_value < 0:
                raise ValueError("Price cannot be negative.")

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            return

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO products (name, quantity, price)
                VALUES (?, ?, ?)
                """,
                (name, quantity_value, price_value)
            )

            conn.commit()

        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            conn.close()

        load_products()
        clear_fields()

        messagebox.showinfo(
            "Success",
            "New product added successfully!"
        )

    # EDIT PRODUCT: LOAD SELECTED PRODUCT INTO FIELDS
    def edit_product():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Product",
                "Please select a product from the table first."
            )
            return

        product_id = int(selected[0])

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, quantity, price
                FROM products
                WHERE id = ?
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                messagebox.showerror(
                    "Error",
                    "Selected product was not found."
                )
                return

            name, quantity, price = product

            name_entry.delete(0, tk.END)
            name_entry.insert(0, name)

            quantity_entry.delete(0, tk.END)
            quantity_entry.insert(0, str(quantity))

            price_entry.delete(0, tk.END)
            price_entry.insert(0, str(price))

        except Exception as error:
            messagebox.showerror("Database Error", str(error))

        finally:
            conn.close()

    # UPDATE PRODUCT
    def update_product():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Product",
                "Please select a product first."
            )
            return

        name = name_entry.get().strip()
        quantity = quantity_entry.get().strip()
        price = price_entry.get().strip()

        if not name or not quantity or not price:
            messagebox.showwarning(
                "Missing Information",
                "Please fill all fields."
            )
            return

        try:
            quantity_value = float(quantity)
            price_value = float(price)

            if quantity_value < 0:
                raise ValueError("Quantity cannot be negative.")

            if price_value < 0:
                raise ValueError("Price cannot be negative.")

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            return

        product_id = int(selected[0])

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this product?"
        )

        if not confirm:
            return

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE products
                SET name = ?, quantity = ?, price = ?
                WHERE id = ?
                """,
                (name, quantity_value, price_value, product_id)
            )

            if cursor.rowcount == 0:
                messagebox.showerror(
                    "Error",
                    "Product was not found."
                )
                return

            conn.commit()

        except Exception as error:
            conn.rollback()
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            conn.close()

        load_products()
        clear_fields()

        messagebox.showinfo(
            "Success",
            "Product updated successfully!"
        )

    # ADD STOCK TO EXISTING PRODUCT
    def add_stock():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Product",
                "Please select a product from the table first."
            )
            return

        quantity = quantity_entry.get().strip()
        new_price = price_entry.get().strip()

        try:
            added_quantity = float(quantity)

            if added_quantity <= 0:
                raise ValueError(
                    "Purchased quantity must be greater than zero."
                )

            if new_price:
                price_value = float(new_price)

                if price_value < 0:
                    raise ValueError("Price cannot be negative.")
            else:
                price_value = None

        except ValueError as error:
            messagebox.showerror("Invalid Input", str(error))
            return

        product_id = int(selected[0])

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name, quantity FROM products WHERE id = ?",
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                messagebox.showerror(
                    "Error",
                    "Selected product was not found."
                )
                return

            product_name, old_quantity = product
            new_quantity = float(old_quantity) + added_quantity

            if price_value is None:
                cursor.execute(
                    """
                    UPDATE products
                    SET quantity = ?
                    WHERE id = ?
                    """,
                    (new_quantity, product_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE products
                    SET quantity = ?, price = ?
                    WHERE id = ?
                    """,
                    (new_quantity, price_value, product_id)
                )

            conn.commit()

        except Exception as error:
            conn.rollback()
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            conn.close()

        load_products()
        clear_fields()

        messagebox.showinfo(
            "Stock Updated",
            f"Product: {product_name}\n"
            f"Previous Stock: {old_quantity}\n"
            f"Purchased Stock: {added_quantity:g}\n"
            f"New Total Stock: {new_quantity:g}"
        )

    # DELETE PRODUCT
    def delete_product():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a product first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected product?"
        )

        if not confirm:
            return

        conn = connect_db()

        try:
            cursor = conn.cursor()

            for item in selected:
                cursor.execute(
                    "DELETE FROM products WHERE id = ?",
                    (int(item),)
                )

            conn.commit()

        except Exception as error:
            conn.rollback()
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            conn.close()

        load_products()
        clear_fields()

        messagebox.showinfo(
            "Success",
            "Product deleted successfully!"
        )

    # LOW STOCK ALERT
    def check_low_stock():

        conn = connect_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name, quantity
                FROM products
                WHERE quantity <= 10
                """
            )

            low_products = cursor.fetchall()

        except Exception as error:
            messagebox.showerror("Database Error", str(error))
            return

        finally:
            conn.close()

        if low_products:

            alert = "LOW STOCK WARNING!\n\n"

            for name, quantity in low_products:
                alert += f"{name} - Remaining: {quantity:g}\n"

            messagebox.showwarning("Low Stock Alert", alert)

    # BUTTONS
    tk.Button(
        search_frame,
        text="Search",
        command=search_product,
        width=10
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Show All",
        command=load_products,
        width=10
    ).pack(side="left", padx=5)

    button_frame = tk.Frame(window, bg="#eef2f7")
    button_frame.pack(pady=12)

    ttk.Button(
        button_frame,
        text="Add Product",
        command=add_product,
        width=14
    ).pack(side="left", padx=4)

    ttk.Button(
        button_frame,
        text="Edit Product",
        command=edit_product,
        width=14
    ).pack(side="left", padx=4)

    ttk.Button(
        button_frame,
        text="Update Product",
        command=update_product,
        width=15
    ).pack(side="left", padx=4)

    ttk.Button(
        button_frame,
        text="Add Stock",
        command=add_stock,
        width=12
    ).pack(side="left", padx=4)

    ttk.Button(
        button_frame,
        text="Delete Product",
        command=delete_product,
        width=14
    ).pack(side="left", padx=4)

    ttk.Button(
        button_frame,
        text="Refresh",
        command=load_products,
        width=10
    ).pack(side="left", padx=4)

    # INITIAL LOAD
    load_products()
    check_low_stock()
