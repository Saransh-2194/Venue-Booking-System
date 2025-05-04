import sys
import pandas as pd
from datetime import datetime
from storage import BookingStorage


class AdminPortal:
    def __init__(self):
        self.storage = BookingStorage()

    def display_pending_requests(self):
        """Display all pending booking requests"""
        pending_requests = self.storage.get_pending_requests()
        
        if pending_requests.empty:
            print("\nNo pending booking requests.")
            return None
        
        print("\n===== Pending Booking Requests =====")
        for i, (_, req) in enumerate(pending_requests.iterrows(), 1):
            print(f"\n[{i}] Request ID: {req['id']}")
            print(f"Club: {req['club']}")
            print(f"Event: {req['event_name']}")
            print(f"Venue: {req['venue']}")
            print(f"Date: {req['date']} ({req['day']})")
            print(f"Time: {req['time_slot']}")
            print(f"Expected Attendance: {req['expected_attendance']}")
            print(f"Purpose: {req['purpose']}")
            print(f"Contact: {req['contact_email']}")
            print(f"Submitted: {req['submitted_at']}")
            print("-" * 40)
            
        return pending_requests

    def process_request(self, request_index, pending_requests):
        """Process a single booking request"""
        if pending_requests is None or pending_requests.empty or request_index < 0 or request_index >= len(pending_requests):
            print("Invalid request index.")
            return
            
        request = pending_requests.iloc[request_index]
        print(f"\n===== Processing Request ID: {request['id']} =====")
        print(f"Club: {request['club']}")
        print(f"Event: {request['event_name']}")
        print(f"Venue: {request['venue']} on {request['date']} ({request['day']}) at {request['time_slot']}")
        
        # Check for conflicts
        conflicts = self.storage.get_conflicting_bookings(
            request['venue'], request['date'], request['time_slot'], exclude_id=request['id']
        )
        
        if not conflicts.empty:
            print("\n⚠️ WARNING: This request conflicts with the following approved/pending bookings:")
            for i, (_, conflict) in enumerate(conflicts.iterrows(), 1):
                status_marker = "✅" if conflict['status'] == "Approved" else "⏳"
                print(f"{i}. {status_marker} {conflict['club']} - {conflict['event_name']} - {conflict['time_slot']}")
        
        # Get admin decision
        while True:
            decision = input("\nApprove this request? (a=approve, r=reject): ").lower()
            if decision in ['a', 'r']:
                break
            print("Invalid choice. Please enter 'a' for approve or 'r' for reject.")
        
        # Get admin comment
        admin_comment = input("Enter any comments (optional): ")
        
        # Process decision
        status = "Approved" if decision == 'a' else "Rejected"
        success = self.storage.update_request_status(request['id'], status, admin_comment)
        
        if success:
            if status == "Approved":
                print(f"\n✅ Request ID {request['id']} has been approved.")
            else:
                print(f"\n❌ Request ID {request['id']} has been rejected.")
        else:
            print(f"\n❌ Failed to update request status. Please try again.")

    def view_booking_log(self):
        """View the booking log"""
        logs_df = self.storage.load_logs()
        
        if logs_df.empty:
            print("No booking logs available.")
            return
            
        print("\n===== Booking Log =====")
        # Format the dataframe for display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 120)
        print(logs_df)
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')

    def view_all_bookings(self):
        """View all bookings (approved, rejected, and pending)"""
        bookings_df = self.storage.get_all_bookings()
        
        if bookings_df.empty:
            print("No booking requests found.")
            return
            
        # Group by status
        status_groups = {status: group for status, group in bookings_df.groupby('status')}
            
        # Display by status
        for status, group_df in status_groups.items():
            if not group_df.empty:
                print(f"\n===== {status} Bookings =====")
                for _, booking in group_df.iterrows():
                    status_icon = "✅" if status == "Approved" else "❌" if status == "Rejected" else "⏳"
                    print(f"{status_icon} [{booking['id']}] {booking['club']} - {booking['event_name']}")
                    print(f"    Venue: {booking['venue']} on {booking['date']} ({booking['day']}) at {booking['time_slot']}")
                    if pd.notna(booking['admin_comment']) and booking['admin_comment']:
                        print(f"    Comment: {booking['admin_comment']}")
                    print()

    def run(self):
        """Main menu for the Admin Portal"""
        print("\n===== Admin Venue Booking Portal =====")
        
        while True:
            print("\n===== Admin Portal Menu =====")
            print("1. Process Pending Booking Requests")
            print("2. View All Bookings")
            print("3. View Booking Log")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                pending_requests = self.display_pending_requests()
                if pending_requests is not None and not pending_requests.empty:
                    while True:
                        request_idx = input("\nEnter the number of the request to process (or 'q' to go back): ")
                        if request_idx.lower() == 'q':
                            break
                        try:
                            idx = int(request_idx) - 1  # Convert to 0-based index
                            self.process_request(idx, pending_requests)
                            # Refresh the list after processing
                            pending_requests = self.storage.get_pending_requests()
                            if pending_requests.empty:
                                print("No more pending requests.")
                                break
                            else:
                                # Show remaining requests
                                print("\nRemaining pending requests:")
                                for i, (_, req) in enumerate(pending_requests.iterrows(), 1):
                                    print(f"[{i}] ID: {req['id']} - {req['club']} - {req['event_name']} - {req['venue']}")
                        except ValueError:
                            print("Please enter a valid number.")
            
            elif choice == "2":
                self.view_all_bookings()
            
            elif choice == "3":
                self.view_booking_log()
            
            elif choice == "4":
                print("Thank you for using the Admin Portal. Goodbye!")
                sys.exit(0)
            
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    portal = AdminPortal()
    portal.run()