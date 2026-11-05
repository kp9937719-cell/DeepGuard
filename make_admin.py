"""
DeepGuard – Admin Account Setup Script
=======================================
Run this once to promote an existing user to the admin role.

Usage:
    python make_admin.py your@email.com

Requirements:
    - MongoDB must be running
    - The user must already be registered at http://127.0.0.1:5000/register
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from pymongo import MongoClient

def make_admin(email: str):
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB_NAME]

    user = db.users.find_one({"email": email})
    if not user:
        print(f"[ERROR] No user found with email: {email}")
        print("       Register first at http://127.0.0.1:5000/register")
        sys.exit(1)

    if user.get("role") == "admin":
        print(f"[INFO] {email} is already an admin.")
        sys.exit(0)

    db.users.update_one({"email": email}, {"$set": {"role": "admin"}})
    print(f"[OK] {email} has been promoted to admin.")
    print(f"     Admin dashboard: http://127.0.0.1:5000/admin/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)
    make_admin(sys.argv[1].strip())
