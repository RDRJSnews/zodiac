from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from zodiac_audio import main as zodiac_audio_main
import librosa
import soundfile as sf
import math
import io
import tempfile
import os
from datetime import datetime
import argparse
import numpy as np

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

def change_audio_speed(input_buffer, speed_factor=1.0):
    """
    Change the playback speed of an audio buffer using librosa and return the audio data.
    """
    log_print("INFO", "=== Starting Audio Speed Change Process ===")
    log_print("INFO", f"Speed factor: {speed_factor}x")
    
    try:
        log_print("INFO", "Creating temporary audio file for processing")
        # Create a temporary file from the audio buffer
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(input_buffer.read())
            temp_file_path = temp_file.name
        
        try:
            log_print("INFO", "Loading audio file with librosa")
            # Load the audio file
            y, sr = librosa.load(temp_file_path, sr=None)
            log_print("INFO", f"Audio loaded successfully. Duration: {len(y)/sr:.2f}s, Sample rate: {sr}Hz")
            
            # Use librosa's time_stretch with the correct parameter name
            # In newer versions of librosa, the parameter is 'rate' not 'rate'
            try:
                log_print("INFO", "Attempting to stretch audio using librosa.effects.time_stretch")
                # Try the newer librosa version approach
                y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
                log_print("INFO", "Audio stretching completed using primary method")
            except TypeError:
                log_print("WARNING", "Primary stretching method failed, trying fallback")
                # Fallback for older versions or different parameter names
                try:
                    y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
                    log_print("INFO", "Audio stretching completed using fallback method 1")
                except:
                    log_print("WARNING", "Fallback method 1 failed, using simple resampling approach")
                    # If all else fails, use a simple resampling approach
                    print("Using fallback method for audio speed change")
                    new_length = int(len(y) / speed_factor)
                    y_stretched = librosa.util.fix_length(y, size=new_length)
                    log_print("INFO", "Audio stretching completed using simple resampling")
            
            # Normalize and boost audio volume
            log_print("INFO", "Normalizing and boosting audio volume")
            # Normalize to prevent clipping
            y_normalized = librosa.util.normalize(y_stretched)
            # Boost volume by multiplying by a factor (adjust this value as needed)
            volume_boost = 2.0  # Increase this value to make audio louder
            y_boosted = y_normalized * volume_boost
            # Clip to prevent distortion
            y_boosted = np.clip(y_boosted, -1.0, 1.0)
            log_print("INFO", f"Audio volume boosted by {volume_boost}x factor")
            
            # Save to bytes buffer instead of file
            log_print("INFO", "Converting stretched audio to buffer")
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, y_boosted, sr, format='WAV')
            audio_buffer.seek(0)
            
            buffer_size = len(audio_buffer.getvalue())
            log_print("INFO", f"Audio buffer created. Size: {buffer_size} bytes")
            log_print("INFO", f"Original duration: {len(y)/sr:.2f}s, New duration: {len(y_stretched)/sr:.2f}s")
            log_print("INFO", "=== Audio Speed Change Completed Successfully ===")
            return audio_buffer
            
        finally:
            # Clean up temporary file
            log_print("INFO", "Cleaning up temporary audio file")
            os.unlink(temp_file_path)
        
    except Exception as e:
        log_print("ERROR", f"Error in audio speed change: {str(e)}")
        raise

