from zodiac_text import main as zodiac_text_main
from gtts import gTTS
import io
from datetime import datetime

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

def zodiac_reader(text, lang):
    """Generate speech from text using gTTS."""
    log_print("INFO", "=== Starting Text-to-Speech Conversion ===")
    log_print("INFO", f"Language: {lang}")
    log_print("INFO", f"Text length: {len(text)} characters")
    
    try:
        log_print("INFO", "Initializing gTTS with specified parameters")
        # Generate Tamil speech
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        log_print("INFO", "gTTS object created successfully")
        
        # Save to bytes buffer instead of file
        log_print("INFO", "Converting speech to audio buffer")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
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
    
    # Tamil, English, Hindi zodiac text
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
        
        # Generate audio from text
        audio_buffer = zodiac_reader(zodiac_text, lang)
        
        log_print("INFO", "=== Zodiac Audio Generation Completed Successfully ===")
        return audio_buffer
        
    except Exception as e:
        log_print("ERROR", f"Error in main audio generation process: {str(e)}")
        raise

# if __name__ == "__main__":
#     main(0)
