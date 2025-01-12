# smart-surveillance-system-
smart surveillance system using image processing for security


# Smart Surveillance System

This project is a Python-based smart surveillance system that uses computer vision to detect motion and classify potential threats, such as weapons, in a video feed. It also integrates Twilio's messaging service to send alerts in real time.

## Features

- **Motion Detection**: Identifies and highlights areas with significant movement.
- **Weapon Detection**: Detects weapon-like objects (e.g., guns, knives) based on contours and aspect ratios.
- **Real-time Alerts**: Sends SMS alerts using Twilio API when a potential threat is detected.
- **Image and Video Recording**: Saves frames and videos of detected threats.
- **Full-Screen Display**: Displays live surveillance feed in full-screen mode with overlayed details.

## Requirements

### Hardware
- A computer with a webcam (or an external camera).

### Software
- Python 3.x
- Required Python libraries (listed below)

### Python Libraries
Install the required libraries using the following command:
```bash
pip install opencv-python opencv-python-headless numpy imutils twilio
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Twilio:
   - Create a [Twilio](https://www.twilio.com/) account.
   - Obtain your **Account SID** and **Auth Token**.
   - Update the `account_sid` and `auth_token` variables in the script with your Twilio credentials.
   - Add your Twilio trial number and recipient's phone number in the `info_dict` dictionary.

4. Run the script:
   ```bash
   python surveillance_system.py
   ```

## How It Works

1. The system captures video feed from the default webcam.
2. It uses a background subtractor to detect motion and contours to identify weapon-like shapes.
3. If a weapon is detected:
   - An SMS alert is sent to the specified phone number.
   - The frame and video are saved for further analysis.
4. If no weapon is detected, the system displays "Normal Activity" on the live feed.

## Directory Structure

```
<repository-folder>/
|-- motion_images/      # Saved images of detected threats
|-- motion_videos/      # Saved videos of detected threats
|-- surveillance_system.py   # Main script
|-- README.md           # Documentation (this file)
|-- requirements.txt    # Python dependencies
```

## Customization

- **Motion Sensitivity**: Adjust the `cv2.contourArea` threshold to ignore smaller movements.
- **Weapon Detection**: Modify the `classify_weapon` function to classify other objects.
- **Alert Frequency**: Change `alert_threshold` to adjust the interval between alerts.
- **Recording Resolution**: Change the video frame size in `cv2.VideoWriter`.

## Notes

- Ensure your camera is properly connected and accessible by the script.
- The system requires internet access to send SMS alerts via Twilio.
- For production use, ensure secure storage of Twilio credentials.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgments

- [OpenCV](https://opencv.org/) for computer vision functionality.
- [Twilio](https://www.twilio.com/) for SMS alert integration.
