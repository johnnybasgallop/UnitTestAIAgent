import os
from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from flask import Flask, abort, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# --- Configuration ---
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "your-secret-key"
)  # Use environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///:memory:"
)  # Use environment variable or in-memory
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Models ---


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    roles = db.relationship(
        "Role", secondary="user_roles", backref=db.backref("users", lazy="dynamic")
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "roles": [role.name for role in self.roles],  # Include roles
        }


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


# Association table for many-to-many relationship between User and Role
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", backref=db.backref("products", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category.name,  # Include category name
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("orders", lazy=True))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), default="Pending"
    )  # e.g., Pending, Shipped, Delivered
    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "order_date": self.order_date.isoformat(),
            "total_amount": self.total_amount,
            "status": self.status,
            "items": [item.to_dict() for item in self.items],  # Include order items
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product")  # No backref needed here
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at the time of order

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name,  # Include Product Name
            "quantity": self.quantity,
            "price": self.price,
        }


# --- Helper Functions ---


def create_admin_user():
    """Creates an admin user if one doesn't exist."""
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        db.session.add(admin_role)
        db.session.commit()  # Commit to get the role ID

    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(username="admin", email="admin@example.com", is_active=True)
        admin_user.set_password("admin")
        admin_user.roles.append(admin_role)  # Append here
        db.session.add(admin_user)
        db.session.commit()


def token_required(f):
    """Decorator for requiring a valid JWT."""

    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.get(data["id"])
            if not current_user:
                return jsonify({"message": "User not found"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e:
            return jsonify({"message": "Error decoding token!"}), 401

        return f(current_user, *args, **kwargs)

    decorated.__name__ = f.__name__  # Important: Stops function name changing
    return decorated


# --- Routes ---


@app.route("/api/register", methods=["POST"])
def register():
    """Registers a new user."""
    data = request.get_json()
    if (
        not data
        or not data.get("username")
        or not data.get("password")
        or not data.get("email")
    ):
        abort(400, description="Missing username, password, or email")

    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        abort(400, description="Username already exists")

    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return (
        jsonify({"message": "User registered successfully", "user_id": new_user.id}),
        201,
    )


@app.route("/api/login", methods=["POST"])
def login():
    """Logs in a user and returns a JWT."""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    user = User.query.filter_by(username=auth.username).first()
    if not user or not user.check_password(auth.password):
        return make_response(
            "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
        )

    token = jwt.encode(
        {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return jsonify({"token": token})


@app.route("/api/users", methods=["GET"])
@token_required
def get_all_users(current_user):
    """Gets all users (requires admin role)."""
    if not any(role.name == "admin" for role in current_user.roles):
        return jsonify({"message": "Unauthorized"}), 403

    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@app.route("/api/users/<int:user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    """Gets a specific user by ID."""
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    # Check if the current user is the user being requested or is an admin
    if current_user.id != user_id and not any(
        role.name == "admin" for role in current_user.roles
    ):
        return jsonify({"message": "Unauthorized"}), 403

    return jsonify(user.to_dict()), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    """Gets all products."""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Gets a product by ID."""
    product = Product.query.get(product_id)
    if not product:
        abort(404, description="Product not found")
    return jsonify(product.to_dict()), 200


@app.route("/api/products", methods=["POST"])
@token_required
def create_product(current_user):
    """Creates a new product (requires admin role)."""
    if not any(role.name == "admin" for role in current_user.roles):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    if (
        not data
        or not data.get("name")
        or not data.get("price")
        or not data.get("category_id")
    ):
        abort(400, description="Missing name, price, or category_id")

    category = Category.query.get(data["category_id"])
    if not category:
        abort(400, description="Invalid category_id")

    new_product = Product(
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        stock=data.get("stock", 0),
        category_id=data["category_id"],
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
@token_required
def update_product(current_user, product_id):
    """Updates an existing product (requires admin role)."""

    if not any(role.name == "admin" for role in current_user.roles):
        return jsonify({"message": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        abort(404, description="Product not found")

    data = request.get_json()
    if not data:
        abort(400, description="No Data")

    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "price" in data:
        product.price = data["price"]
    if "stock" in data:
        product.stock = data["stock"]
    if "category_id" in data:
        category = Category.query.get(data["category_id"])
        if not category:
            abort(400, description="Invalid category_id")
        product.category_id = data["category_id"]

    db.session.commit()
    return jsonify(product.to_dict()), 200


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
@token_required
def delete_product(current_user, product_id):
    """Deletes a product (requires admin role)."""
    if not any(role.name == "admin" for role in current_user.roles):
        return jsonify({"message": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        abort(404, description="Product not found")

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Gets all categories."""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories]), 200


@app.route("/api/categories", methods=["POST"])
@token_required
def create_category(current_user):
    """Creates a new category (requires admin role)."""
    if not any(role.name == "admin" for role in current_user.roles):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    if not data or not data.get("name"):
        abort(400, description="Missing name")
    new_category = Category(name=data["name"])

    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201


@app.route("/api/orders", methods=["POST"])
@token_required
def create_order(current_user):
    """Creates a new order."""
    data = request.get_json()
    if not data or not data.get("items"):
        abort(400, description="Missing items")

    # Validate items and calculate total amount
    total_amount = 0
    order_items = []
    for item_data in data["items"]:
        product_id = item_data.get("product_id")
        quantity = item_data.get("quantity")

        if not product_id or not quantity or quantity <= 0:
            abort(400, description="Invalid item data")

        product = Product.query.get(product_id)
        if not product:
            abort(400, description=f"Product with id {product_id} not found")

        if product.stock < quantity:
            abort(400, description=f"Not enough stock for product {product.name}")

        order_item = OrderItem(product=product, quantity=quantity, price=product.price)
        order_items.append(order_item)
        total_amount += product.price * quantity

    # Create the order
    new_order = Order(user=current_user, total_amount=total_amount)
    new_order.items = order_items  # Assign the items
    db.session.add(new_order)

    # Reduce product stock
    for item in order_items:
        item.product.stock -= item.quantity

    db.session.commit()
    return jsonify(new_order.to_dict()), 201


@app.route("/api/orders", methods=["GET"])
@token_required
def get_orders(current_user):
    """Gets all orders for the current user (or all orders if admin)."""

    if any(role.name == "admin" for role in current_user.roles):
        orders = Order.query.all()  # Admin gets all


if __name__ == "__main__":
    app.run(debug=True)
