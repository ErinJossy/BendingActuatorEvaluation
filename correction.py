m = 0.9354282684 #slope from linear regression for the distance
b = -5.905816318 #intercept from linear regression for the distance

import numpy as np

# Your raw calibration data
# List of tuples: (Actual Weight (g), Measured ADC Value)
raw_data = [
    (50, 2956),
    (100, 3583),
    (200, 3948),
    (50, 3030),
    (100, 3345),
    (200, 3804),
    (100, 3402),
    (0, 0)      # Added the 0g reading
]

# --- Data Processing: Group and Average ---
calibration_points = {} # Dictionary to store {weight: [list of ADC readings]}


def parse_weight_data():
    """
    Parse the raw calibration data and return two arrays: adc_cal_points and weight_cal_points.
    
    adc_cal_points is an array of average ADC values from the calibration data, sorted by ADC value.
    weight_cal_points is an array of corresponding weights (in grams), sorted by ADC value.
    """
    for weight, adc in raw_data:
        if weight not in calibration_points:
            calibration_points[weight] = []
        calibration_points[weight].append(adc)

    # Calculate average ADC for each weight and store as (ADC_avg, Weight) tuples
    # We sort by ADC value for interpolation later
    averaged_data = []
    for weight, adc_list in calibration_points.items():
        avg_adc = np.mean(adc_list)
        averaged_data.append((avg_adc, weight)) # Store as (ADC, Weight)

    # Sort the data based on the average ADC reading (important for interpolation)
    averaged_data.sort()

    # Separate into two lists/arrays for easier use with numpy functions
    adc_cal_points = np.array([adc for adc, weight in averaged_data])
    weight_cal_points = np.array([weight for adc, weight in averaged_data])
    return adc_cal_points, weight_cal_points

def estimate_weight_interpolation(adc_reading, adc_cal, weight_cal):
    """
    Estimates weight based on ADC reading using linear interpolation.

    Args:
        adc_reading (float or int): The current ADC reading from the FSR.
        adc_cal (np.array): Sorted array of ADC values from calibration.
        weight_cal (np.array): Corresponding array of weights from calibration.

    Returns:
        float: Estimated weight in grams. Handles readings outside the
               calibration range by returning the min/max calibrated weight.
    """
    estimated_weight = np.interp(adc_reading, adc_cal, weight_cal)
    return estimated_weight


def correct_distance(distance):
    """
    Correct the distance measured from the lidar to account for the non-linear relationship between distance and voltage.

    Parameters
    ----------
    distance : float
        The distance measured by the lidar in inches.

    Returns
    -------
    float
        The corrected distance in inches.
    """
    return m * distance + b




def correct_fsr(fsr):
    """
    Correct the FSR reading to account for the non-linear relationship between FSR and voltage.

    Parameters
    ----------
    fsr : float
        The FSR reading.

    Returns
    -------
    float
        The corrected FSR reading.
    """
    adc_cal, weight_cal = parse_weight_data()
    return estimate_weight_interpolation(fsr, adc_cal, weight_cal)
#     # Correct the FSR reading using the linear regression model

