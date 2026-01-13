from collections import defaultdict

CACHE = defaultdict(
    lambda: {
        "weight": 0,
        "height": 0,
        "age": 0,
        "activity_level": 0,
        "city": "Doesn't set",
        "target_calories": 0,
        "target_water": 0,
        "burned_calories": 0,
        "current_calories": 0,
        "current_water": 0,
        "current_temp": None,
        "log_water": list(),
        "log_calories": list(),
    }
)

PRODUCT_CACHE = dict()
