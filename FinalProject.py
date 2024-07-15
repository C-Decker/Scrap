import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to handle button click, insert data into database, and display data in the second GUI
def insert_and_display_data():
    # Get values from GUI fields
    line = line_var.get()
    product_name = product_name_entry.get()
    net_weight = net_weight_entry.get()
    packaging_type = packaging_var.get()
    comment = comment_entry.get("1.0", tk.END)  # Get text from comment Text widget

    # Insert into SQLite database
    conn = sqlite3.connect('inventory.db')  # Connect to or create SQLite database file
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (line TEXT, product_name TEXT, net_weight REAL, packaging_type TEXT, comment TEXT)''')
    c.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?)", (line, product_name, net_weight, packaging_type, comment))
    conn.commit()

    # Close connection
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
    data_listbox = ttk.Treeview(root_display, columns=("Line", "Product Name", "Net Weight (kg)", "Packaging Type", "Comment"), show="headings")
    data_listbox.heading("Line", text="Line")
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

    # Function to start the display GUI main loop
    def start_display_gui():
        root_display.mainloop()

    # Call the function to start displaying the GUI
    start_display_gui()

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

# Function to send email with data
def send_email():
    # Get selected email addresses from dropdown
    selected_emails = email_listbox.curselection()
    if not selected_emails:
        messagebox.showerror("Error", "Please select at least one email address.")
        return

    # Get data from SQLite database
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    rows = c.fetchall()
    conn.close()

    # Prepare email content
    email_content = "\n".join([f"Line: {row[0]}, Product Name: {row[1]}, Net Weight: {row[2]} kg, Packaging Type: {row[3]}, Comment: {row[4]}" for row in rows])

    # Set up email parameters
    sender_email = 'your_email@example.com'  # Replace with your email address
    sender_password = 'your_password'  # Replace with your email password
    smtp_server = 'smtp.example.com'  # Replace with your SMTP server address
    smtp_port = 587  # Replace with your SMTP port number

    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(email_listbox.get(idx) for idx in selected_emails)
    msg['Subject'] = 'Inventory Data'

    # Add email body
    msg.attach(MIMEText(email_content, 'plain'))

    try:
        # Log in to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
        messagebox.showinfo("Success", "Email sent successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while sending email: {e}")

# Create main window for input
root_input = tk.Tk()
root_input.title("Inventory Input")

# Labels and Entry Widgets
line_label = ttk.Label(root_input, text="Line:")
line_label.grid(row=0, column=0, padx=10, pady=10)
line_var = tk.StringVar(root_input)
line_dropdown = ttk.Combobox(root_input, textvariable=line_var, values=["1", "2", "3", "5", "8", "9", "10", "11", "12", "13", "16", "N/a"])
line_dropdown.grid(row=0, column=1, padx=10, pady=10)

product_name_label = ttk.Label(root_input, text="Product Name:")
product_name_label.grid(row=1, column=0, padx=10, pady=10)
product_name_entry = ttk.Entry(root_input)
product_name_entry.grid(row=1, column=1, padx=10, pady=10)

net_weight_label = ttk.Label(root_input, text="Net Weight (kg):")
net_weight_label.grid(row=2, column=0, padx=10, pady=10)
net_weight_entry = ttk.Entry(root_input)
net_weight_entry.grid(row=2, column=1, padx=10, pady=10)

packaging_label = ttk.Label(root_input, text="Packaging Type:")
packaging_label.grid(row=3, column=0, padx=10, pady=10)
packaging_var = tk.StringVar(root_input)
packaging_dropdown = ttk.Combobox(root_input, textvariable=packaging_var, values=["Roll", "Skid", "Box"])
packaging_dropdown.grid(row=3, column=1, padx=10, pady=10)

comment_label = ttk.Label(root_input, text="Comment:")
comment_label.grid(row=4, column=0, padx=10, pady=10)
comment_entry = tk.Text(root_input, height=4, width=30)
comment_entry.grid(row=4, column=1, padx=10, pady=10)

# Email addresses listbox and scrollbar
email_label = ttk.Label(root_input, text="Select Email Addresses:")
email_label.grid(row=5, column=0, padx=10, pady=10)
email_listbox = tk.Listbox(root_input, selectmode=tk.MULTIPLE, height=3)
email_listbox.grid(row=5, column=1, padx=10, pady=10)
# Add sample email addresses
sample_emails = ["recipient1@example.com", "recipient2@example.com", "recipient3@example.com"]
for email in sample_emails:
    email_listbox.insert(tk.END, email)

# Button to submit data and display in second GUI
submit_button = ttk.Button(root_input, text="Submit", command=insert_and_display_data)
submit_button.grid(row=6, column=0, columnspan=2, pady=10)

# Button to clear database (prompt for password)
clear_button = ttk.Button(root_input, text="Clear Database", command=clear_database)
clear_button.grid(row=7, column=0, columnspan=2, pady=10)

# Button to send email with data
send_email_button = ttk.Button(root_input, text="Send Email", command=send_email)
send_email_button.grid(row=8, column=0, columnspan=2, pady=10)

# Start the input GUI main loop
root_input.mainloop()
