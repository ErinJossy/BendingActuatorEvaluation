# To Evaluate Bending Soft Actuator
## Camera set up
Ensure your phone and PC is connected to same network and download the [IP Camera](https://play.google.com/store/apps/details?id=com.pas.webcam&pcampaignid=web_share) and launch IP cam server on phone and copy its IP address
## Files included
### hsv_tuner.py
- To find the hsv value of interested object
### bend.py 
- measure the mid line displacement of bending actuator
### ESP32.py 
- read serial data from ESP32 and store values onto a CSV file called data_esp.csv
### correction.py
- calibration code for both sensor
### ESP_Correction.py
- read data from data_esp.csv and apply calibration filter and save to filtered_data.csv
### ESP32 Folder
- ReadFSR: to read FSR value from ESP32
- ReadVL53L0X: to read TOF sensor
