from django.test import TestCase
from datetime import date, datetime, timedelta


class XeroTestCase(TestCase):
    # Disable saturday/sunday for delivery
    days_disabled = [0, 6]
    # Set the selectable dates to start 3 days away from today
    min_date = date.today() + timedelta(days=3)

    t1 = datetime.now().replace(hour=14, minute=30, second=0, microsecond=0);

    if t1.time() < datetime.now().time():
        print("T1 is less than datetime.now()")

    if t1.time() > datetime.now().time():
        print("T1 time is greater than datetime.now()")

    print(datetime.today().weekday())

    print(t1)
    print(datetime.now().time())