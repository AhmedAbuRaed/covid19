import json
import os
import csv
import argparse

# Function to process files based on the region
def process_files(region):
    # Subdirectory name for output files
    base_subdirectory = "../output"
    sentiment_output_dir = os.path.join(base_subdirectory, "sentiment_output")

    # Create the sentiment_output directory if it doesn't exist
    if not os.path.exists(sentiment_output_dir):
        os.makedirs(sentiment_output_dir)

    # List of file names in the subdirectory based on the region
    short_months = ["jan", "feb", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    full_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    if region == "Canada":
        file_names = [f"pipeline_monthly_canada_{month}_output.csv" for month in short_months]
    elif region == "US":
        file_names = [f"pipeline_monthly_us_{month}_output.csv" for month in short_months]
    elif region == "EU_UK":
        file_names = [f"pipeline_monthly_EU_UK_{month}_output.csv" for month in short_months]
    else:
        print("Invalid region specified.")
        return

    # List to store data for each file
    file_data = []

    # Iterate over the file names and corresponding full month names
    for index, (file_name, full_month) in enumerate(zip(file_names, full_months), start=1):
        # Construct the full file path with the subdirectory
        file_path = os.path.join(base_subdirectory, file_name)

        try:
            # Open the CSV file in read mode
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                positive = 0
                negative = 0
                neutral = 0

                for row in reader:
                    tweet_info = row  # Assuming each row is a valid dictionary

                    if 'sentiment_confidence' not in tweet_info:
                        print(f"Error: 'sentiment_confidence' key not found in row: {row}")
                        continue

                    tweet_info['sentiment_confidence'] = float(tweet_info['sentiment_confidence'])
                    if tweet_info['sentiment_confidence'] < 0.66:
                        tweet_info['sentiment'] = "Neutral"
                        neutral += 1
                    else:
                        if tweet_info['sentiment'] == 'LABEL_0':
                            tweet_info['sentiment'] = 'Positive'
                            positive += 1
                        elif tweet_info['sentiment'] == 'LABEL_1':
                            tweet_info['sentiment'] = 'Negative'
                            negative += 1

                # Append data for the current file to the list
                file_data.append({'Month': full_month, 'Positive': positive, 'Negative': negative, 'Neutral': neutral})

        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred while reading {file_path}: {e}")

    # Write the results to a CSV file
    output_csv_path = os.path.join(sentiment_output_dir, f"monthly_sentiment_counts_per_month_{region.lower()}.csv")

    header = ['Month', 'Positive', 'Negative', 'Neutral']

    with open(output_csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        writer.writerows(file_data)

    print(f"CSV file '{output_csv_path}' created successfully.")

# Argument parser for region selection
parser = argparse.ArgumentParser(description="Process sentiment analysis files for different regions.")
parser.add_argument('region', choices=['Canada', 'US', 'EU_UK'], help='Region to process (Canada, US, EU_UK)')
args = parser.parse_args()

# Process files based on the selected region
process_files(args.region)
