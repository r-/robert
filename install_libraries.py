# Run this program to install all required libraries for robert

import subprocess
import sys

# List of required packages
packages = [
    "flask",
    "flask-cors",
    "opencv-python",
    "opencv-contrib-python",
    "psutil",
    "pyttsx3",
    "buildhat",
    "mpg321",
    "gTTs"
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
