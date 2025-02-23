
import requests

item_id = 1 # Replace with the desired item ID
url = 'http://localhost:5000/items' + str(item_id)
response = requests.get(url)
if response.status_code == 200:
    item = response.json()
    print(f"Item {item_id} found: {item}")
else:
    print("Item not found.")
