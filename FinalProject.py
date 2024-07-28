import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import win32print
import win32api

# Function to handle button click, insert data into database, and display data in the second GUI
def insert_and_display_data():
    # Get values from GUI fields
    line = line_var.get()
    month = month_var.get()
    day = day_var.get()
    product_name = product_name_entry.get()
    net_weight = net_weight_entry.get()
    packaging_type = packaging_var.get()
    comment = comment_entry.get("1.0", tk.END).strip()

    # Combine month and day into date format (e.g., "July 14")
    current_date = f"{month} {day}"

    # Insert into SQLite database
    conn = sqlite3.connect('inventory.db')  # Connect to or create SQLite database file
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (line TEXT, date TEXT, product_name TEXT, net_weight REAL, packaging_type TEXT, comment TEXT)''')
    c.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)", (line, current_date, product_name, net_weight, packaging_type, comment))
    conn.commit()
    conn.close()

    # Clear input fields after insertion
    product_name_entry.delete(0, tk.END)
    net_weight_entry.delete(0, tk.END)
    comment_entry.delete("1.0", tk.END)

    # Open new window to display data
    display_data()

# Function to fetch data from database and populate the listbox
def display_data():
    # Create new window for displaying data
    root_display = tk.Toplevel()
    root_display.title("Inventory Data Viewer")

    # Create a treeview (listbox) to display data
    data_listbox = ttk.Treeview(root_display, columns=("Line", "Date", "Product Name", "Net Weight (kg)", "Packaging Type", "Comment"), show="headings")
    data_listbox.heading("Line", text="Line")
    data_listbox.heading("Date", text="Date")
    data_listbox.heading("Product Name", text="Product Name")
    data_listbox.heading("Net Weight (kg)", text="Net Weight (kg)")
    data_listbox.heading("Packaging Type", text="Packaging Type")
    data_listbox.heading("Comment", text="Comment")
    data_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Fetch data from SQLite database
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    rows = c.fetchall()
    conn.close()

    # Populate the listbox with fetched data
    for row in rows:
        data_listbox.insert("", "end", values=row)

    # Add print button
    print_button = ttk.Button(root_display, text="Print Data", command=lambda: print_data(rows))
    print_button.pack(pady=10)

# Function to clear database (prompt for password)
def clear_database():
    # Prompt for password
    password = simpledialog.askstring("Password", "Enter Password to Clear Database:", show='*')
    if password == "admin":
        # Connect to SQLite database and clear all data
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("DELETE FROM inventory")  # Delete all rows from the inventory table
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Database cleared successfully!")
    elif password is None:
        # User clicked Cancel
        return
    else:
        messagebox.showerror("Error", "Incorrect password!")

# Function to print the data to the specified printer
def print_data(data):
    # Create a temporary text file with the data
    temp_file = "temp_inventory_data.txt"
    with open(temp_file, "w") as file:
        file.write("Line\tDate\tProduct Name\tNet Weight (kg)\tPackaging Type\tComment\n")
        for row in data:
            file.write("\t".join(map(str, row)) + "\n")

    # Print the file to the specified printer
    printer_name = "Took_)outNetwork_printer"  # Network printer path
    try:
        win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(
            0,
            "print",
            temp_file,
            None,
            ".",
            0
        )
        messagebox.showinfo("Success", "Data sent to printer successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while printing: {e}")

    # Clean up the temporary file
    os.remove(temp_file)

# Create main window for input
root_input = tk.Tk()
root_input.title("Inventory Input")

# Labels and Entry Widgets
line_label = ttk.Label(root_input, text="Line:")
line_label.grid(row=0, column=0, padx=10, pady=10)
line_var = tk.StringVar(root_input)
line_dropdown = ttk.Combobox(root_input, textvariable=line_var, values=["1", "2", "3", "5", "8", "9", "10", "11", "12", "13", "16", "N/a"])
line_dropdown.grid(row=0, column=1, padx=10, pady=10)

# Date input (Month and Day)
month_label = ttk.Label(root_input, text="Month:")
month_label.grid(row=1, column=0, padx=10, pady=10)
month_var = tk.StringVar(root_input)
month_dropdown = ttk.Combobox(root_input, textvariable=month_var, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
month_dropdown.grid(row=1, column=1, padx=10, pady=10)

day_label = ttk.Label(root_input, text="Day:")
day_label.grid(row=1, column=2, padx=10, pady=10)
day_var = tk.StringVar(root_input)
day_dropdown = ttk.Combobox(root_input, textvariable=day_var, values=[str(i) for i in range(1, 32)])
day_dropdown.grid(row=1, column=3, padx=10, pady=10)

product_name_label = ttk.Label(root_input, text="Product Name:")
product_name_label.grid(row=2, column=0, padx=10, pady=10)
product_name_entry = ttk.Entry(root_input)
product_name_entry.grid(row=2, column=1, padx=10, pady=10)

net_weight_label = ttk.Label(root_input, text="Net Weight (kg):")
net_weight_label.grid(row=3, column=0, padx=10, pady=10)
net_weight_entry = ttk.Entry(root_input)
net_weight_entry.grid(row=3, column=1, padx=10, pady=10)

packaging_label = ttk.Label(root_input, text="Packaging Type:")
packaging_label.grid(row=4, column=0, padx=10, pady=10)
packaging_var = tk.StringVar(root_input)
packaging_dropdown = ttk.Combobox(root_input, textvariable=packaging_var, values=["Roll", "Skid", "Box"])
packaging_dropdown.grid(row=4, column=1, padx=10, pady=10)

comment_label = ttk.Label(root_input, text="Comment:")
comment_label.grid(row=5, column=0, padx=10, pady=10)
comment_entry = tk.Text(root_input, height=4, width=30)
comment_entry.grid(row=5, column=1, padx=10, pady=10)

# Button to submit data and display in second GUI
submit_button = ttk.Button(root_input, text="Submit", command=insert_and_display_data)
submit_button.grid(row=6, column=0, columnspan=4, pady=10)

# Button to clear database (prompt for password)
clear_button = ttk.Button(root_input, text="Clear Database", command=clear_database)
clear_button.grid(row=7, column=0, columnspan=4, pady=10)

# Start the input GUI main loop
root_input.mainloop()
