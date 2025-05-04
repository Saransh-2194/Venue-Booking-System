#!/usr/bin/env python3
"""
Storage Module - For handling data operations
Part of the Venue Booking System
"""

import os
import pandas as pd
from datetime import datetime
import warnings

class BookingStorage:
    """A class to handle reading from and writing to the booking data store"""
    
    def __init__(self):
        self.bookings_file = "bookings.csv"
        self.logs_file = "booking_log.csv"
        
        # Initialize bookings file if it doesn't exist
        if not os.path.exists(self.bookings_file):
            # Create a DataFrame with the required columns
            columns = [
                'id', 'club', 'event_name', 'contact_email', 'day', 'date', 
                'time_slot', 'venue', 'expected_attendance', 'purpose',
                'status', 'submitted_at', 'processed_at', 'admin_comment'
            ]
            pd.DataFrame(columns=columns).to_csv(self.bookings_file, index=False)
        
        # Initialize logs file if it doesn't exist
        if not os.path.exists(self.logs_file):
            columns = [
                'time', 'club', 'venue', 'status', 'day', 'date', 
                'time_slot', 'event', 'admin_comment'
            ]
            pd.DataFrame(columns=columns).to_csv(self.logs_file, index=False)

    def load_bookings(self):
        """Load all bookings from the CSV file"""
        try:
            return pd.read_csv(self.bookings_file)
        except Exception as e:
            print(f"Error reading bookings file: {e}")
            # Create a new DataFrame with the required columns
            columns = [
                'id', 'club', 'event_name', 'contact_email', 'day', 'date', 
                'time_slot', 'venue', 'expected_attendance', 'purpose',
                'status', 'submitted_at', 'processed_at', 'admin_comment'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.bookings_file, index=False)
            return df

    def save_bookings(self, bookings_df):
        """Save bookings back to the CSV file"""
        try:
            bookings_df.to_csv(self.bookings_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving bookings: {e}")
            return False

    def load_logs(self):
        """Load all logs from the CSV file"""
        try:
            return pd.read_csv(self.logs_file)
        except Exception as e:
            print(f"Error reading logs file: {e}")
            # Create a new DataFrame with the required columns
            columns = [
                'time', 'club', 'venue', 'status', 'day', 'date', 
                'time_slot', 'event', 'admin_comment'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.logs_file, index=False)
            return df

    def add_log(self, log_entry):
        """Add a new log entry to the CSV file"""
        try:
            logs_df = self.load_logs()
            logs_df = pd.concat([logs_df, pd.DataFrame([log_entry])], ignore_index=True)
            logs_df.to_csv(self.logs_file, index=False)
            return True
        except Exception as e:
            print(f"Error adding log entry: {e}")
            return False

    def save_request(self, request):
        """Save a new booking request"""
        try:
            bookings_df = self.load_bookings()
            
            # Generate a new ID
            if len(bookings_df) > 0:
                try:
                    new_id = int(bookings_df['id'].max()) + 1
                except:
                    new_id = len(bookings_df) + 1
            else:
                new_id = 1
                
            # Add metadata
            request['id'] = new_id
            request['status'] = 'Pending'
            request['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            request['processed_at'] = None
            request['admin_comment'] = None
            
            # Add to dataframe and save
            bookings_df = pd.concat([bookings_df, pd.DataFrame([request])], ignore_index=True)
            self.save_bookings(bookings_df)
            
            # Add log entry
            log_entry = {
                'time': request['submitted_at'],
                'club': request['club'],
                'venue': request['venue'],
                'status': 'Submitted',
                'day': request['day'],
                'date': request['date'],
                'time_slot': request['time_slot'],
                'event': request['event_name'],
                'admin_comment': ''
            }
            self.add_log(log_entry)
            
            return new_id
            
        except Exception as e:
            print(f"Error saving request: {e}")
            return None

    def update_request_status(self, request_id, status, admin_comment=''):
        """Update the status of a request"""
        try:
            bookings_df = self.load_bookings()
            
            # Find the request
            request_idx = bookings_df.index[bookings_df['id'] == request_id].tolist()
            if not request_idx:
                print(f"Request ID {request_id} not found.")
                return False
                
            # Update the request
            processed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            bookings_df.loc[request_idx[0], 'status'] = status
            bookings_df.loc[request_idx[0], 'processed_at'] = processed_time
            bookings_df['admin_comment'] = bookings_df['admin_comment'].astype(object)
            bookings_df.loc[request_idx[0], 'admin_comment'] = admin_comment
            
            # Save changes
            self.save_bookings(bookings_df)
            
            # Add log entry
            request_row = bookings_df.loc[request_idx[0]]
            log_entry = {
                'time': processed_time,
                'club': request_row['club'],
                'venue': request_row['venue'],
                'status': status,
                'day': request_row['day'],
                'date': request_row['date'],
                'time_slot': request_row['time_slot'],
                'event': request_row['event_name'],
                'admin_comment': admin_comment
            }
            self.add_log(log_entry)
            
            return True
            
        except Exception as e:
            print(f"Error updating request status: {e}")
            return False

    def get_pending_requests(self):
        """Get all pending requests"""
        try:
            bookings_df = self.load_bookings()
            return bookings_df[bookings_df['status'] == 'Pending']
        except Exception as e:
            print(f"Error getting pending requests: {e}")
            return pd.DataFrame()

    def get_all_bookings(self):
        """Get all bookings"""
        return self.load_bookings()

    def get_club_bookings(self, club_name):
        """Get all bookings for a specific club"""
        try:
            bookings_df = self.load_bookings()
            return bookings_df[bookings_df['club'] == club_name]
        except Exception as e:
            print(f"Error getting club bookings: {e}")
            return pd.DataFrame()

    def check_venue_availability(self, venue_name, date, time_slot):
        """Check if a venue is available for a given date and time slot"""
        try:
            bookings_df = self.load_bookings()
            
            # Filter relevant bookings
            venue_bookings = bookings_df[
                (bookings_df['venue'] == venue_name) & 
                (bookings_df['date'] == date) & 
                (bookings_df['status'].isin(['Pending', 'Approved']))
            ]
            
            if venue_bookings.empty:
                return True
                
            # Parse time slot
            start_new, end_new = [datetime.strptime(t, "%H:%M").time() for t in time_slot.split("-")]
            
            # Check for conflicts
            for _, booking in venue_bookings.iterrows():
                booked_slot = booking['time_slot']
                start_booked, end_booked = [datetime.strptime(t, "%H:%M").time() 
                                         for t in booked_slot.split("-")]
                
                # Check for overlap
                if start_new < end_booked and end_new > start_booked:
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error checking venue availability: {e}")
            return False

    def get_conflicting_bookings(self, venue_name, date, time_slot, exclude_id=None):
        """Get all conflicting bookings for a given venue, date and time slot"""
        try:
            bookings_df = self.load_bookings()
            
            # Filter relevant bookings
            venue_bookings = bookings_df[
                (bookings_df['venue'] == venue_name) & 
                (bookings_df['date'] == date) & 
                (bookings_df['status'].isin(['Pending', 'Approved']))
            ]
            
            if exclude_id is not None:
                venue_bookings = venue_bookings[venue_bookings['id'] != exclude_id]
            
            if venue_bookings.empty:
                return pd.DataFrame()
                
            # Parse time slot
            start_new, end_new = [datetime.strptime(t, "%H:%M").time() for t in time_slot.split("-")]
            
            # Find conflicts
            conflicts = []
            for _, booking in venue_bookings.iterrows():
                booked_slot = booking['time_slot']
                start_booked, end_booked = [datetime.strptime(t, "%H:%M").time() 
                                         for t in booked_slot.split("-")]
                
                # Check for overlap
                if start_new < end_booked and end_new > start_booked:
                    conflicts.append(booking)
                    
            return pd.DataFrame(conflicts) if conflicts else pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting conflicting bookings: {e}")
            return pd.DataFrame()

    def get_booking_by_id(self, booking_id):
        """Get a specific booking by ID"""
        try:
            bookings_df = self.load_bookings()
            booking = bookings_df[bookings_df['id'] == booking_id]
            return booking.iloc[0] if not booking.empty else None
        except Exception as e:
            print(f"Error getting booking by ID: {e}")
            return None