from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
from googletrans import Translator
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import quiz_service
import os
from dotenv import load_dotenv
from datetime import datetime
from firebase_models import (
    initialize_firebase, FirebaseUser, UserStats, 
    TranslationHistory, QuizResults, LanguageProgress
)
from firebase_admin import auth as firebase_auth

# Load environment variables
load_dotenv()

import json

# Initialize Flask app
app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Firebase
# First check for JSON content in environment variable (Render/Cloud)
firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
if firebase_creds:
    # If it's a string containing JSON
    try:
        cred_dict = json.loads(firebase_creds)
        db = initialize_firebase(cred_dict)
        print("Initialized Firebase from environment variable")
    except json.JSONDecodeError as e:
        print(f"Error parsing FIREBASE_CREDENTIALS: {e}")
        # Fallback
        FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        db = initialize_firebase(FIREBASE_CRED_PATH)
else:
    # Fallback to file path (Local)
    FIREBASE_CRED_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    db = initialize_firebase(FIREBASE_CRED_PATH)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return FirebaseUser.get_by_id(db, user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Protect dashboard and other app pages
    if filename in ['dashboard.html', 'translate.html', 'quiz.html'] and not current_user.is_authenticated:
        return redirect(url_for('login'))
        
    if filename.endswith('.html'):
        return render_template(filename)
    return send_from_directory('.', filename)

# Auth Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = FirebaseUser.get_by_email(db, email)
        if existing_user:
            flash('Email already exists')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = FirebaseUser.create_user(db, email, username, password)
        if new_user:
            login_user(new_user)
            return redirect(url_for('dashboard'))
        else:
            flash('Error creating account. Please try again.')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Get user from Firebase
        user = FirebaseUser.get_by_email(db, email)
        
        if not user:
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        
        # Verify password
        if not FirebaseUser.verify_password(db, email, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        
        # Password is correct, log in user
        try:
            user.update_last_login(db)
            login_user(user)
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('An error occurred. Please try again.')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard.html')
@login_required
def dashboard():
    # Get user stats from Firebase
    stats = UserStats.get_stats(db, current_user.id)
    
    return render_template('dashboard.html', 
                         name=current_user.username,
                         date_today=datetime.now().strftime("%A, %b %d"),
                         stats=stats)

@app.route('/translate.html')
@login_required
def translate():
    return render_template('translate.html',
                         name=current_user.username)

# API Routes
@app.route('/api/user/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user statistics"""
    try:
        stats = UserStats.get_stats(db, current_user.id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/translations', methods=['GET'])
@login_required
def get_user_translations():
    """Get user's translation history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        translations = TranslationHistory.get_user_translations(db, current_user.id, limit)
        return jsonify(translations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/quiz-results', methods=['GET'])
@login_required
def get_quiz_results():
    """Get user's quiz results"""
    try:
        limit = request.args.get('limit', 10, type=int)
        results = QuizResults.get_user_results(db, current_user.id, limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/language-progress', methods=['GET'])
@login_required
def get_language_progress():
    """Get user's language progress"""
    try:
        progress = LanguageProgress.get_all_progress(db, current_user.id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    try:
        data = request.json
        text = data.get('text')
        source_lang = data.get('source', 'auto')
        target_lang = data.get('target', 'en')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Print translation request (safely handle Unicode)
        try:
            print(f"Translating '{text}' from {source_lang} to {target_lang}...")
        except UnicodeEncodeError:
            print(f"Translating text from {source_lang} to {target_lang}...")

        # Initialize translator per request for stability
        translator = Translator()
        translation = translator.translate(text, src=source_lang, dest=target_lang)

        # Print translation result (safely handle Unicode)
        try:
            print(f"Translation result: {translation.text}")
        except UnicodeEncodeError:
            print(f"Translation completed (non-ASCII result)")

        # Save translation to Firebase only if user is logged in
        if current_user.is_authenticated:
            try:
                TranslationHistory.add_translation(
                    db, 
                    current_user.id,
                    text,
                    translation.text,
                    translation.src,
                    translation.dest
                )
                
                # Increment words learned (simplified)
                UserStats.increment_stat(db, current_user.id, 'words_learned', 1)
                UserStats.increment_stat(db, current_user.id, 'total_points', 10)
            except Exception as e:
                print(f"Failed to save to Firebase: {e}")

        response = {
            'original': text,
            'translated': translation.text,
            'pronunciation': translation.pronunciation, 
            'src_lang': translation.src,
            'dest_lang': translation.dest
        }
        
        return jsonify(response)

    except Exception as e:
        print(f"Translation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/translation/history', methods=['GET'])
@login_required
def get_translation_history():
    """Get user's translation history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        translations = TranslationHistory.get_user_translations(db, current_user.id, limit)
        
        # Convert datetime objects to strings for JSON serialization
        for translation in translations:
            if 'timestamp' in translation and hasattr(translation['timestamp'], 'isoformat'):
                translation['timestamp'] = translation['timestamp'].isoformat()
        
        return jsonify(translations)
    except Exception as e:
        print(f"Error fetching translation history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
@login_required
def generate_quiz():
    try:
        data = request.json
        target_lang = data.get('target', 'es')

        response = quiz_service.generate_quiz_data(target_lang)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz results"""
    try:
        data = request.json
        language = data.get('language')
        score = data.get('score')
        total_questions = data.get('total_questions')
        correct_answers = data.get('correct_answers')
        
        # Save quiz result
        QuizResults.add_result(
            db,
            current_user.id,
            language,
            score,
            total_questions,
            correct_answers
        )
        
        # Update stats
        points = correct_answers * 20
        UserStats.increment_stat(db, current_user.id, 'total_points', points)
        
        return jsonify({'success': True, 'points_earned': points})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Polyglot Pal Server with Firebase...")
    print("Go to http://localhost:5000 to view the app")
    app.run(debug=True)
