import cv2
import numpy as np
import time
import math

# --- Configuration ---
# Replace with your IP camera's stream URL (RTSP, HTTP, etc.)
# Examples:
# ip_camera_url = "rtsp://username:password@ip_address:port/stream_path"
# ip_camera_url = "http://ip_address:port/video.mjpg"
ip_camera_url = "http://192.168.50.118:8080/video" # Use 0 for default webcam, replace with your URL

# HSV Color Range for the GREEN actuator (NEEDS CAREFUL TUNING)
# Use a color picker tool (like GIMP, online tools, or a dedicated script)
# to find the HSV values for your specific actuator green under your lighting.
# Format: [Hue, Saturation, Value]
lower_green = np.array([41, 99, 102])  # Example lower bound
upper_green = np.array([179, 255, 255]) # Example upper bound

# Number of points to track along the neutral axis
NUM_POINTS = 10

# Minimum contour area to filter out noise
MIN_CONTOUR_AREA = 500

# --- Global Variables ---
reference_points = None
reference_axis_endpoints = None
is_reference_set = False

# --- Helper Functions ---

def find_actuator_and_axis(frame, lower_color, upper_color, min_area):
    """
    Finds the largest green contour, calculates its minimum area rectangle,
    and determines the endpoints of its neutral axis (centerline).
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Optional: Morphological operations to clean up mask
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None, None # No contours found

    # Find the largest contour assuming it's the actuator
    largest_contour = max(contours, key=cv2.contourArea)

    if cv2.contourArea(largest_contour) < min_area:
        return None, None, None # Largest contour is too small

    # Get the minimum area rectangle bounding the contour
    # rect = ((center_x, center_y), (width, height), angle)
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect) # Get the 4 corners of the rectangle
    box = box.astype(np.int32) # Get the 4 corners of the rectangle (as integers)
# Or alternatively: box = box.astype(int)

    # Calculate neutral axis endpoints (midpoints of the shorter sides)
    center, (w, h), angle = rect
    if w > h: # Ensure height is the longer dimension for a vertical actuator
         w, h = h, w
         angle += 90 # Adjust angle accordingly

    # Calculate endpoints based on center, height (length), and angle
    # Angle from minAreaRect is degrees, convert to radians for trig functions
    angle_rad = math.radians(angle)
    dx = 0.5 * h * math.cos(angle_rad)
    dy = 0.5 * h * math.sin(angle_rad)

    # Correcting endpoint calculation based on angle definition
    # A more robust way is using the corners (boxPoints)
    # Find the two shortest sides
    side1_len = np.linalg.norm(box[0] - box[1])
    side2_len = np.linalg.norm(box[1] - box[2])

    if side1_len < side2_len: # side 0-1 and 2-3 are shorter
        mid1 = (box[0] + box[1]) / 2
        mid2 = (box[2] + box[3]) / 2
    else: # side 1-2 and 3-0 are shorter
        mid1 = (box[1] + box[2]) / 2
        mid2 = (box[3] + box[0]) / 2

    # Ensure consistent direction (e.g., always top-to-bottom or bottom-to-top)
    # Let's assume the actuator bends primarily horizontally, so check y-coords
    if mid1[1] > mid2[1]: # If mid1 is lower than mid2, swap them
         mid1, mid2 = mid2, mid1

    endpoint1 = tuple(mid1.astype(np.int32))
    endpoint2 = tuple(mid2.astype(np.int32))
    # Or alternatively:
    # endpoint1 = tuple(mid1.astype(int))
    # endpoint2 = tuple(mid2.astype(int))

    # Ensure endpoint1 is always the 'start' (e.g., lowest y if mostly vertical)
    # This helps maintain correspondence
    if endpoint1[1] > endpoint2[1]:
         endpoint1, endpoint2 = endpoint2, endpoint1


    return largest_contour, rect, (endpoint1, endpoint2)


def get_points_on_axis(endpoints, num_points):
    """
    Linearly interpolates points along the line segment defined by endpoints.
    """
    pt1, pt2 = np.array(endpoints[0]), np.array(endpoints[1])
    if num_points < 2:
        return [tuple(((pt1 + pt2) / 2).astype(int))]
    points = [tuple(pt1.astype(int))] # Include start point
    for i in range(1, num_points):
        fraction = i / (num_points -1) # Correct interpolation factor
        interpolated_point = pt1 + fraction * (pt2 - pt1)
        points.append(tuple(interpolated_point.astype(int)))
    # points = [tuple((pt1 + (pt2 - pt1) * i / (num_points - 1)).astype(int)) for i in range(num_points)]
    return points

# --- Main Loop ---

cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print(f"Error: Could not open video stream at {ip_camera_url}")
    exit()

print("Video stream opened successfully.")
print("Press 's' to set the current frame as the reference (undeflected) state.")
print("Press 'r' to reset the reference state.")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame or stream ended.")
        # Optional: Attempt to reconnect
        # cap.release()
        # time.sleep(5)
        # cap = cv2.VideoCapture(ip_camera_url)
        # if not cap.isOpened():
        #    print("Reconnect failed. Exiting.")
        #    break
        # continue
        break # Exit if frame grab fails

    # --- Find Actuator and Current Axis ---
    contour, rect, current_axis_endpoints = find_actuator_and_axis(
        frame, lower_green, upper_green, MIN_CONTOUR_AREA
    )

    display_frame = frame.copy() # Draw on a copy

    if contour is not None:
        # Draw the contour and bounding box
        cv2.drawContours(display_frame, [contour], -1, (0, 255, 0), 1)
        box = cv2.boxPoints(rect)
        box = box.astype(np.int32)
# Or alternatively: box = box.astype(int)
        cv2.drawContours(display_frame, [box], 0, (255, 0, 0), 1)

        # Draw the current neutral axis
        cv2.line(display_frame, current_axis_endpoints[0], current_axis_endpoints[1], (0, 0, 255), 2) # Red line for current axis

        # Calculate current points
        current_points = get_points_on_axis(current_axis_endpoints, NUM_POINTS)

        # Draw current points
        for pt in current_points:
            cv2.circle(display_frame, pt, 4, (255, 255, 0), -1) # Cyan circles

        # --- Displacement Calculation (if reference is set) ---
        if is_reference_set:
            if len(current_points) == len(reference_points):
                total_deflection = 0
                for i in range(NUM_POINTS):
                    ref_pt = np.array(reference_points[i])
                    curr_pt = np.array(current_points[i])
                    # Calculate Euclidean distance
                    displacement = np.linalg.norm(curr_pt - ref_pt)
                    total_deflection += displacement

                    # Draw line connecting reference point (visualized) to current point
                    # For visualization, draw reference points slightly offset or in a fixed position if needed
                    # Here, just draw line from calculated current point back towards where reference *was*
                    # A better viz might draw the original axis faintly
                    # Draw line from reference to current
                    cv2.line(display_frame, reference_points[i], current_points[i], (255, 255, 255), 1)
                    # Display displacement value near the current point
                    cv2.putText(display_frame, f"{displacement:.1f}",
                                (current_points[i][0] + 10, current_points[i][1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                # Display average or total deflection (optional)
                avg_deflection = total_deflection / NUM_POINTS
                cv2.putText(display_frame, f"Avg Defl: {avg_deflection:.1f} px", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Draw the reference axis faintly for comparison
            cv2.line(display_frame, reference_axis_endpoints[0], reference_axis_endpoints[1], (0, 255, 255, 100), 1) # Faint yellow

    else:
        cv2.putText(display_frame, "Actuator not found", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # --- Display Instructions ---
    if not is_reference_set:
        cv2.putText(display_frame, "Press 's' to set reference", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
         cv2.putText(display_frame, "Reference SET. Press 'r' to reset.", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


    # --- Show the frame ---
    cv2.imshow("Actuator Deflection Analysis", display_frame)

    # --- Handle User Input ---
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Quitting...")
        break
    elif key == ord('s'):
        if contour is not None:
            reference_axis_endpoints = current_axis_endpoints
            reference_points = get_points_on_axis(reference_axis_endpoints, NUM_POINTS)
            is_reference_set = True
            print(f"Reference state set with {len(reference_points)} points.")
        else:
            print("Cannot set reference: Actuator not found in current frame.")
    elif key == ord('r'):
        reference_points = None
        reference_axis_endpoints = None
        is_reference_set = False
        print("Reference state reset.")

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()