def repeat_video_to_match_audio(video_path, audio_buffer):
    """Repeat video to match audio duration and combine them."""
    log_print("INFO", "=== Starting Video-Audio Combination Process ===")
    log_print("INFO", f"Video path: {video_path}")
    
    try:
        log_print("INFO", "Loading video file")
        # Load the video file
        video = VideoFileClip(video_path)
        log_print("INFO", f"Video loaded successfully. Duration: {video.duration:.2f}s, FPS: {video.fps}")
        
        log_print("INFO", "Creating temporary audio file for MoviePy")
        # Create a temporary file from the audio buffer for MoviePy
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio_file:
            temp_audio_file.write(audio_buffer.read())
            temp_audio_path = temp_audio_file.name
        
        try:
            log_print("INFO", "Loading audio file with MoviePy")
            audio = AudioFileClip(temp_audio_path)  # MoviePy still needs FFmpeg here, but only for reading
            log_print("INFO", f"Audio loaded successfully. Duration: {audio.duration:.2f}s")
            
            # Get durations
            video_duration = video.duration
            audio_duration = audio.duration
            
            log_print("INFO", f"Video duration: {video_duration:.2f}s")
            log_print("INFO", f"Audio duration: {audio_duration:.2f}s")
            log_print("INFO", f"Using audio file: {temp_audio_path}")
            
            # Calculate how many times we need to repeat the video
            num_repeats = math.ceil(audio_duration / video_duration)
            log_print("INFO", f"Number of video repeats needed: {num_repeats}")
            
            # Create a list of repeated video clips
            log_print("INFO", "Creating repeated video clips")
            repeated_clips = [video] * num_repeats
            
            # Concatenate all the clips
            log_print("INFO", "Concatenating video clips")
            final_video = concatenate_videoclips(repeated_clips)
            log_print("INFO", f"Video concatenation completed. Duration: {final_video.duration:.2f}s")
            
            # Set the audio of the final video
            log_print("INFO", "Setting audio to final video")
            final_video = final_video.set_audio(audio)
            
            # Trim the video to exactly match the audio duration
            log_print("INFO", "Trimming video to match audio duration")
            final_video = final_video.subclip(0, audio_duration)
            
            log_print("INFO", f"Final video duration: {final_video.duration:.2f}s")
            
            # Write to a temporary file instead of buffer
            log_print("INFO", "Writing final video to temporary file")
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video_file:
                temp_video_path = temp_video_file.name

            final_video.write_videofile(
                temp_video_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                verbose=False
            )

            # Read the file into a buffer
            with open(temp_video_path, 'rb') as f:
                video_buffer = io.BytesIO(f.read())

            # Clean up the temp file
            os.unlink(temp_video_path)
            log_print("INFO", f"Video buffer created successfully. Size: {video_buffer.getbuffer().nbytes} bytes")
            
            # Close the clips to free resources
            log_print("INFO", "Cleaning up video and audio resources")
            video.close()
            audio.close()
            final_video.close()
            
            log_print("INFO", "=== Video-Audio Combination Completed Successfully ===")
            return video_buffer
            
        finally:
            # Clean up temporary audio file
            log_print("INFO", "Cleaning up temporary audio file")
            os.unlink(temp_audio_path)
        
    except Exception as e:
        log_print("ERROR", f"Error in video-audio combination: {str(e)}")
        raise

def main(lang_code=0):
    """Main function to generate zodiac video. lang_code=0 for Tamil, 1 for English."""
    log_print("INFO", "=== Starting Zodiac Video Generation Process ===")
    try:
        video_path = "template.mp4"
        log_print("INFO", f"Using template video: {video_path}")

        log_print("INFO", f"Calling zodiac_audio_main to generate audio (lang_code={lang_code})")
        audio_buffer = zodiac_audio_main(lang_code) # 0 for Tamil, 1 for English

        if not audio_buffer:
            log_print("ERROR", "No audio buffer received from zodiac_audio_main")
            raise Exception("Audio generation failed")

        log_print("INFO", "Audio buffer received successfully")

        speed = 1.5  # 1.5x speed (change this value as needed)
        log_print("INFO", f"Applying speed factor: {speed}x")

        log_print("INFO", "Processing audio speed change")
        audio_speeded_buffer = change_audio_speed(audio_buffer, speed)

        log_print("INFO", "Combining video and audio")
        final_video_buffer = repeat_video_to_match_audio(video_path, audio_speeded_buffer)

        log_print("INFO", "=== Zodiac Video Generation Completed Successfully ===")
        return final_video_buffer

    except Exception as e:
        log_print("ERROR", f"Error in main video generation process: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate zodiac video in Tamil or English.")
    parser.add_argument('--lang', type=str, default='ta', choices=['ta', 'en-in', 'hi'], help='Language code: ta for Tamil, en-in for English, hi for Hindi')
    args = parser.parse_args()
    lang_map = {'ta': 0, 'en-in': 1, 'hi': 2}
    lang_code = lang_map.get(args.lang, 0)
    try:
        video_buffer = main(lang_code=lang_code)
        if not video_buffer:
            log_print("ERROR", "No video data generated!")
            exit(1)
        log_print("INFO", "Video generated successfully!")
        # Save the video buffer to the correct file
        output_map = {0: "output_video.mp4", 1: "output_video_1.mp4", 2: "output_video_2.mp4"}
        output_file = output_map.get(lang_code, "output_video.mp4")
        with open(output_file, "wb") as f:
            f.write(video_buffer.getbuffer())
        log_print("INFO", f"Video saved to {output_file}")
    except Exception as e:
        log_print("ERROR", f"An error occurred in the video generation workflow: {str(e)}")
        raise
    