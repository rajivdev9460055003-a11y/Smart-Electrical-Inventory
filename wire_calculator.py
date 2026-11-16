import tkinter as tk
from tkinter import ttk, messagebox


def open_wire_calculator():

    window = tk.Toplevel()
    window.title("Loose Wire Calculator")
    window.geometry("600x500")
    window.configure(bg="#f0f4f8")

    # Heading
    tk.Label(
        window,
        text="LOOSE WIRE CALCULATOR",
        font=("Arial", 20, "bold"),
        bg="#f0f4f8",
        fg="#17365D"
    ).pack(pady=25)

    # Input Frame
    frame = tk.Frame(window, bg="#f0f4f8")
    frame.pack(pady=15)

    # Wire Type
    tk.Label(
        frame, text="Wire Type:",
        font=("Arial", 12), bg="#f0f4f8"
    ).grid(row=0, column=0, padx=10, pady=12)

    wire_type = ttk.Combobox(
        frame,
        values=["Copper Wire", "Aluminium Wire", "Flexible Wire"],
        state="readonly",
        width=22
    )
    wire_type.grid(row=0, column=1)
    wire_type.current(0)

    # Length
    tk.Label(
        frame, text="Length (Meters):",
        font=("Arial", 12), bg="#f0f4f8"
    ).grid(row=1, column=0, padx=10, pady=12)

    length_entry = tk.Entry(frame, font=("Arial", 12))
    length_entry.grid(row=1, column=1)

    # Price per meter
    tk.Label(
        frame, text="Price Per Meter (₹):",
        font=("Arial", 12), bg="#f0f4f8"
    ).grid(row=2, column=0, padx=10, pady=12)

    price_entry = tk.Entry(frame, font=("Arial", 12))
    price_entry.grid(row=2, column=1)

    # Result
    result_label = tk.Label(
        window,
        text="Total Amount: ₹0.00",
        font=("Arial", 18, "bold"),
        fg="green",
        bg="#f0f4f8"
    )
    result_label.pack(pady=25)

    # Calculate Function
    def calculate():

        try:
            length = float(length_entry.get())
            price = float(price_entry.get())

            if length <= 0 or price < 0:
                raise ValueError

            total = length * price

            result_label.config(
                text=f"Total Amount: ₹{total:.2f}"
            )

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid positive length and non-negative price."
            )

    # Reset Function
    def reset():

        length_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)

        result_label.config(
            text="Total Amount: ₹0.00"
        )

    # Buttons
    tk.Button(
        window,
        text="Calculate Price",
        command=calculate,
        bg="#198754",
        fg="white",
        font=("Arial", 12, "bold"),
        width=18
    ).pack(pady=8)

    tk.Button(
        window,
        text="Reset",
        command=reset,
        bg="#dc3545",
        fg="white",
        font=("Arial", 11),
        width=12
    ).pack(pady=5)