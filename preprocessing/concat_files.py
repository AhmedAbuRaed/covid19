filenames = ['tweets_EU_UK_en_0.txt', 'tweets_EU_UK_en_1.txt', 'tweets_EU_UK_en_2.txt', 'tweets_EU_UK_en_3.txt',
             'tweets_EU_UK_en_4.txt', 'tweets_EU_UK_en_5.txt', 'tweets_EU_UK_en_6.txt', 'tweets_EU_UK_en_7.txt',
             'tweets_EU_UK_en_8.txt', 'tweets_EU_UK_en_9.txt', 'tweets_EU_UK_en_10.txt', 'tweets_EU_UK_en_11.txt']
with open('tweets_EU_UK_en.txt', 'w', encoding="utf-8") as outfile:
    for fname in filenames:
        with open(fname, encoding='utf-8') as infile:
            for line in infile:
                outfile.write(line)
            infile.close()
    outfile.close()
