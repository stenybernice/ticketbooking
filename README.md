# ticketbooking
This Python application is a GUI-based ticket booking system built with Tkinter for the user interface, MySQL for persistent storage, and threading for safe concurrent operations.
 It allows users to book or cancel seats, view booking history, and reset all bookings, all while ensuring data integrity using locks. The backend connects to a MySQL database (Osproject) and stores seat data in a tickets table, tracking each seat’s booking status and the user who reserved it. The system also features a background thread that continuously monitors and prints the current ticket status to the console, simulating a real-time feed. It's an ideal mini-project for learning GUI development, database integration, and thread-safe programming in Python.

