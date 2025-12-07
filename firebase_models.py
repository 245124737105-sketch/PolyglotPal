import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Firebase (will be called from app.py)
def initialize_firebase(cred_path):
    """Initialize Firebase Admin SDK"""
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

class FirebaseUser:
    """User model for Firebase Firestore"""
    
    def __init__(self, user_id, email, username, created_at=None):
        self.id = user_id
        self.email = email
        self.username = username
        self.created_at = created_at or datetime.now()
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        """Required for Flask-Login"""
        return self.id
    
    @staticmethod
    def create_user(db, email, username, password):
        """Create a new user in Firebase"""
        try:
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Create user in Firebase Auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            # Store additional user data in Firestore with hashed password
            user_ref = db.collection('users').document(user_record.uid)
            user_data = {
                'email': email,
                'username': username,
                'password_hash': password_hash,  # Store hashed password
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            user_ref.set(user_data)
            
            # Initialize user stats
            stats_ref = db.collection('user_stats').document(user_record.uid)
            stats_ref.set({
                'streak_days': 0,
                'total_points': 0,
                'words_learned': 0,
                'quizzes_taken': 0,
                'last_updated': datetime.now()
            })
            
            return FirebaseUser(user_record.uid, email, username)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_by_email(db, email):
        """Get user by email"""
        try:
            # Query Firestore for user
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict()
                return FirebaseUser(
                    doc.id,
                    data['email'],
                    data['username'],
                    data.get('created_at')
                )
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def get_by_id(db, user_id):
        """Get user by ID"""
        try:
            user_ref = db.collection('users').document(user_id)
            doc = user_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return FirebaseUser(
                    doc.id,
                    data['email'],
                    data['username'],
                    data.get('created_at')
                )
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def verify_password(db, email, password):
        """Verify user password by checking hash in Firestore"""
        try:
            # Get user from Firestore
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict()
                password_hash = data.get('password_hash')
                
                if password_hash:
                    # Verify password using werkzeug
                    return check_password_hash(password_hash, password)
                else:
                    print(f"No password hash found for user: {email}")
                    return False
            
            # User not found
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def update_last_login(self, db):
        """Update user's last login timestamp"""
        try:
            user_ref = db.collection('users').document(self.id)
            user_ref.update({'last_login': datetime.now()})
        except Exception as e:
            print(f"Error updating last login: {e}")


class UserStats:
    """User statistics model"""
    
    @staticmethod
    def get_stats(db, user_id):
        """Get user statistics"""
        try:
            stats_ref = db.collection('user_stats').document(user_id)
            doc = stats_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                # Create default stats if not exists
                default_stats = {
                    'streak_days': 0,
                    'total_points': 0,
                    'words_learned': 0,
                    'quizzes_taken': 0,
                    'last_updated': datetime.now()
                }
                stats_ref.set(default_stats)
                return default_stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    @staticmethod
    def update_stats(db, user_id, stats_data):
        """Update user statistics"""
        try:
            stats_ref = db.collection('user_stats').document(user_id)
            stats_data['last_updated'] = datetime.now()
            stats_ref.update(stats_data)
            return True
        except Exception as e:
            print(f"Error updating stats: {e}")
            return False
    
    @staticmethod
    def increment_stat(db, user_id, stat_name, increment=1):
        """Increment a specific stat"""
        try:
            stats_ref = db.collection('user_stats').document(user_id)
            stats_ref.update({
                stat_name: firestore.Increment(increment),
                'last_updated': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error incrementing stat: {e}")
            return False


class TranslationHistory:
    """Translation history model"""
    
    @staticmethod
    def add_translation(db, user_id, source_text, translated_text, source_lang, target_lang):
        """Add a translation to history"""
        try:
            translation_ref = db.collection('translations').document()
            translation_ref.set({
                'user_id': user_id,
                'source_text': source_text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'timestamp': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error adding translation: {e}")
            return False
    
    @staticmethod
    def get_user_translations(db, user_id, limit=10):
        """Get user's recent translations"""
        try:
            translations_ref = db.collection('translations')
            query = translations_ref.where('user_id', '==', user_id).limit(limit * 2)  # Get more to sort
            
            translations = []
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                translations.append(data)
            
            # Sort by timestamp in Python (descending - newest first)
            translations.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            
            # Return only the requested limit
            return translations[:limit]
        except Exception as e:
            print(f"Error getting translations: {e}")
            import traceback
            traceback.print_exc()
            return []


class QuizResults:
    """Quiz results model"""
    
    @staticmethod
    def add_result(db, user_id, language, score, total_questions, correct_answers):
        """Add a quiz result"""
        try:
            quiz_ref = db.collection('quiz_results').document()
            quiz_ref.set({
                'user_id': user_id,
                'language': language,
                'score': score,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'timestamp': datetime.now()
            })
            
            # Increment quizzes taken stat
            UserStats.increment_stat(db, user_id, 'quizzes_taken')
            
            return True
        except Exception as e:
            print(f"Error adding quiz result: {e}")
            return False
    
    @staticmethod
    def get_user_results(db, user_id, limit=10):
        """Get user's recent quiz results"""
        try:
            results_ref = db.collection('quiz_results')
            query = results_ref.where('user_id', '==', user_id)\
                              .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                              .limit(limit)
            
            results = []
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            print(f"Error getting quiz results: {e}")
            return []


class LanguageProgress:
    """Language progress tracking"""
    
    @staticmethod
    def update_progress(db, user_id, language_code, progress_percent, words_learned=0):
        """Update progress for a specific language"""
        try:
            progress_ref = db.collection('language_progress').document(user_id)\
                            .collection('languages').document(language_code)
            
            progress_ref.set({
                'progress_percent': progress_percent,
                'words_learned': words_learned,
                'last_practiced': datetime.now()
            }, merge=True)
            
            return True
        except Exception as e:
            print(f"Error updating language progress: {e}")
            return False
    
    @staticmethod
    def get_all_progress(db, user_id):
        """Get progress for all languages"""
        try:
            progress_ref = db.collection('language_progress').document(user_id)\
                            .collection('languages')
            
            progress_data = {}
            for doc in progress_ref.stream():
                progress_data[doc.id] = doc.to_dict()
            
            return progress_data
        except Exception as e:
            print(f"Error getting language progress: {e}")
            return {}
