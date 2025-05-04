# 📅 Venue Booking Simulation System

A Discrete Event Simulation (DES) project that models a venue booking system for an academic institution. This simulation helps identify and solve issues such as double bookings, administrative delays, and inefficient communication between clubs and the admin.

## 🔍 Overview

This Python-based project simulates a venue booking system where clubs request venues, the system checks for availability, and an admin decides to approve or reject requests. Notifications are simulated using SMTP, and conflict detection is built-in.

## 🎯 Features

- Simulates realistic venue booking and approval workflow
- Detects and prevents double bookings
- Modular OOP design for ease of extension
- Real-time admin interaction through console

## ⚙️ Technologies Used

- **Python 3.x**
- `pandas` – working with data and files
- `datetime` – Time-based simulation of booking slots
- `random` – (Optional) Future use for request variability
- `os` – For accessing files

## 🧱 System Architecture

- **Club Module:** Initiates booking requests
- **Venue Module:** Maintains schedule and checks availability
- **Admin Module:** Approves or rejects requests


## 📝 How to Run

1. Clone the repository.
2. Open the simulation script in VS Code or Jupyter Notebook.
3. Run the script and follow command-line prompts to simulate bookings.

## 🚀 Future Enhancements

- Web-based frontend using React
- Admin dashboard for real-time management
- Integration with Flask/Node.js backend

## 🙌 Acknowledgements

Thanks to Prof. Pardeep Garg for guidance and JUIT Solan's ECE Department for support. Peer collaboration during testing also helped shape this project.

---



