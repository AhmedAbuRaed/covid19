import torch
from transformers import pipeline
from bert_score import score

months = [
    "jan",
    "feb",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]



for month in months:
    file = open(
        "D:/Research/UBC/covid19/visualization/canada-"
        + month
        + "-2021/"
        + "topics.txt",
        "r",
    )
    if month == "jan":
        jan_list = eval(file.read())
    elif month == "feb":
        feb_list = eval(file.read())
    elif month == "march":
        march_list = eval(file.read())
    elif month == "april":
        april_list = eval(file.read())
    elif month == "may":
        may_list = eval(file.read())
    elif month == "june":
        june_list = eval(file.read())
    elif month == "july":
        july_list = eval(file.read())
    elif month == "august":
        august_list = eval(file.read())
    elif month == "september":
        september_list = eval(file.read())
    elif month == "october":
        october_list = eval(file.read())
    elif month == "november":
        november_list = eval(file.read())
    elif month == "december":
        december_list = eval(file.read())
    else:
        print("ERROR")


year_list = [jan_list, feb_list, march_list, april_list, may_list, june_list, july_list, august_list, september_list,
             october_list, november_list, december_list]

normalized_importance_scores = [0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03,
                                0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
                                0.01, 0.01, 0.01, 0.01]


output = open('D:/Research/UBC/covid19/visualization/topics_similaritiesBertS.txt', 'a')

for i in range(11):
    # Two lists of sentences
    month1 = year_list[i]
    month2 = year_list[i + 1]

    for month1_topic_index in range(5):
        weights = {}
        sentences1 = month1[month1_topic_index]
        for i, w in enumerate(sentences1):
            weights[w] = normalized_importance_scores[i]
        for month2_topic_index in range(5):
            sentences2 = month2[month2_topic_index]

            for i, w in enumerate(sentences2):
                weights[w] = normalized_importance_scores[i]

            P, R, F1 = score(sentences1, sentences2, lang='en')

            weighted_scores1 = [weights[word] * score for word, score in zip(sentences1, F1)]
            weighted_scores2 = [weights[word] * score for word, score in zip(sentences2, F1)]
            average_tensor1 = torch.mean(torch.stack(weighted_scores1), dim=0).item()
            average_tensor2 = torch.mean(torch.stack(weighted_scores2), dim=0).item()
            output.write(str(i + 1) + ',' + str(month1_topic_index + 1) + ',' + str(month2_topic_index + 1) + ',' + str((average_tensor1 + average_tensor2) / 2) + '\n')

print("done")
