import fasttext
from scipy.spatial.distance import cosine

model_path = 'D:/Research/UBC/covid19/BioWordVec_PubMed_MIMICIII_d200.bin'
model = fasttext.load_model(model_path)

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
        "D:/Research/UBC/covid19/visualization/EU_UK-"
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

year_list = [jan_list, feb_list, march_list, april_list, may_list, june_list,
             july_list, august_list, september_list, october_list,
             november_list, december_list]

output = open('D:/Research/UBC/covid19/visualization/EU_UK_topics_similaritiesWord2VecCosine.txt', 'a')

for i in range(11):
    # Two lists of sentences
    month1 = year_list[i]
    month2 = year_list[i + 1]

    for month1_topic_index in range(5):
        weights = {}
        sentences1 = month1[month1_topic_index]

        for month2_topic_index in range(5):
            sentences2 = month2[month2_topic_index]

            total_similarity = 0
            for word1 in sentences1[0:10]:
                for word2 in sentences2[0:10]:
                    total_similarity = total_similarity + (1 - cosine(model.get_word_vector(word1), model.get_word_vector(word2)))

            average_similarity = total_similarity / (len(sentences1[0:10]) * len(sentences2[0:10]))

            output.write(str(i + 1) + ',' + str(month1_topic_index + 1) + ',' + str(month2_topic_index + 1) + ',' +
                         str(average_similarity) + '\n')

print("done")
