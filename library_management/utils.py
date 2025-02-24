from datetime import datetime

def calculate_rent_fee(issue_date, return_date):
    duration = (return_date - issue_date).days
    return duration * 10

