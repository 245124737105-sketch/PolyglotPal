from firebase_models import initialize_firebase, FirebaseUser
from dotenv import load_dotenv
import os
import random

# Load environment
load_dotenv()

# Initialize Firebase
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
db = initialize_firebase(FIREBASE_CRED_PATH)

print("Firebase initialized successfully!")

# Test creating a user with a unique email
random_num = random.randint(1000, 9999)
email = f"newuser{random_num}@example.com"

print(f"\nTesting user creation with email: {email}")
try:
    user = FirebaseUser.create_user(db, email, f"Test User {random_num}", "password123")
    if user:
        print(f"SUCCESS! User created!")
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
    else:
        print("FAILED: User creation returned None")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
