class Booking:
    def __init__(self, customer_name, email, adventure_type, booking_date):
        self.customer_name = customer_name
        self.email = email
        self.adventure_type = adventure_type
        self.booking_date = booking_date

    def to_dict(self):
        return {
            "customer_name": self.customer_name,
            "email": self.email,
            "adventure_type": self.adventure_type,
            "booking_date": self.booking_date
        }
