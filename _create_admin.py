"""
DeepGuard – Create/update admin account with hashed password.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from config import Config
from pymongo import MongoClient
from datetime import datetime, timezone
import bcrypt

email    = "admin0211@gmail.com"
password = "Krish@02"
name     = "DeepGuard Admin"

client = MongoClient(Config.MONGODB_URI)
db     = client["deepguard_db"]

pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

existing = db.users.find_one({"email": email})
if existing:
    db.users.update_one(
        {"email": email},
        {"$set": {"password_hash": pw_hash, "role": "admin", "name": name}}
    )
    print(f"[UPDATED] {email} -> role=admin, password reset.")
else:
    db.users.insert_one({
        "name":          name,
        "email":         email,
        "password_hash": pw_hash,
        "role":          "admin",
        "created_at":    datetime.now(timezone.utc),
    })
    print(f"[CREATED] {email} -> role=admin")

print("Done. Login at http://127.0.0.1:5000/login")
