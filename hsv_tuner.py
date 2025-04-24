import cv2
import numpy as np

# --- Configuration ---
# Replace with your IP camera's stream URL or use 0 for default webcam
ip_camera_url = "http://192.168.50.118:8080/video" # Use 0 for default webcam

# --- Callback function for trackbars (does nothing, needed by createTrackbar) ---
def nothing(x):
    pass

# --- Setup ---
# Create a window for the trackbars
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 400, 300) # Adjust size as needed

# Create trackbars for lower HSV bounds
# Hue range is 0-179 in OpenCV
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)

# Create trackbars for upper HSV bounds
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

# --- Video Capture ---
cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print(f"Error: Could not open video stream at {ip_camera_url}")
    exit()

print("Video stream opened.")
print("Adjust trackbars until the 'Mask' window shows your object in white.")
print("Press 'q' to quit and print the final values.")

lower_h, lower_s, lower_v = 0, 0, 0
upper_h, upper_s, upper_v = 179, 255, 255

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame or stream ended.")
        break

    # Optional: Resize frame for performance if needed
    # frame = cv2.resize(frame, (640, 480))

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get current positions from trackbars
    lower_h = cv2.getTrackbarPos("L - H", "Trackbars")
    lower_s = cv2.getTrackbarPos("L - S", "Trackbars")
    lower_v = cv2.getTrackbarPos("L - V", "Trackbars")
    upper_h = cv2.getTrackbarPos("U - H", "Trackbars")
    upper_s = cv2.getTrackbarPos("U - S", "Trackbars")
    upper_v = cv2.getTrackbarPos("U - V", "Trackbars")

    # Create numpy arrays for the lower and upper bounds
    lower_bound = np.array([lower_h, lower_s, lower_v])
    upper_bound = np.array([upper_h, upper_s, upper_v])

    # Create the mask using the bounds
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # --- Optional: Apply morphological operations to clean the mask ---
    # kernel = np.ones((5,5),np.uint8)
    # mask = cv2.erode(mask, kernel, iterations = 1)
    # mask = cv2.dilate(mask, kernel, iterations = 1)
    # -----------------------------------------------------------------

    # --- Optional: Show the result of masking on the original image ---
    result = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow("Result (Mask Applied)", result)
    # -----------------------------------------------------------------

    # Display the original frame and the mask
    cv2.imshow("Original Frame", frame)
    cv2.imshow("Mask", mask)

    # Print current bounds to console (optional, but helpful during tuning)
    # print(f"\rLower: [{lower_h:3d}, {lower_s:3d}, {lower_v:3d}], Upper: [{upper_h:3d}, {upper_s:3d}, {upper_v:3d}]", end="")


    # Check for 'q' key press to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()

# Print the final selected values
print("\n--- Final HSV Bounds ---")
print(f"lower_green = np.array([{lower_h}, {lower_s}, {lower_v}])")
print(f"upper_green = np.array([{upper_h}, {upper_s}, {upper_v}])")