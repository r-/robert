# R.O.B.E.R.T
**Robotic Overlord Bent on Enslaving and Ruling Technology**  
*You can call me Robby.*

---

## Overview
R.O.B.E.R.T is a robotics project designed to showcase the integration of **Raspberry Pi** with **LEGO components** and **AI-powered image recognition**, controlled through a web dashboard. This system explores the synergy between hardware and software in an engaging and educational way.

For a user interface to monitor and control R.O.B.E.R.T, check out the [R.O.B.E.R.T Control Dashboard project](https://github.com/r-/robert-control).

---

## Built With

### Hardware
- **Raspberry Pi** – The core controller for R.O.B.E.R.T's operations
- **BuildHAT** – Provides seamless integration with LEGO motors and sensors
- **LEGO Motors and Sensors** – Drive and sensor capabilities using LEGO’s flexible components
- **USB or Pi Camera** – For vision and object recognition
- **Coral USB Accelerator** – Adds AI processing power for real-time image recognition

### Software

#### Python
- **Flask** – API to handle requests and enable communication between the hardware and the web dashboard
- **OpenCV** – For computer vision tasks, including object detection and recognition

#### PHP
- **Control Dashboard** – A PHP-based dashboard to monitor and control R.O.B.E.R.T’s functions remotely

---

## Setup

### Prerequisites
- Raspberry Pi with Raspberry Pi OS installed
- Python 3.x and required packages (see requirements.txt)
- PHP and a web server (e.g., Apache) for hosting the control dashboard

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/r-/robert.git
   cd robert
