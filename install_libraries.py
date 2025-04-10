# NOTE: For TTS type "sudo apt-get install mpg321" into command-terminal

# Run this program to install all required libraries for robert

import subprocess
import sys

# List of required packages
packages = [
"buildhat",
"Flask",
"flask-cors",
"gTTS",
"netifaces",
"numpy",
"openai",
"opencv-contrib-python",
"opencv-python",
"psutil",
"pyttsx3",
"pyzbar",
"requests",
"SpeechRecognition",
"urllib3",
"Werkzeug",
]

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")

def main():
    print("🚀 Installing required packages...\n")
    for package in packages:
        install_package(package)
    
    print("\n🎉 All packages installed! You're ready to go.")

if __name__ == "__main__":
    main()
