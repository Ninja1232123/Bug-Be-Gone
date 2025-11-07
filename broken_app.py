#!/usr/bin/env python3
"""
Deliberately broken app - the classic developer nightmare.

Every error here is common. You've seen them 1000 times.
Watch them disappear in seconds.
"""

import json

def process_user_order(user_id, order_data):
    """Process user order - but it's full of bugs."""

    # Bug 1: KeyError - 'email' key doesn't exist
    user_email = order_data['email']

    # Bug 2: ZeroDivisionError - total_items might be 0
    average_price = order_data['total_price'] / order_data['total_items']

    # Bug 3: IndexError - items list might be empty
    first_item = order_data['items'][0]

    # Bug 4: FileNotFoundError - user preferences file might not exist
    with open(f'user_{user_id}_prefs.json') as f:
        preferences = json.load(f)

    # Bug 5: AttributeError - preferences might be None
    notification_method = preferences.method

    return {
        'user_email': user_email,
        'average_price': average_price,
        'first_item': first_item,
        'notification': notification_method
    }


if __name__ == '__main__':
    # This will crash immediately
    order = {
        'total_price': 100,
        'total_items': 0,  # Zero! Will cause division by zero
        'items': []  # Empty! Will cause index error
    }

    result = process_user_order(12345, order)
    print(f"Order processed: {result}")
