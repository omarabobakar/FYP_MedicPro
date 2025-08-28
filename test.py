from datetime import datetime, timedelta

def get_next_weekday(weekday_name):
    # Define a dictionary to convert weekday names to numbers
    weekdays = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    # Get the current date
    today = datetime.now()
    
    # Get the current weekday as a number
    current_weekday = today.weekday()
    
    # Get the target weekday as a number
    target_weekday = weekdays[weekday_name]
    
    # Calculate days until the next occurrence of the target weekday
    days_until_next = (target_weekday - current_weekday + 7) % 7
    if days_until_next == 0:
        days_until_next = 7
    
    # Calculate the date of the next occurrence of the target weekday
    next_weekday_date = today + timedelta(days=days_until_next)
    
    # Return the date as a string
    return next_weekday_date.strftime('%Y-%m-%d')

# Example usage
day_name = input("Enter the name of the day: ")
next_date = get_next_weekday(day_name)
print(f"The next {day_name} will be on {next_date}.")