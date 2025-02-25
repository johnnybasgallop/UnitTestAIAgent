from flask import Flask, request, jsonify

"""
A simple Flask API for managing a list of items.

This module provides a RESTful API for creating, reading, updating, and deleting items.
Items are stored in an in-memory list for simplicity.
"""

app = Flask(__name__)

# In-memory "database" for simplicity
items = []


# Create
@app.route("/items", methods=["POST"])
def create_item():
    """
    Creates a new item.

    Args:
        None

    Returns:
        tuple: A tuple containing the JSON representation of the created item and the HTTP status code 201 (Created).

    Raises:
        None
    """
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201


# Read all
@app.route("/items", methods=["GET"])
def read_items():
    """
    Reads all items.

    Args:
        None

    Returns:
        tuple: A tuple containing the JSON representation of all items and the HTTP status code 200 (OK).

    Raises:
        None
    """
    return jsonify(items)


# Read one
@app.route("/items/<int:item_id>", methods=["GET"])
def read_item(item_id):
    """
    Reads a single item by its ID.

    Args:
        item_id (int): The ID of the item to read.

    Returns:
        tuple: A tuple containing the JSON representation of the item and the HTTP status code 200 (OK) if the item is found, or a tuple containing an error message and the HTTP status code 404 (Not Found) if the item is not found.

    Raises:
        None
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    return jsonify(items[item_id])


# Update
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """
    Updates an existing item by its ID.

    Args:
        item_id (int): The ID of the item to update.

    Returns:
        tuple: A tuple containing the JSON representation of the updated item and the HTTP status code 200 (OK) if the item is found, or a tuple containing an error message and the HTTP status code 404 (Not Found) if the item is not found.

    Raises:
        None
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    data = request.get_json()
    items[item_id] = data
    return jsonify(data)


# Delete
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Deletes an item by its ID.

    Args:
        item_id (int): The ID of the item to delete.

    Returns:
        tuple: A tuple containing an empty string and the HTTP status code 204 (No Content) if the item is found, or a tuple containing an error message and the HTTP status code 404 (Not Found) if the item is not found.

    Raises:
        None
    """
    if item_id < 0 or item_id >= len(items):
        return "Item not found.", 404
    del items[item_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)