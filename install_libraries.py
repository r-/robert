# NOTE: For TTS type "sudo apt-get install mpg321" into command-terminal

# Run this program to install all required libraries for robert

import subprocess
import sys

# List of required packages
packages = [
    "annotated-types",
"anyio",
"bidict",
"blinker",
"buildhat",
"certifi",
"charset-normalizer",
"click",
"colorzero",
"distro",
"Flask",
"flask-cors",
"Flask-SocketIO",
"gpiozero",
"gTTS",
"h11",
"httpcore",
"httpx",
"idna",
"itsdangerous",
"Jinja2",
"jiter",
"MarkupSafe",
"netifaces",
"numpy",
"openai",
"opencv-contrib-python",
"opencv-python",
"pip",
"psutil",
"pydantic",
"pydantic_core",
"pyserial",
"python-engineio",
"python-socketio",
"pyttsx3",
"pyzbar",
"requests",
"setuptools",
"simple-websocket",
"sniffio",
"SpeechRecognition",
"tqdm",
"typing_extensions",
"typing-inspection",
"urllib3",
"Werkzeug",
"wsproto"
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
