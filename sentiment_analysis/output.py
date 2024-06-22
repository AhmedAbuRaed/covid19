import json
import os
import csv

# Subdirectory name
subdirectory = "output"

# List of file names in the subdirectory
file_names = ["falcon_sa_tweets_canada_en_0_output_sent.txt", "falcon_sa_tweets_canada_en_1_output_sent.txt",
              "falcon_sa_tweets_canada_en_2_output_sent.txt", "falcon_sa_tweets_canada_en_3_output_sent.txt",
              "falcon_sa_tweets_canada_en_4_output_sent.txt", "falcon_sa_tweets_canada_en_5_output_sent.txt",
              "falcon_sa_tweets_canada_en_6_output_sent.txt", "falcon_sa_tweets_canada_en_7_output_sent.txt",
              "falcon_sa_tweets_canada_en_8_output_sent.txt", "falcon_sa_tweets_canada_en_9_output_sent.txt",
              "falcon_sa_tweets_canada_en_10_output_sent.txt", "falcon_sa_tweets_canada_en_11_output_sent.txt"]

# List to store data for each file
file_data = []

# Iterate over the file names
for index, file_name in enumerate(file_names, start=1):
    # Construct the full file path with the subdirectory
    file_path = os.path.join(subdirectory, file_name)
    output_path = os.path.join(subdirectory, 'sentiments_' + file_name)

    try:
        # Open the file in read mode
        with open(file_path, 'r') as file, open(output_path, 'a') as out_file:

            positive = 0
            negative = 0
            neutral = 0

            for line in file:
                # Read the contents of the file
                tweet_info = eval(line)  # Assuming each line is a valid Python dictionary representation
                if tweet_info['confidence'] < 0.66:
                    tweet_info['sentiment'] = "Neutral"
                    neutral += 1
                else:
                    if tweet_info['sentiment'] == 'LABEL_0':
                        tweet_info['sentiment'] = 'Positive'
                        positive += 1
                    elif tweet_info['sentiment'] == 'LABEL_1':
                        tweet_info['sentiment'] = 'Negative'
                        negative += 1
                out_file.write(json.dumps(tweet_info) + '\n')

            # Append data for the current file to the list
            file_data.append({'Month': index, 'Positive': positive, 'Negative': negative, 'Neutral':neutral})


    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")

# Write the results to a CSV file
output_csv_path = "falcon_sentiment_counts_per_month_canada.csv"

header = ['Month', 'Positive', 'Negative', 'Neutral']

with open(output_csv_path, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    writer.writerows(file_data)

print(f"CSV file '{output_csv_path}' created successfully.")
