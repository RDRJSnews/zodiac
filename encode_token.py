import base64
import os

def encode_pickle_to_base64():
    try:
        # Read the youtube_token.pickle file in binary mode
        with open('youtube_token.pickle', 'rb') as f:
            pickle_data = f.read()
        
        # Encode to base64
        base64_data = base64.b64encode(pickle_data)
        
        # Convert to string
        base64_string = base64_data.decode('utf-8')
        
        # Print instructions
        print("\n=== YOUTUBE_TOKEN.PICKLE ENCODED SUCCESSFULLY ===")
        print("\nFollow these steps to add to GitHub Secrets:")
        print("1. Go to your GitHub repository")
        print("2. Click Settings > Secrets and variables > Actions")
        print("3. Click 'New repository secret'")
        print("4. Name: YOUTUBE_TOKEN_PICKLE")
        print("5. Value: (copy the encoded string below)")
        print("\n=== ENCODED STRING (copy everything below this line) ===")
        print(base64_string)
        print("=== END OF ENCODED STRING ===\n")
        
        # Also save to a file as backup
        with open('youtube_token.pickle.base64.txt', 'w') as f:
            f.write(base64_string)
        print("Backup saved to youtube_token.pickle.base64.txt")
        
    except FileNotFoundError:
        print("Error: youtube_token.pickle file not found!")
        print("Make sure youtube_token.pickle is in the same directory as this script.")
        print("\nCurrent directory contents:")
        for file in os.listdir('.'):
            if 'token' in file.lower() or 'pickle' in file.lower():
                print(f"- {file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    encode_pickle_to_base64() 