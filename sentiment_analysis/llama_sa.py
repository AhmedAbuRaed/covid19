from sys import argv
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import json

output_file_path, tweets_file_path, lama_2_folder_path = argv[1:]

# Define the path for the output and input files
# output_path = '/scratch/st-carenini-1/covid19/llama_sa_tweets_canada_en_0_output_sent.txt'
# tweets_path = '/scratch/st-carenini-1/covid19/tweets_sa_canada_en_0.txt'
output_path = output_file_path
tweets_path = tweets_file_path


# Update to the LLaMA 2 model path or identifier
# lama_2_model_path = "/arc/project/st-carenini-1/LLMs/huggingface/llama-2-13b-chat-hf"
lama_2_model_path = lama_2_folder_path

tokenizer = AutoTokenizer.from_pretrained(lama_2_model_path)
model = AutoModelForSequenceClassification.from_pretrained(lama_2_model_path)

sentiment_analysis_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)


# Function to process and analyze a single tweet using sentiment analysis
def process_tweet_sentiment(tweet, pipeline):
    tweet_text = tweet['text']
    result = pipeline(tweet_text)

    # Directly include the sentiment result in the list
    sentiment_result = {
        "tweet_id": tweet['id'],
        "sentiment": result[0]['label'],
        "confidence": result[0]['score']
    }

    return sentiment_result


# Read tweets and process them
with open(tweets_path, 'r') as rf, open(output_path, 'a') as output:
    for line in rf:
        try:
            data_json = json.loads(line)
            tweet_id = data_json['id']
            created_at = data_json['created_at']
            tweet_text = data_json['text']
            tweet = {'id': tweet_id, 'created_at': created_at, 'text': tweet_text}

            # Process the tweet sentiment
            sentiment = process_tweet_sentiment(tweet, sentiment_analysis_pipeline)

            # Write the original tweet and its sentiment to the output file
            output.write(f"{sentiment}\n")

        except json.JSONDecodeError as e:
            print(f"Error reading line: {e}")


print("Done")