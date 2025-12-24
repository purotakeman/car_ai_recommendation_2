from app import utility_processor
import pandas as pd

def test_format_currency():
    utils = utility_processor()
    format_currency = utils['format_currency']
    
    test_cases = [
        (5100000, "510"),
        ("5100000~10650000", "510～1,065"),
        (43500, "43,500"),
        (250, "250"),
        ("250~300", "250～300"),
        (None, "0"),
        ("", "0")
    ]
    
    print("Testing format_currency:")
    for val, expected in test_cases:
        result = format_currency(val)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {val} -> Result: {result} (Expected: {expected})")

if __name__ == "__main__":
    test_format_currency()
