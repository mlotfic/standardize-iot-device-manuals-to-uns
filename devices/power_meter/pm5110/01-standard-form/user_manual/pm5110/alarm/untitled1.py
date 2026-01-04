# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 08:44:00 2026

@author: User
"""

import json

file_path = 'available_alarms.json'

try:
    with open(file_path, 'r', encoding='utf-8') as file_handle:
        data = json.load(file_handle)
    
    # You can now work with the data, which is a Python dictionary or list
    for item in data:
        for key, value in item.items():
            if key == "label":
                print(value)

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from the file '{file_path}'. Check file format.")
except UnicodeDecodeError:
    print(f"Error: Unable to decode the file using utf-8. Please check the file's actual encoding.")
