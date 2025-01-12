import cv2
import numpy as np
from twilio.rest import Client
import imutils
import time
import os
from datetime import datetime

# Twilio account SID and Auth Token
account_sid = 'Your account sid'
auth_token = 'Your account token'

# Info dictionary containing valid phone numbers
info_dict = {
    'your_num': '+91            ',  # Replace with the recipient's valid phone number
    'trial_num': '+1            ',  # Replace with your Twilio trial phone number
}

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Create a directory to save images and videos if they don't exist
if not os.path.exists('motion_images'):
    os.makedirs('motion_images')

if not os.path.exists('motion_videos'):
    os.makedirs('motion_videos')

# Initialize video capture (webcam)
cap = cv2.VideoCapture(0)  # 0 is default webcam
time.sleep(2)  # Allow camera to initialize

# Set up Background Subtractor for motion detection
fgbg = cv2.createBackgroundSubtractorMOG2()

motion_detected = False
image_saved = False  # Flag to track if image has been saved
last_alert_time = time.time()
alert_threshold = 60  # Time interval between consecutive alerts (in seconds)

image_counter = 0  # For naming saved images
video_writer = None  # Initialize the video writer to None

# Speed thresholds (in pixels per frame)
fast_speed_threshold = 30  # Minimum distance moved between frames to detect fast movement
very_fast_speed_threshold = 60  # Minimum distance moved for very fast movement (abnormal activity)

# Create a window in full screen
cv2.namedWindow("Surveillance System", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Surveillance System", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Flag to track if the initial SMS has been sent
initial_sms_sent = False

# Helper function to classify weapons based on their shape and size
def classify_weapon(frame, contour):
    # Get the bounding box for the contour
    (x, y, w, h) = cv2.boundingRect(contour)

    # Aspect ratio (length / height ratio) for classification
    aspect_ratio = float(w) / h
    if aspect_ratio > 2:  # Gun-like shape: long and narrow
        cv2.putText(frame, "Possible Gun Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        return "Gun"
    
    elif 1.5 < aspect_ratio < 2:  # Knife-like shape: smaller but still elongated
        cv2.putText(frame, "Possible Knife Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        return "Knife"
    
    # Add other shape classifications if needed
    else:
        cv2.putText(frame, "Unidentified Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return "Unknown"

# Helper function to detect weapon-like shapes based on contour and aspect ratio
def detect_weapon(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)  # Detect edges using Canny edge detector

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    weapon_detected = False
    detected_weapon_type = "Unknown"

    for contour in contours:
        if cv2.contourArea(contour) < 1000:  # Ignore small contours
            continue

        # Classify weapon based on contour
        detected_weapon_type = classify_weapon(frame, contour)
        if detected_weapon_type != "Unknown":
            weapon_detected = True

    return weapon_detected, detected_weapon_type

# Main loop for video capture and processing
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for better processing performance
    frame = imutils.resize(frame, width=500)

    # Apply background subtraction to detect motion
    fgmask = fgbg.apply(frame)
    
    # Convert mask to binary (black and white)
    _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

    # Find contours (areas with movement)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_centroids = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Reset motion detection flag for the current frame
    detected_abnormal_activity = False
    detected_weapon = False
    weapon_type = "Unknown"

    # Iterate through detected contours (motion regions)
    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Ignore small movements (less than 500 pixels area)
            continue
        
        # Get the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Check if there's any weapon detected in the frame
        detected_weapon, weapon_type = detect_weapon(frame)

    # If a weapon is detected, trigger the alert and display message
    if detected_weapon:
        print(f"{weapon_type} detected in the frame!")
        cv2.putText(frame, f"{weapon_type} Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Send SMS alert about weapon detection
        if not initial_sms_sent:
            message = client.messages.create(
                to=info_dict['your_num'],
                from_=info_dict['trial_num'],
                body=f"{weapon_type} detected! Check your surveillance system."
            )
            print(f"Alert sent with SID: {message.sid}")
            initial_sms_sent = True  # Mark that the initial SMS has been sent

        # Optionally, save image or video if weapon detected
        if not image_saved:
            image_filename = f"motion_images/{weapon_type.lower()}_{image_counter}.jpg"
            cv2.imwrite(image_filename, frame)
            print(f"Image saved as {image_filename}")
            image_counter += 1
            image_saved = True  # Set the flag to true after saving the image
        
        # Start video recording if not already recording
        if video_writer is None:
            video_filename = f"motion_videos/{weapon_type.lower()}_{image_counter}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
            print(f"Started video recording: {video_filename}")
        
        # Write the current frame to the video
        video_writer.write(frame)

    else:
        # Display "Normal Activity" text on the frame if no weapon detected
        cv2.putText(frame, "Normal Activity", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Stop video recording if no weapon detected and video is being recorded
        if video_writer is not None:
            video_writer.release()
            video_writer = None
            print("Stopped video recording.")

    # Display current date and time on the frame
    cv2.putText(frame, f"Date & Time: {current_time}", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame with motion and edges in full screen
    cv2.imshow('Surveillance System', frame)

    # Reset the motion detection flag after processing
    motion_detected = False  # Reset flag for the next frame

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close OpenCV windows
cap.release()
if video_writer is not None:
    video_writer.release()  # Release the video writer if recording
cv2.destroyAllWindows()  # Close all OpenCV windows
