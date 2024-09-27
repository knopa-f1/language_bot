import json

# Load dict from JSON file
def load_dict(file_name:str):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save dict to JSON file
def save_dict(date_dict:dict, file_name:str):
    with open(file_name, "w") as file:
        json.dump(date_dict, file, indent=4)

