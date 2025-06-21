from zodiac_text import main as zodiac_text_main
import pyttsx3
import io
from datetime import datetime

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

def get_male_voice(engine, lang_code):
    """Get a male voice for the specified language."""
    log_print("INFO", "Searching for male voice")
    
    # Get available voices
    voices = engine.getProperty('voices')
    log_print("DEBUG", f"Found {len(voices)} available voices")
    
    # Language code mapping for voice selection
    lang_voice_mapping = {
        0: ['tamil', 'ta', 'indian'],  # Tamil
        1: ['english', 'en', 'us', 'uk'],  # English
        2: ['hindi', 'hi', 'indian']  # Hindi
    }
    
    target_langs = lang_voice_mapping.get(lang_code, ['english'])
    log_print("DEBUG", f"Looking for voices matching: {target_langs}")
    
    # Try to find a male voice for the target language
    for voice in voices:
        voice_name = voice.name.lower()
        voice_id = voice.id.lower()
        
        # Check if it's a male voice (common male voice indicators)
        is_male = any(indicator in voice_name for indicator in ['male', 'man', 'david', 'james', 'john', 'mike', 'steve'])
        
        # Check if it matches our target language
        matches_lang = any(lang in voice_name or lang in voice_id for lang in target_langs)
        
        if is_male and matches_lang:
            log_print("INFO", f"Found male voice: {voice.name} ({voice.id})")
            return voice.id
    
    # Fallback: find any male voice
    for voice in voices:
        voice_name = voice.name.lower()
        if any(indicator in voice_name for indicator in ['male', 'man', 'david', 'james', 'john', 'mike', 'steve']):
            log_print("INFO", f"Using fallback male voice: {voice.name} ({voice.id})")
            return voice.id
    
    # If no male voice found, use the first available voice
    if voices:
        log_print("WARNING", f"No male voice found, using default: {voices[0].name}")
        return voices[0].id
    
    log_print("ERROR", "No voices available")
    return None

def zodiac_reader(text, lang_code):
    """Generate speech from text using pyttsx3 with male voice."""
    log_print("INFO", "=== Starting Text-to-Speech Conversion ===")
    log_print("INFO", f"Language code: {lang_code}")
    log_print("INFO", f"Text length: {len(text)} characters")
    
    try:
        log_print("INFO", "Initializing pyttsx3 engine")
        engine = pyttsx3.init()
        
        # Set male voice
        male_voice_id = get_male_voice(engine, lang_code)
        if male_voice_id:
            engine.setProperty('voice', male_voice_id)
            log_print("INFO", f"Set male voice: {male_voice_id}")
        
        # Configure speech properties
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        log_print("INFO", "Converting speech to audio buffer")
        
        # Save to temporary file first (pyttsx3 limitation)
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate speech to file
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        
        # Read the file into buffer
        audio_buffer = io.BytesIO()
        with open(temp_path, 'rb') as f:
            audio_buffer.write(f.read())
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        audio_buffer.seek(0)
        buffer_size = len(audio_buffer.getvalue())
        log_print("INFO", f"Audio buffer created successfully. Size: {buffer_size} bytes")
        log_print("INFO", "=== Text-to-Speech Conversion Completed Successfully ===")
        
        return audio_buffer
        
    except Exception as e:
        log_print("ERROR", f"Error in text-to-speech conversion: {str(e)}")
        raise

def main(lang_code):
    """Main function to generate zodiac audio."""
    log_print("INFO", "=== Starting Zodiac Audio Generation Process ===")
    log_print("INFO", f"Language code received: {lang_code}")
    
    # Language mapping
    langs = ['ta', 'en-in', 'hi']
    
    if lang_code < 0 or lang_code >= len(langs):
        log_print("ERROR", f"Invalid language code: {lang_code}. Valid range: 0-{len(langs)-1}")
        raise ValueError(f"Invalid language code: {lang_code}")
    
    lang = langs[lang_code]
    log_print("INFO", f"Selected language: {lang} (code: {lang_code})")
    
    try:
        log_print("INFO", "Calling zodiac_text_main to generate zodiac content")
        zodiac_text = zodiac_text_main(lang)
        
        if not zodiac_text or zodiac_text.startswith("An error occurred"):
            log_print("ERROR", "Failed to get zodiac text from zodiac_text_main")
            raise Exception("Zodiac text generation failed")
        
        log_print("INFO", "Zodiac text generated successfully")
        log_print("DEBUG", f"Zodiac text preview: {zodiac_text[:100]}...")
        
        # Generate audio from text with male voice
        audio_buffer = zodiac_reader(zodiac_text, lang_code)
        
        log_print("INFO", "=== Zodiac Audio Generation Completed Successfully ===")
        return audio_buffer
        
    except Exception as e:
        log_print("ERROR", f"Error in main zodiac audio generation process: {str(e)}")
        raise

# if __name__ == "__main__":
#     main(0)
