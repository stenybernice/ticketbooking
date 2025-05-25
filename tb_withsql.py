import mysql.connector
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from mysql.connector import Error
import time

# Ticket Booking System Class
class TicketBookingSystem:
    def __init__(self, total_tickets):
        self.total_tickets = total_tickets
        self.lock = threading.Lock()
        self.connect_to_database()
        self.initialize_tickets()

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host='127.0.0.1',
                database='Osproject',
                user='root',  # Replace with your MySQL username
                password='password'  # Replace with your MySQL password
            )
            if self.connection.is_connected():
                print("Connected to MySQL Database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def initialize_tickets(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM tickets")
        count = cursor.fetchone()[0]

        if count == 0:  # If no tickets exist, initialize the table
            cursor.executemany("INSERT INTO tickets (seat_number) VALUES (%s)", [(i,) for i in range(1, self.total_tickets + 1)])
            self.connection.commit()

    def book_ticket(self, seat_number, user):
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT is_booked FROM tickets WHERE seat_number = %s", (seat_number,))
            is_booked = cursor.fetchone()[0]
            if not is_booked:
                cursor.execute("UPDATE tickets SET is_booked = %s, booked_by = %s WHERE seat_number = %s",
                               (True, user, seat_number))
                self.connection.commit()
                return True
            else:
                return False
        finally:
            self.lock.release()

    def cancel_ticket(self, seat_number):
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT is_booked FROM tickets WHERE seat_number = %s", (seat_number,))
            is_booked = cursor.fetchone()[0]
            if is_booked:
                cursor.execute("UPDATE tickets SET is_booked = %s, booked_by = NULL WHERE seat_number = %s",
                               (False, seat_number))
                self.connection.commit()
                return True
            else:
                return False
        finally:
            self.lock.release()

    def reset_all_bookings(self):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE tickets SET is_booked = %s, booked_by = NULL", (False,))
        self.connection.commit()

    def get_booking_history(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT seat_number, booked_by FROM tickets WHERE is_booked = %s", (True,))
        history = cursor.fetchall()
        return [f"Seat {seat_number} booked by {booked_by}" for seat_number, booked_by in history]

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")

    # New function to continuously fetch and display ticket data
    def continuously_fetch_tickets(self):
        cursor = self.connection.cursor()
        while True:
            cursor.execute("SELECT * FROM tickets")
            tickets = cursor.fetchall()
            print("\nCurrent Ticket Status:")
            for ticket in tickets:
                print(ticket)
            time.sleep(5)  # Pause for 5 seconds before fetching data again


# GUI Application for Ticket Booking
class TicketBookingApp:
    def __init__(self, root, total_tickets):
        self.system = TicketBookingSystem(total_tickets)
        self.total_tickets = total_tickets
        self.create_widgets(root)
        # Start a thread to continuously fetch and display ticket data
        threading.Thread(target=self.system.continuously_fetch_tickets, daemon=True).start()

    def create_widgets(self, root):
        root.title("Ticket Booking System")

        self.buttons = []
        for i in range(1, self.total_tickets + 1):
            btn = tk.Button(root, text=f"Seat {i}", width=10, command=lambda i=i: self.book_or_cancel_seat(i))
            btn.grid(row=(i-1)//5, column=(i-1)%5, padx=10, pady=10)
            self.buttons.append(btn)

        # View History Button
        view_history_btn = tk.Button(root, text="View Booking History", command=self.view_booking_history)
        view_history_btn.grid(row=(self.total_tickets)//5 + 1, column=0, columnspan=2, pady=10)

        # Reset Button
        reset_btn = tk.Button(root, text="Reset All Bookings", command=self.reset_all_bookings)
        reset_btn.grid(row=(self.total_tickets)//5 + 1, column=3, columnspan=2, pady=10)

    def book_or_cancel_seat(self, seat_number):
        if self.buttons[seat_number - 1]['text'] == "Booked":
            action = messagebox.askquestion("Cancel Booking", f"Are you sure you want to cancel the booking for seat {seat_number}?", icon='question')
            if action == 'yes':
                cancel_thread = threading.Thread(target=self.cancel_seat_thread, args=(seat_number,))
                cancel_thread.start()
        else:
            user = simpledialog.askstring("Input", "Enter your name to book the seat")
            if user:
                booking_thread = threading.Thread(target=self.book_seat_thread, args=(seat_number, user))
                booking_thread.start()

    def book_seat_thread(self, seat_number, user):
        success = self.system.book_ticket(seat_number, user)
        root.after(0, self.update_ui_after_booking, seat_number, user, success)

    def update_ui_after_booking(self, seat_number, user, success):
        if success:
            self.update_button(seat_number, "Booked", disable=False)
            messagebox.showinfo("Success", f"Seat {seat_number} has been booked by {user}!")
        else:
            messagebox.showwarning("Warning", f"Seat {seat_number} is already booked!")

    def cancel_seat_thread(self, seat_number):
        success = self.system.cancel_ticket(seat_number)
        root.after(0, self.update_ui_after_cancellation, seat_number, success)

    def update_ui_after_cancellation(self, seat_number, success):
        if success:
            self.update_button(seat_number, f"Seat {seat_number}", disable=False)
            messagebox.showinfo("Success", f"Booking for seat {seat_number} has been cancelled!")
        else:
            messagebox.showwarning("Warning", f"Seat {seat_number} is not booked yet!")

    def update_button(self, seat_number, text, disable):
        self.buttons[seat_number - 1].config(text=text, state=tk.NORMAL if not disable else tk.DISABLED)

    def reset_all_bookings(self):
        reset_confirmation = messagebox.askquestion("Reset All", "Are you sure you want to reset all bookings?", icon='warning')
        if reset_confirmation == 'yes':
            reset_thread = threading.Thread(target=self.reset_all_bookings_thread)
            reset_thread.start()

    def reset_all_bookings_thread(self):
        self.system.reset_all_bookings()
        root.after(0, self.update_ui_after_reset)

    def update_ui_after_reset(self):
        for i in range(1, self.total_tickets + 1):
            self.update_button(i, f"Seat {i}", disable=False)
        messagebox.showinfo("Success", "All bookings have been reset!")

    def view_booking_history(self):
        history = self.system.get_booking_history()
        if history:
            messagebox.showinfo("Booking History", "\n".join(history))
        else:
            messagebox.showinfo("Booking History", "No bookings have been made yet.")


# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = TicketBookingApp(root, 20)  # Create a ticket booking system with 20 seats

    def on_closing():
        app.system.close_connection()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
