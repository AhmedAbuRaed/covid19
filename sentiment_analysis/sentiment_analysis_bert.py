from transformers import pipeline
import json

output_path = '/scratch/st-carenini-1/covid19/canada_output_sent.txt'
tweets_path = '/scratch/st-carenini-1/covid19/tweets_canada_en_0.txt'

# Initialize the sentiment analysis pipeline with BERT model
model_name = "/arc/home/aaburaed/.cache/huggingface/hub/models--bert-base-uncased/snapshots/a265f773a47193eed794233aa2a0f0bb6d3eaa63/"  # Replace with "roberta-base" if you prefer RoBERTa
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)

# Function to process and analyze a single tweet
def process_tweet(tweet, pipeline):
    tweet_text = tweet['text']
    try:
        sentiment = pipeline(tweet_text)
        return sentiment
    except Exception as e:
        print(f"Error processing tweet ID {tweet['id']}: {e}")
        return None

# Read tweets and process them
with open(tweets_path, 'r') as rf, open(output_path, 'a') as output:
    for line in rf:
        try:
            data_json = json.loads(line)
            tweet_id = data_json['id']
            created_at = data_json['created_at']
            tweet_text = data_json['text']
            tweet = {'id': tweet_id, 'created_at': created_at, 'text': tweet_text}

            # Process the tweet
            result = process_tweet(tweet, sentiment_pipeline)
            if result:
                # Formatting the output as desired
                sentiment_result = f"{result[0]['label']}, {result[0]['score']:.2f}"
                output_line = f"{tweet_id},{created_at},{sentiment_result}\n"
                output.write(output_line)
                print(output_line)
        except json.JSONDecodeError as e:
            print(f"Error reading line: {e}")
