"""
Cleanup script to remove test user from Firebase Auth
"""
import os
from dotenv import load_dotenv
from firebase_models import initialize_firebase
from firebase_admin import auth

load_dotenv()

FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
db = initialize_firebase(FIREBASE_CRED_PATH)

test_email = "authtest@example.com"

print(f"Looking for user: {test_email}")

try:
    # Get user by email from Firebase Auth
    user = auth.get_user_by_email(test_email)
    print(f"Found user with UID: {user.uid}")
    
    # Delete from Firebase Auth
    auth.delete_user(user.uid)
    print(f"Deleted from Firebase Auth")
    
    # Delete from Firestore
    db.collection('users').document(user.uid).delete()
    db.collection('user_stats').document(user.uid).delete()
    print(f"Deleted from Firestore")
    
    print("Cleanup complete!")
except Exception as e:
    print(f"Error or user not found: {e}")
