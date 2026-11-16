
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import connect_db
from pathlib import Path
import shutil
import sys
import os


# ================= APP DATA FOLDER =================

APP_NAME = "Smart Electrical Inventory & Loose-Wire Calculator"


def get_app_data_folder():

    if getattr(sys, "frozen", False):

        if sys.platform == "darwin":
            folder = (
                Path.home()
                / "Library"
                / "Application Support"
                / APP_NAME
            )

        elif os.name == "nt":
            folder = (
                Path(os.environ.get("LOCALAPPDATA", Path.home()))
                / APP_NAME
            )

        else:
            folder = (
                Path.home()
                / ".local"
                / "share"
                / APP_NAME
            )

    else:
        folder = Path(__file__).resolve().parent

    folder.mkdir(parents=True, exist_ok=True)

    return folder


# ================= LOGO STORAGE =================

def store_logo_file(source_path):

    if not source_path:
        return ""

    source = Path(source_path).expanduser()

    if not source.is_file():
        raise FileNotFoundError("Selected logo file was not found.")

    logo_folder = get_app_data_folder() / "Assets"
    logo_folder.mkdir(parents=True, exist_ok=True)

    extension = source.suffix.lower()

    if extension not in [".png", ".jpg", ".jpeg"]:
        raise ValueError("Please select a PNG or JPG logo.")

    destination = logo_folder / f"shop_logo{extension}"

    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    return str(destination)


# ================= DATABASE TABLE =================

def create_shop_table():

    conn = connect_db()
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
    conn.close()


# ================= SHOP SETTINGS WINDOW =================

def open_shop_settings():

    create_shop_table()

    window = tk.Toplevel()
    window.title("Shop Profile & Settings")
    window.geometry("650x650")
    window.configure(bg="#f1f5f9")

    NAVY = "#142d4e"
    WHITE = "#ffffff"

    tk.Label(
        window,
        text="SHOP PROFILE & SETTINGS",
        font=("Arial", 22, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=20
    ).pack(fill="x")

    form = tk.Frame(window, bg=WHITE)
    form.pack(fill="both", expand=True, padx=30, pady=25)

    fields = [
        ("Shop Name", "shop_name"),
        ("Shop Address", "address"),
        ("Mobile Number", "mobile"),
        ("GSTIN Number", "gstin"),
        ("Email Address", "email")
    ]

    entries = {}

    for index, (label, key) in enumerate(fields):

        tk.Label(
            form,
            text=label,
            font=("Arial", 11, "bold"),
            bg=WHITE
        ).grid(
            row=index,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        entry = tk.Entry(
            form,
            width=35,
            font=("Arial", 11)
        )

        entry.grid(
            row=index,
            column=1,
            padx=10,
            pady=15
        )

        entries[key] = entry

    # ================= LOGO SELECTION =================

    logo_path = tk.StringVar()

    def choose_logo():

        path = filedialog.askopenfilename(
            title="Select Shop Logo",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg")
            ]
        )

        if path:
            logo_path.set(path)

    tk.Label(
        form,
        text="Shop Logo",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(
        row=5,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    logo_frame = tk.Frame(form, bg=WHITE)

    logo_frame.grid(
        row=5,
        column=1,
        padx=10,
        pady=15
    )

    tk.Entry(
        logo_frame,
        textvariable=logo_path,
        width=22
    ).pack(side="left")

    ttk.Button(
        logo_frame,
        text="Browse",
        command=choose_logo
    ).pack(side="left", padx=5)

    # ================= LOAD SAVED DETAILS =================

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT shop_name, address, mobile, gstin, email, logo_path
        FROM shop_settings
        WHERE id = 1
    """)

    data = cursor.fetchone()
    conn.close()

    if data:

        for index, (_, key) in enumerate(fields):

            if data[index]:
                entries[key].insert(0, data[index])

        saved_logo = data[5] or ""

        # Keep the saved logo path available.
        # If the file exists, copy it into the app's data folder.

        if saved_logo and Path(saved_logo).is_file():

            try:
                permanent_logo = store_logo_file(saved_logo)
                logo_path.set(permanent_logo)

            except Exception:
                logo_path.set(saved_logo)

        else:
            logo_path.set(saved_logo)

    # ================= SAVE SHOP DETAILS =================

    def save_settings():

        shop_name = entries["shop_name"].get().strip()

        if not shop_name:
            messagebox.showerror(
                "Required Field",
                "Please enter the shop name."
            )
            return

        selected_logo = logo_path.get().strip()

        try:

            if selected_logo and Path(selected_logo).is_file():
                selected_logo = store_logo_file(selected_logo)

            conn = connect_db()

            try:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE shop_settings
                    SET shop_name = ?,
                        address = ?,
                        mobile = ?,
                        gstin = ?,
                        email = ?,
                        logo_path = ?
                    WHERE id = 1
                """, (
                    shop_name,
                    entries["address"].get().strip(),
                    entries["mobile"].get().strip(),
                    entries["gstin"].get().strip(),
                    entries["email"].get().strip(),
                    selected_logo
                ))

                conn.commit()

            finally:
                conn.close()

            logo_path.set(selected_logo)

            messagebox.showinfo(
                "Success",
                "Shop profile saved successfully!"
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )

    tk.Button(
        form,
        text="SAVE SHOP DETAILS",
        command=save_settings,
        bg="#198754",
        fg=WHITE,
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10
    ).grid(
        row=6,
        column=0,
        columnspan=2,
        pady=30
    )
