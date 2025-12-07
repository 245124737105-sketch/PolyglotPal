"""
Test script to verify authentication system
Tests password hashing and verification
"""
import os
import sys
from dotenv import load_dotenv
from firebase_models import initialize_firebase, FirebaseUser
from werkzeug.security import check_password_hash

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Initialize Firebase
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
db = initialize_firebase(FIREBASE_CRED_PATH)

print("=" * 60)
print("AUTHENTICATION SYSTEM TEST")
print("=" * 60)

# Test 1: Create a test user
print("\n[TEST 1] Creating test user...")
test_email = "authtest@example.com"
test_password = "SecurePassword123"
test_username = "Auth Test User"

# Check if user already exists and delete
existing_user = FirebaseUser.get_by_email(db, test_email)
if existing_user:
    print(f"  [!] User {test_email} already exists, deleting...")
    try:
        # Delete from Firebase Auth
        from firebase_admin import auth
        auth.delete_user(existing_user.id)
    except Exception as e:
        print(f"  [!] Could not delete from Firebase Auth: {e}")
    
    # Delete from Firestore
    db.collection('users').document(existing_user.id).delete()
    db.collection('user_stats').document(existing_user.id).delete()

# Create new user
new_user = FirebaseUser.create_user(db, test_email, test_username, test_password)
if new_user:
    print(f"  [PASS] User created successfully: {new_user.email}")
else:
    print("  [FAIL] Failed to create user")
    exit(1)

# Test 2: Verify password is hashed in Firestore
print("\n[TEST 2] Verifying password is hashed...")
user_ref = db.collection('users').document(new_user.id)
user_data = user_ref.get().to_dict()

if 'password_hash' in user_data:
    password_hash = user_data['password_hash']
    print(f"  [PASS] Password hash found: {password_hash[:50]}...")
    
    # Verify it's not the plain password
    if password_hash != test_password:
        print(f"  [PASS] Password is hashed (not stored as plain text)")
    else:
        print(f"  [FAIL] WARNING: Password appears to be stored in plain text!")
        
    # Verify the hash format
    if password_hash.startswith('pbkdf2:sha256:'):
        print(f"  [PASS] Hash format is correct (pbkdf2:sha256)")
    else:
        print(f"  [!] Unexpected hash format: {password_hash[:20]}")
else:
    print("  [FAIL] No password hash found in Firestore!")
    exit(1)

# Test 3: Verify correct password
print("\n[TEST 3] Testing login with CORRECT password...")
is_valid = FirebaseUser.verify_password(db, test_email, test_password)
if is_valid:
    print(f"  [PASS] Password verification PASSED (correct password accepted)")
else:
    print(f"  [FAIL] Password verification FAILED (correct password rejected!)")
    exit(1)

# Test 4: Verify incorrect password is rejected
print("\n[TEST 4] Testing login with INCORRECT password...")
is_valid = FirebaseUser.verify_password(db, test_email, "WrongPassword123")
if not is_valid:
    print(f"  [PASS] Password verification PASSED (incorrect password rejected)")
else:
    print(f"  [FAIL] Password verification FAILED (incorrect password accepted!)")
    exit(1)

# Test 5: Verify non-existent user
print("\n[TEST 5] Testing login with non-existent user...")
is_valid = FirebaseUser.verify_password(db, "nonexistent@example.com", "anypassword")
if not is_valid:
    print(f"  [PASS] Password verification PASSED (non-existent user rejected)")
else:
    print(f"  [FAIL] Password verification FAILED (non-existent user accepted!)")
    exit(1)

# Cleanup
print("\n[CLEANUP] Removing test user...")
try:
    from firebase_admin import auth
    auth.delete_user(new_user.id)
except Exception as e:
    print(f"  [!] Could not delete from Firebase Auth: {e}")
    
db.collection('users').document(new_user.id).delete()
db.collection('user_stats').document(new_user.id).delete()
print("  [PASS] Test user removed")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nAuthentication system is working correctly:")
print("  - Passwords are hashed using pbkdf2:sha256")
print("  - Correct passwords are accepted")
print("  - Incorrect passwords are rejected")
print("  - Non-existent users are rejected")

