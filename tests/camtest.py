import cv2
import numpy as np

def main():
    # Välj vilken ArUco-ordbok du vill använda
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    # Initiera kameran (anpassa kamerans index om det behövs)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kunde inte öppna kameran")
        return

    print("Tryck 'q' för att avsluta")

    while True:
        # Läs en bild från kameran
        ret, frame = cap.read()
        if not ret:
            print("Misslyckades med att läsa från kameran")
            break

        # Konvertera bilden till gråskala
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Upptäck ArUco-markörer
        corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        # Rita markörer om de hittas
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for marker_id in ids.flatten():
                print(f"Upptäckte ArUco-markör med ID: {marker_id}")

        # Visa bilden
        cv2.imshow('ArUco Detector', frame)

        # Tryck 'q' för att avsluta
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Stäng kameran och fönster
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
