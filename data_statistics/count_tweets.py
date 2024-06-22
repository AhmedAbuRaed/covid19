import os
import plotly.graph_objs as go
import plotly.io as pio
from PIL import Image

# Define the paths to the folders containing the tweet files
folder_path = "../preprocessing"

# Define the regions and file naming patterns
regions = {
    "Canada": "tweets_canada_en_",
    "US": "tweets_us_en_",
    "EU+UK": "tweets_EU_UK_en_"
}

# Initialize a dictionary to store the counts
tweet_counts = {region: [0]*12 for region in regions.keys()}

# Count the number of lines (tweets) in each file
for region, file_prefix in regions.items():
    for month in range(12):
        file_path = os.path.join(folder_path, f"{file_prefix}{month}.txt")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                tweet_counts[region][month] = sum(1 for line in file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

# Print the results
for region, counts in tweet_counts.items():
    print(f"{region}: {counts}")

# Optionally, create the table format output
print("\nTable 2: Monthly Distribution of Tweets by Region for Long COVID Discourse Analysis")
print("Region\t01\t02\t03\t04\t05\t06\t07\t08\t09\t10\t11\t12")
for region, counts in tweet_counts.items():
    print(region + "\t" + "\t".join(map(str, counts)))

# Data for visualization
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
canada = tweet_counts["Canada"]
us = tweet_counts["US"]
eu_uk = tweet_counts["EU+UK"]

# Line Chart using Plotly
line_chart = go.Figure()
line_chart.add_trace(go.Scatter(x=months, y=canada, mode='lines+markers', name='Canada'))
line_chart.add_trace(go.Scatter(x=months, y=us, mode='lines+markers', name='US'))
line_chart.add_trace(go.Scatter(x=months, y=eu_uk, mode='lines+markers', name='EU+UK'))

line_chart.update_layout(
    title='Monthly Distribution of Tweets by Region for Long COVID Discourse Analysis',
    xaxis_title='Month',
    yaxis_title='Number of Tweets',
    legend_title='Region'
)

# Save the figure with orca
output_file = "D:/Research/UBC/Papers/Project2/figure1.png"
try:
    print("Attempting to save chart with orca...")
    pio.write_image(line_chart, output_file, width=6*300, height=4*300, scale=1, engine="orca")
    print(f"Chart saved successfully to {output_file}")

    # Open the image with PIL and set the DPI
    with Image.open(output_file) as img:
        img.save(output_file, dpi=(300, 300))
    print(f"Chart DPI set to 300 and saved successfully to {output_file}")
except Exception as e:
    print(f"Error: {e}")
