// Speech Recognition Language Mapping Fix
// This file fixes the speech recognition language code issue

(function () {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSpeechFix);
    } else {
        initSpeechFix();
    }

    function initSpeechFix() {
        const micBtn = document.getElementById('micBtn');
        const sourceText = document.getElementById('sourceText');
        const sourceLang = document.getElementById('sourceLang');

        if (!micBtn || !sourceText || !sourceLang) {
            console.error('Speech fix: Required elements not found');
            return;
        }

        // Remove existing event listeners by cloning the button
        const newMicBtn = micBtn.cloneNode(true);
        micBtn.parentNode.replaceChild(newMicBtn, micBtn);

        // Add new event listener with proper language mapping
        newMicBtn.addEventListener('click', function () {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                showToast('Speech recognition not supported in this browser');
                return;
            }

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();

            // Proper language code mapping
            const langMap = {
                'en': 'en-US',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'it': 'it-IT',
                'pt': 'pt-PT',
                'ru': 'ru-RU',
                'ja': 'ja-JP',
                'ko': 'ko-KR',
                'zh-cn': 'zh-CN',
                'zh-tw': 'zh-TW',
                'ar': 'ar-SA',
                'hi': 'hi-IN',
                'te': 'te-IN',
                'bn': 'bn-IN',
                'vi': 'vi-VN',
                'th': 'th-TH',
                'tr': 'tr-TR',
                'pl': 'pl-PL',
                'uk': 'uk-UA',
                'nl': 'nl-NL',
                'sv': 'sv-SE',
                'no': 'no-NO',
                'da': 'da-DK',
                'fi': 'fi-FI'
            };

            const selectedLang = sourceLang.value === 'auto' ? 'en' : sourceLang.value;
            recognition.lang = langMap[selectedLang] || 'en-US';
            recognition.continuous = false;
            recognition.interimResults = false;

            newMicBtn.textContent = '🎤 Listening...';
            newMicBtn.disabled = true;

            recognition.onresult = function (event) {
                const transcript = event.results[0][0].transcript;
                sourceText.value = transcript;

                // Trigger char count update if function exists
                if (typeof updateCharCount === 'function') {
                    updateCharCount();
                }

                if (typeof showToast === 'function') {
                    showToast('Speech captured! ✓');
                }

                newMicBtn.textContent = '🎤 Speak';
                newMicBtn.disabled = false;
            };

            recognition.onerror = function (event) {
                console.error('Speech recognition error:', event.error);

                if (typeof showToast === 'function') {
                    showToast('Speech recognition error: ' + event.error);
                }

                newMicBtn.textContent = '🎤 Speak';
                newMicBtn.disabled = false;
            };

            recognition.onend = function () {
                newMicBtn.textContent = '🎤 Speak';
                newMicBtn.disabled = false;
            };

            try {
                recognition.start();
            } catch (error) {
                console.error('Failed to start recognition:', error);
                newMicBtn.textContent = '🎤 Speak';
                newMicBtn.disabled = false;

                if (typeof showToast === 'function') {
                    showToast('Failed to start speech recognition');
                }
            }
        });

        console.log('Speech recognition fix applied successfully');
    }
})();
