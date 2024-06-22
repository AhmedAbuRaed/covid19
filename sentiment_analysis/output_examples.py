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
    file_path = os.path.join(subdirectory, 'sentiments_' + file_name)
    output_path = os.path.join(subdirectory, 'examples_sentiments_' + file_name)
    tweets_path = 'D:/Research/UBC/covid19/preprocessing/' + file_name.split("falcon_sa_")[1].split("_output_sent")[0] + '.txt'

    tweets_dict = {}

    with open(tweets_path, 'r') as file:
        # Iterate through each line (tweet) in the file
        for line in file:
            # Parse the JSON data for each tweet
            tweet_data = json.loads(line)
            # Extract the tweet ID as the key for the dictionary
            tweet_id = tweet_data['id']
            # Store the tweet data in the dictionary using the tweet ID as the key
            tweets_dict[tweet_id] = tweet_data

    try:
        # Open the file in read mode
        with open(file_path, 'r') as file, open(output_path, 'a') as out_file:
            for line in file:
                # Read the contents of the file
                tweet_info = eval(line)  # Assuming each line is a valid Python dictionary representation
                tweet = tweets_dict[tweet_info['tweet_id']]

                out_file.write(json.dumps({'tweet_id': tweet_info['tweet_id'], 'sentiment': tweet_info['sentiment'], 'text': tweet['text']}) + '\n')


    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")


