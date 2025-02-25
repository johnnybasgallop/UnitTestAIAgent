# basic.py
import random


def greet():
    random_number = random.randint(1, 100)
    print(f"hello {random_number}")


if __name__ == "__main__":
    greet()
