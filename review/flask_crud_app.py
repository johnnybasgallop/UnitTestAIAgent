"""
This module provides a simple Flask application that allows for basic CRUD operations
on an in-memory list of items. It supports creating, reading, updating, and deleting
items via HTTP requests.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory "database" for simplicity
items = []

# Create
@app.route("/items", methods=["POST"])
def create_item():
    """Creates a new item and adds it to the in-memory database.

    Returns:
        json: The created item.
        int: HTTP status code 201 if successful.

    Raises:
        ValueError: If the input data is not valid JSON.
    """
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201

# Read all
@app.route("/items", methods=["GET"])
def read_items():
    """Retrieves all items from the in-memory database.

    Returns:
        json: A list of all items.
    """
    return jsonify(items)

# Read one
@app.route("/items/<int:item_id>", methods=["GET"])
def read_item(item_id):
    """Retrieves a single item by its ID.

    Args:
        item_id (int): The ID of the item to retrieve.

    Returns:
        json: The requested item.
        str: An error message if the item is not found.
        int: HTTP status code 404 if the item is not found.
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    return jsonify(items[item_id])

# Update
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Updates an existing item by its ID.

    Args:
        item_id (int): The ID of the item to update.

    Returns:
        json: The updated item.
        str: An error message if the item is not found.
        int: HTTP status code 404 if the item is not found.
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    data = request.get_json()
    items[item_id] = data
    return jsonify(data)

# Delete
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Deletes an item by its ID.

    Args:
        item_id (int): The ID of the item to delete.

    Returns:
        str: An empty response if successful.
        str: An error message if the item is not found.
        int: HTTP status code 404 if the item is not found.
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    del items[item_id]
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)