import random
from datetime import datetime, timezone, timedelta


def generate_otp():
    return str(random.randint(100000, 999999))


def get_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=5)
