import csv
import json
import sys
from pathlib import Path

import torch
from contextualized_topic_models.models.ctm import ZeroShotTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from preprocessor import clean  # Use your existing clean function
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Extract command-line arguments for various paths
region, month, part, input_folder_path, topic_modeling_folder_path, sentiment_model_path, output_folder_path, generic_model = sys.argv[
                                                                                                                              1:]

# Convert the string 'true' or 'false' to a boolean
topic_model_specific = generic_model.lower() == 'true'

# Decide the model path based on the value of topic_model_specific
if topic_model_specific:
    model_path = topic_modeling_folder_path
else:
    model_path = f"{topic_modeling_folder_path}{region}-{month}-2021/contextualized_topic_model_nc_5_tpm_0.0_tpv_0.8_hs_prodLDA_ac_(100, 100)_do_softplus_lr_0.2_mo_0.002_rp_0.99/"

# Mapping of month names to their indices (0 for January, 1 for February, etc.)
month_to_index = {
    'jan': 0, 'feb': 1, 'march': 2, 'april': 3,
    'may': 4, 'june': 5, 'july': 6, 'august': 7,
    'september': 8, 'october': 9, 'november': 10, 'december': 11
}

# Convert the month name to its index
month_index = month_to_index[month.lower()]

# Initialize the TopicModelDataPreparation with a base model
tp = TopicModelDataPreparation("distiluse-base-multilingual-cased")

input_path = Path(input_folder_path)
all_cleaned_texts = []  # Collect all cleaned texts for both BoW and contextual

# Collect and preprocess texts using your clean function
for file_path in input_path.glob(f"tweets_{region}_en_{month_index}_{part}.txt"):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            tweet = json.loads(line)
            all_cleaned_texts.append(clean(tweet['text']))  # Use your clean function

# Ensure there's meaningful content in at least some texts
if not all_cleaned_texts:
    raise ValueError("No meaningful content found in tweets after cleaning.")

# Fit the TopicModelDataPreparation object with the cleaned texts
tp.fit(text_for_contextual=all_cleaned_texts, text_for_bow=all_cleaned_texts)

# Load the ZeroShotTM model for topic modeling from the specified folder path
ctm = ZeroShotTM(bow_size=len(tp.vocab), contextual_size=512, n_components=5, num_epochs=100)
ctm.load(model_path, epoch=99)

# Initialize the sentiment analysis pipeline using the specified folder path for model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(sentiment_model_path)
model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_path)
sentiment_analysis_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)


def process_batch(tweets):
    cleaned_texts = [clean(tweet['text']) for tweet in tweets]  # Use your clean function
    sentiments = sentiment_analysis_pipeline(cleaned_texts)
    testing_dataset = tp.transform(text_for_contextual=cleaned_texts)
    doc_topic_dists = ctm.get_doc_topic_distribution(testing_dataset, n_samples=5)

    results = []
    for tweet, sentiment, doc_topic_dist in zip(tweets, sentiments, doc_topic_dists):
        topic_dist = doc_topic_dist.tolist()
        highest_topic_index, highest_topic_score = max(enumerate(topic_dist), key=lambda pair: pair[1])

        results.append({
            "tweet_id": tweet['id'],
            "sentiment": sentiment['label'],
            "sentiment_confidence": sentiment['score'],
            "topic_distribution": topic_dist,
            "highest_topic_index": highest_topic_index,
            "highest_topic_score": highest_topic_score
        })

    return results


generic_monthly = 'monthly'
if topic_model_specific:
    generic_monthly = 'generic'

# Process tweets from input files and write the results to an output CSV file
output_file = Path(output_folder_path) / f"pipeline_{generic_monthly}_{region}_{month}_output.csv"
batch_size = 100  # Define your desired batch size

output_file_exists = output_file.exists()

with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    if not output_file_exists:
        writer.writerow(["tweet_id", "sentiment", "sentiment_confidence", "topic_distribution", "highest_topic_index",
                         "highest_topic_score"])

    for file_path in input_path.glob(f"tweets_{region}_en_{month_index}_{part}.txt"):
        batch = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                tweet = json.loads(line)
                batch.append(tweet)
                if len(batch) == batch_size:
                    results = process_batch(batch)
                    for result in results:
                        writer.writerow([
                            result['tweet_id'], result['sentiment'], result['sentiment_confidence'],
                            result['topic_distribution'], result['highest_topic_index'], result['highest_topic_score']
                        ])
                    batch = []

            # Process the last batch if it's not empty
            if batch:
                results = process_batch(batch)
                for result in results:
                    writer.writerow([
                        result['tweet_id'], result['sentiment'], result['sentiment_confidence'],
                        result['topic_distribution'], result['highest_topic_index'], result['highest_topic_score']
                    ])
