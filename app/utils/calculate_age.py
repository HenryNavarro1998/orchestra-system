from datetime import date

def calculate_age(born_date):
    today = date.today()
    age = today.year - born_date.year - (
        (today.month, today.day) < (born_date.month, born_date.day)
    )
    return age