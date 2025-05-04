#!/usr/bin/env python3
"""
Club Portal - For venue booking submissions
Part of the Venue Booking System
"""

from datetime import datetime
import re
import sys
import pandas as pd
from storage import BookingStorage

class ClubPortal:
    def __init__(self):
        self.storage = BookingStorage()
        
        # Define venue data
        self.venues = {
            "Auditorium": {"category": "Auditorium", "capacity": 1000},
            "LT-1": {"category": "Lecture Theatre", "capacity": 300},
            "LT-2": {"category": "Lecture Theatre", "capacity": 250},
            "CR-1": {"category": "Conference Room", "capacity": 100},
            "CR-2": {"category": "Conference Room", "capacity": 50},
            "Sports Hall": {"category": "Sports", "capacity": 500}
        }
        
        # Group venues by category
        self.categories = {}
        for venue_name, details in self.venues.items():
            category = details["category"]
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(venue_name)

    def suggest_available_venues(self, date, time_slot):
        """Suggest venues available for a given date and time slot across all categories."""
        available_venues = {}
        for category, venue_list in self.categories.items():
            available_venues[category] = []
            for venue in venue_list:
                if self.storage.check_venue_availability(venue, date, time_slot):
                    available_venues[category].append(venue)
        return available_venues

    def submit_booking_request(self):
        """Interactive CLI for submitting a booking request"""
        print("\n===== Club Venue Booking Portal =====\n")
        
        # Get club information
        club_name = input("Enter club name: ")
        event_name = input("Enter event name: ")
        contact_email = input("Enter contact email: ")
        
        # Get day and date
        day = input("Enter day of event (e.g. Monday): ")
        while True:
            date_input = input("Enter date of event (YYYY-MM-DD): ")
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Please enter in YYYY-MM-DD format.")
        
        # Get time slot
        while True:
            time_slot = input("Enter time slot (e.g. 09:00-11:00): ")
            if re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', time_slot):
                try:
                    start, end = time_slot.split('-')
                    datetime.strptime(start, "%H:%M")
                    datetime.strptime(end, "%H:%M")
                    break
                except ValueError:
                    print("Invalid time format.")
            else:
                print("Format should be HH:MM-HH:MM.")
        
        # Show available venues
        available_venues = self.suggest_available_venues(date_input, time_slot)
        print("\nAvailable venues:")
        
        has_venues = False
        for category, venues in available_venues.items():
            if venues:
                has_venues = True
                print(f"{category}: {', '.join(venues)}")
        
        if not has_venues:
            print("No venues available for the selected date and time slot.")
            return
        
        # Get venue selection
        while True:
            venue_name = input("\nSelect a venue from the above list: ")
            valid_venues = [v for category_venues in available_venues.values() for v in category_venues]
            if venue_name in valid_venues:
                break
            else:
                print("Invalid venue. Please select from the available venues.")
        
        # Get expected attendance
        while True:
            try:
                expected_attendance = int(input("Enter expected attendance: "))
                if expected_attendance <= 0:
                    print("Expected attendance must be a positive number.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        # Additional details
        purpose = input("Enter purpose of the event: ")
        
        # Create request
        request = {
            "club": club_name,
            "event_name": event_name,
            "contact_email": contact_email,
            "day": day,
            "date": date_input,
            "time_slot": time_slot,
            "venue": venue_name,
            "expected_attendance": expected_attendance,
            "purpose": purpose
        }
        
        # Save request
        request_id = self.storage.save_request(request)
        
        if request_id:
            print(f"\n✅ Booking request submitted successfully! Request ID: {request_id}")
            print("Your request is pending admin approval. Check back later for status updates.")
        else:
            print("\n❌ Failed to submit booking request. Please try again.")

    def view_club_bookings(self):
        """View all bookings for a club"""
        club_name = input("Enter club name to view bookings: ")
        club_bookings = self.storage.get_club_bookings(club_name)
        
        if club_bookings.empty:
            print(f"No booking requests found for {club_name}.")
            return
        
        print(f"\n===== Booking Requests for {club_name} =====")
        for _, booking in club_bookings.iterrows():
            status_icon = "✅" if booking["status"] == "Approved" else "❌" if booking["status"] == "Rejected" else "⏳"
            print(f"ID: {booking['id']} | {status_icon} {booking['status']}")
            print(f"Event: {booking['event_name']}")
            print(f"Venue: {booking['venue']} on {booking['date']} ({booking['day']}) at {booking['time_slot']}")
            if pd.notna(booking["admin_comment"]) and booking["admin_comment"]:
                print(f"Admin Comment: {booking['admin_comment']}")
            print("-" * 40)

    def run(self):
        """Main menu for the Club Portal"""
        while True:
            print("\n===== Club Portal Menu =====")
            print("1. Submit New Booking Request")
            print("2. View My Club's Bookings")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                self.submit_booking_request()
            elif choice == "2":
                self.view_club_bookings()
            elif choice == "3":
                print("Thank you for using the Club Portal. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    portal = ClubPortal()
    portal.run()