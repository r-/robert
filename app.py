import cv2
import cv2.aruco as aruco
from flask import Flask, jsonify, request
from flask_cors import CORS
from buildhat import Motors

app = Flask(__name__)
CORS(app)
