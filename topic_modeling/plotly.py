import pandas as pd
months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

dataframes_list = []
for month in months:
    file = open('D:/Research/UBC/covid19/visualization/canada-' + month + '-2021/' + 'topics.txt', 'r')
    li = eval(file.read())
    df = pd.DataFrame({"Month": [month] * 30,
                       "Topic1": li[0],
                       "Topic2": li[1],
                       "Topic3": li[2],
                       "Topic4": li[3],
                       "Topic5": li[4]})
    print('Month')
    dataframes_list.append(df)

dataframe = pd.concat(dataframes_list)
dataframe.to_csv("D:/Research/UBC/covid19/visualization/canada-2021.csv", index=False)
print("Finished")

