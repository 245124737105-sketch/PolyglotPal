from firebase_models import initialize_firebase, FirebaseUser
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Initialize Firebase
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
db = initialize_firebase(FIREBASE_CRED_PATH)

print("Firebase initialized successfully!")
print(f"Database: {db}")

# Test creating a user
try:
    print("\nTesting user creation...")
    user = FirebaseUser.create_user(db, "test@example.com", "Test User", "password123")
    if user:
        print(f"✅ User created successfully!")
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
    else:
        print("❌ User creation failed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
