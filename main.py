# main.py — Entry point for Job Portal Management System
# Run this file to start the application: python main.py

import tkinter as tk
from tkinter import messagebox
from database import test_connection


def main():
    # Quick DB connectivity check before launching UI
    if not test_connection():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Connection Failed",
            "Could not connect to MySQL database!\n\n"
            "Please follow these steps:\n\n"
            "1. Make sure MySQL Server is running\n"
            "2. Open 'database.py' and set your credentials:\n"
            "     user     = 'root'  (your MySQL username)\n"
            "     password = ''      (your MySQL password)\n\n"
            "3. Open MySQL Workbench and run:\n"
            "     database/jobportal.sql\n\n"
            "4. Then run main.py again"
        )
        root.destroy()
        return

    from login import LoginWindow
    LoginWindow()


if __name__ == "__main__":
    main()
