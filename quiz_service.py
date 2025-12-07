import random
from googletrans import Translator

# Initialize translator
translator = Translator()

# Expanded vocabulary list organized by categories
VOCAB_CATEGORIES = {
    'greetings': ['Hello', 'Goodbye', 'Good morning', 'Good night', 'Thank you', 'Please', 'Sorry', 'Excuse me'],
    'numbers': ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'],
    'colors': ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 'Orange', 'Purple', 'Pink', 'Brown'],
    'food': ['Water', 'Bread', 'Rice', 'Milk', 'Coffee', 'Tea', 'Apple', 'Banana', 'Chicken', 'Fish'],
    'family': ['Mother', 'Father', 'Sister', 'Brother', 'Grandmother', 'Grandfather', 'Daughter', 'Son', 'Family', 'Friend'],
    'animals': ['Dog', 'Cat', 'Bird', 'Fish', 'Horse', 'Cow', 'Elephant', 'Lion', 'Tiger', 'Monkey'],
    'body': ['Head', 'Hand', 'Foot', 'Eye', 'Ear', 'Nose', 'Mouth', 'Heart', 'Arm', 'Leg'],
    'time': ['Today', 'Tomorrow', 'Yesterday', 'Morning', 'Afternoon', 'Evening', 'Night', 'Day', 'Week', 'Month'],
    'places': ['Home', 'School', 'Work', 'Hospital', 'Restaurant', 'Store', 'Park', 'City', 'Country', 'Street'],
    'common': ['Yes', 'No', 'Good', 'Bad', 'Big', 'Small', 'Hot', 'Cold', 'Happy', 'Sad', 'Love', 'Hate', 'Beautiful', 'Ugly']
}

# Flatten all words into a single list
ALL_WORDS = []
for category, words in VOCAB_CATEGORIES.items():
    ALL_WORDS.extend(words)

def generate_quiz_data(target_lang='es'):
    """
    Generates a quiz question with 4 options.
    Question is in English, answers are in the target language (Duolingo-style).
    Returns a dictionary with question, options, and correct_answer.
    """
    try:
        # Pick 4 random words from vocabulary
        selected_words = random.sample(ALL_WORDS, 4)
        
        # First word is the correct answer
        correct_word = selected_words[0]
        
        # Translate all options to target language
        translated_options = []
        correct_translation = None
        
        for word in selected_words:
            try:
                trans = translator.translate(word, dest=target_lang)
                translated_text = trans.text
                pronunciation = trans.pronunciation if trans.pronunciation else trans.text
                
                translated_options.append({
                    'original': word,
                    'translated': translated_text,
                    'pronunciation': pronunciation
                })
                
                # Store the correct answer's translation
                if word == correct_word:
                    correct_translation = translated_text
                    
            except Exception as e:
                # Fallback if translation fails for a specific word
                print(f"Translation failed for '{word}': {e}")
                translated_options.append({
                    'original': word,
                    'translated': word,  # Fallback to original
                    'pronunciation': word
                })
                if word == correct_word:
                    correct_translation = word
        
        # Shuffle the options so correct answer isn't always first
        random.shuffle(translated_options)
        
        # Get language name for display
        lang_names = {
            'es': 'Spanish', 'fr': 'French', 'de': 'German', 
            'hi': 'Hindi', 'te': 'Telugu', 'ta': 'Tamil',
            'ja': 'Japanese', 'ko': 'Korean', 'zh-cn': 'Chinese',
            'ar': 'Arabic', 'ru': 'Russian', 'pt': 'Portuguese',
            'it': 'Italian', 'nl': 'Dutch', 'pl': 'Polish'
        }
        lang_name = lang_names.get(target_lang, target_lang.upper())
        
        return {
            'question': f"What is '{correct_word}' in {lang_name}?",
            'options': translated_options,
            'correct_answer': correct_translation,
            'correct_word': correct_word  # For reference
        }
        
    except Exception as e:
        # Better error handling
        print(f"Quiz generation error: {str(e)}")
        raise Exception(f"Quiz generation failed: {str(e)}")
