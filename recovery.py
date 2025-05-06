import os
import csv

white_folder = './output/white_backgrounds'
review_folder = './output/white_backgrounds_review'
remaining_folder = './output/cleaned_images'
log_path = './data/white_background_log.csv'

log_data = []

for f in os.listdir(white_folder):
    log_data.append([f, 'Moved (White)'])

for f in os.listdir(review_folder):
    log_data.append([f, 'Moved (Review)'])

for f in os.listdir(remaining_folder):
    log_data.append([f, 'Not Moved'])

with open(log_path, 'w', newline='', encoding='utf-8') as log_file:
    writer = csv.writer(log_file)
    writer.writerow(['Filename', 'Status'])
    writer.writerows(log_data)

print("✅ Rebuilt log saved.")
