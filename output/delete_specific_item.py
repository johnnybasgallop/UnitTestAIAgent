```python
import requests
import json

# Make a GET request to the items endpoint with the appropriate arguments
response = requests.get("https://api.example.com/items", params={"name": "My Item"})

# Parse the JSON response and extract the item ID
data = json.loads(response.text)
item_id = data["items"][0]["id"]

# Make a DELETE request to the /items/{id} endpoint with the item ID
response = requests.delete(f"https://api.example.com/items/{item_id}")
```