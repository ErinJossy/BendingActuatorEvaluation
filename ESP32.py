import serial
import re
import time
import csv


SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 115200           
TIMEOUT_SEC = 1            

# --- Regular Expression to parse the line ---
# This pattern looks for the specific keys and captures the values
# It handles potential whitespace variations and the "NaN" value for distance.
# Groups captured: 1: Distance value, 2: FSR value, 3: Time value
# r"Distance\(mm\):\s*([\d\.]+|NaN)\s+FSR Reading:\s*(\d+)\s+Time\(ms\):\s*(\d+)"
line_pattern = re.compile(
    r"Distance\(mm\):\s*([\d\.]+|NaN)\s+"  # Key 1, Value 1 (number, dot, or NaN)
    r"FSR Reading:\s*(\d+)\s+"             # Key 2, Value 2 (integer)
    r"Time\(ms\):\s*(\d+)"                 # Key 3, Value 3 (integer)
)

def parse_serial_data(line):
    """
    Parses a line of serial data using the predefined regex pattern.
    Returns a dictionary with parsed data or None if parsing fails.
    """
    match = line_pattern.search(line)
    if match:
        try:
            distance_str = match.group(1)
            fsr_str = match.group(2)
            time_str = match.group(3)

            # Convert values to appropriate types
            # Handle NaN specifically for distance
            if distance_str.upper() == 'NAN':
                distance_mm = float('nan') # Use Python's NaN representation
            else:
                distance_mm = float(distance_str)

            fsr_reading = int(fsr_str)
            time_ms = int(time_str)

            return {
                "distance_mm": distance_mm,
                "fsr_reading": fsr_reading,
                "time_ms": time_ms
            }
        except (ValueError, IndexError) as e:
            print(f"Error converting parsed values: {e} in line: '{line}'")
            return None
    else:
        # Optional: Print lines that don't match the expected format
        # if line: # Avoid printing blank lines resulting from timeouts etc.
        #    print(f"Warning: Line did not match expected format: '{line}'")
        return None

def read_serial(port, baudrate, timeout):
    """
    Continuously reads from the specified serial port and parses the data.
    """
    with open('data_esp.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['distance mm', 'fsr reading', 'time ms'])
    print(f"Attempting to connect to {port} at {baudrate} baud...")
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            print(f"Successfully connected to {port}. Reading data...")
            while True:
                try:
                    # Read one line, including the newline character
                    line_bytes = ser.readline()

                    if line_bytes:
                        # Decode bytes to string (assuming utf-8 encoding)
                        # Use 'ignore' or 'replace' for errors if needed
                        line_str = line_bytes.decode('utf-8', errors='ignore').strip()

                        if line_str: # Check if the line is not empty after stripping
                            parsed_data = parse_serial_data(line_str)
                            if parsed_data:
                                print(f"Received Data: {parsed_data}")
                                with open('data_esp.csv', 'a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([parsed_data['distance_mm'], parsed_data['fsr_reading'], parsed_data['time_ms']])
                except serial.SerialException as e:
                    print(f"Serial error: {e}")
                    print("Attempting to reconnect...")
                    time.sleep(2) # Wait before retrying connection within the loop
                    # Break or continue based on desired behavior on error
                    break # Exit the inner loop to let the outer try handle reconnect (if applicable)
                except KeyboardInterrupt:
                    print("\nStopping reader...")
                    break # Exit the loop cleanly on Ctrl+C

    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        print("Please check the port name, permissions, and connections.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    read_serial(SERIAL_PORT, BAUD_RATE, TIMEOUT_SEC)