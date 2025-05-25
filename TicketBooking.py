import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

# Ticket Class
class Ticket:
    def __init__(self, seat_number):
        self.seat_number = seat_number
        self.is_booked = False
        self.booked_by = None

    def book(self, user):
        if not self.is_booked:
            self.is_booked = True
            self.booked_by = user
            return True
        return False

    def cancel(self):
        if self.is_booked:
            self.is_booked = False
            self.booked_by = None
            return True
        return False

# Ticket Booking System Class
class TicketBookingSystem:
    def __init__(self, total_tickets):
        self.tickets = [Ticket(i) for i in range(1, total_tickets + 1)]
        self.lock = threading.Lock()

    def book_ticket(self, seat_number, user):
        self.lock.acquire()
        try:
            if self.tickets[seat_number - 1].book(user):
                return True
            else:
                return False
        finally:
            self.lock.release()

    def cancel_ticket(self, seat_number):
        self.lock.acquire()
        try:
            if self.tickets[seat_number - 1].cancel():
                return True
            else:
                return False
        finally:
            self.lock.release()

    def get_booking_history(self):
        history = []
        for ticket in self.tickets:
            if ticket.is_booked:
                history.append(f"Seat {ticket.seat_number} booked by {ticket.booked_by}")
        return history


class TicketBookingApp:
    def __init__(self, root, total_tickets):
        self.system = TicketBookingSystem(total_tickets)
        self.total_tickets = total_tickets
        self.create_widgets(root)

    def create_widgets(self, root):
        root.title("Ticket Booking System")

        self.buttons = []
        for i in range(1, self.total_tickets + 1):
            btn = tk.Button(root, text=f"Seat {i}", width=10, command=lambda i=i: self.book_or_cancel_seat(i))
            btn.grid(row=(i-1)//5, column=(i-1)%5, padx=10, pady=10)
            self.buttons.append(btn)

        # View History Button
        view_history_btn = tk.Button(root, text="View Booking History", command=self.view_booking_history)
        view_history_btn.grid(row=(self.total_tickets)//5 + 1, columnspan=5, pady=10)

    def book_or_cancel_seat(self, seat_number):
        # Check if the seat is already booked for canceling
        if self.buttons[seat_number - 1]['text'] == "Booked":
            # Ask for confirmation before canceling
            action = messagebox.askquestion("Cancel Booking", f"Are you sure you want to cancel the booking for seat {seat_number}?", icon='question')
            if action == 'yes':  # Cancel booking
                cancel_thread = threading.Thread(target=self.cancel_seat_thread, args=(seat_number,))
                cancel_thread.start()
        else:
            # Proceed with booking if the seat is not booked
            user = simpledialog.askstring("Input", "Enter your name to book the seat")
            if user:
                booking_thread = threading.Thread(target=self.book_seat_thread, args=(seat_number, user))
                booking_thread.start()

    def book_seat_thread(self, seat_number, user):
        success = self.system.book_ticket(seat_number, user)
        if success:
            self.update_button(seat_number, "Booked", disable=False)  # Enable the button ag
            messagebox.showinfo("Success", f"Seat {seat_number} has been booked by {user}!")
        else:
            messagebox.showwarning("Warning", f"Seat {seat_number} is already booked!")

    def cancel_seat_thread(self, seat_number):
        success = self.system.cancel_ticket(seat_number)
        if success:
            self.update_button(seat_number, f"Seat {seat_number}", disable=False)  # Enable the button again
            messagebox.showinfo("Success", f"Booking for seat {seat_number} has been cancelled!")
        else:
            messagebox.showwarning("Warning", f"Seat {seat_number} is not booked yet!")

    def update_button(self, seat_number, text, disable):
        self.buttons[seat_number - 1].config(text=text, state=tk.NORMAL if not disable else tk.DISABLED)

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
    root.mainloop()