# Direct test of googletrans - exactly like the tkinter code
from googletrans import Translator

print("Testing googletrans directly (like tkinter code)...\n")

texts_to_test = [
    ("welcome to polyglot pal", "en", "hi", "Hindi"),
    ("welcome to polyglot pal", "en", "te", "Telugu"),
    ("hello world", "en", "es", "Spanish"),
]

translator = Translator()  # reuse one instance

for text, src, dest, lang_name in texts_to_test:
    try:
        print(f"Test: '{text}' to {lang_name}")
        result = translator.translate(text, src=src, dest=dest)
        print(f"Success: {result.text}")
        print(f"  Source: {result.src}, Dest: {result.dest}")
        if result.pronunciation:
            print(f"  Pronunciation: {result.pronunciation}")
        print()
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        print()
