import csv 
import correction

distance_unfiltered = []
FSR_unfiltered = []
FSR_filtered = []
distance_filtered = []
time = []


with open('filtered_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['distance mm', 'fsr  (grams)', 'time ms'])
                        

with open('data_esp.csv', 'r', newline='') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header row
    for row in reader:
        FSR_unfiltered.append(int(row[1]))
        distance_unfiltered.append(float(row[0]))
        time.append(int(row[2]))
        with open('filtered_data.csv', 'a', newline='') as file2:
            writer = csv.writer(file2)
            writer.writerow([correction.correct_distance(float(row[0])), correction.correct_fsr(int(row[1])), int(row[2])])
