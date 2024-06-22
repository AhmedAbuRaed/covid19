import json
import gzip
from pathlib import Path
import csv
import sys
import pickle
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def get_country(users_file_path, user_id):
    keys = ['aaburaed', 'ahmed.aburaed', 'ahmedaburaed', 'aburaedahmed']

    with open(users_file_path) as rf:
        for line in rf:
            data_json = json.loads(line)
            if data_json['id'] == user_id:
                if 'location' in data_json:
                    location = data_json['location']
                    geolocator = Nominatim(user_agent="covid19")
                    try:
                        g = geolocator.geocode(location, addressdetails=True)
                        if g is not None and g.raw is not None and 'address' in g.raw and 'country' in g.raw['address']:
                            # time.sleep(1)
                            return g.raw['address']['country']
                        else:
                            return -1
                    except GeocoderTimedOut as e:
                        print(location)
                    except GeocoderUnavailable as e:
                        print(location)
                    except BaseException as error:
                        print('An exception occurred: {}'.format(error))
                else:
                    return -1
    return -1


def get_user_id(tweet):
    data_json = json.loads(tweet)
    if 'author_id' in data_json:
        return data_json['author_id']
    else:
        return -1


def parse(input_file):
    data = []
    with open(input_file) as rf:
        for line in rf:
            data_json = json.loads(line)
            data.append(data_json)
    return data


def get_hashtag_freq(data):
    hashtags_cnts = {}
    for datum in data:
        hashtags = datum['entities']['hashtags']
        for tag_st in hashtags:
            tag = tag_st['text'].lower()
            if tag in hashtags_cnts:
                hashtags_cnts[tag] += 1
            else:
                hashtags_cnts[tag] = 1

        #[{'text': 'Coronavirus', 'indices': [21, 33]}]
    sorted_cnts = {k: v for k, v in sorted(hashtags_cnts.items(), 
            key=lambda item: item[1], reverse=True)}
    print(sorted_cnts)
    with open('hashtags_cnts.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['hashtag', 'cnt'])
        for k, v in sorted_cnts.items():
            writer.writerow([k,v])

def get_loc_freq(data):
    loc_cnts = {}
    for datum in data:
        loc = datum['bio_location'] #['country']
        if loc == None: 
            continue
        print(loc)
        #loc = '%s, %s' % (loc['full_name'], loc['country']) 
        #loc = loc['country']
        if loc in loc_cnts:
            loc_cnts[loc] += 1
        else:
            loc_cnts[loc] = 1

    sorted_cnts = {k: v for k, v in sorted(loc_cnts.items(), 
            key=lambda item: item[1], reverse=True)}
    print(sorted_cnts)
    with open('place_cnts.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['place', 'cnt'])
        for k, v in sorted_cnts.items():
            writer.writerow([k,v])

def get_lang_freq(data):
    lang_cnts = {}
    for datum in data:
        lang = datum['lang'] #['country']
        if lang == None: 
            continue
        if lang in lang_cnts:
            lang_cnts[lang] += 1
        else:
            lang_cnts[lang] = 1

    sorted_cnts = {k: v for k, v in sorted(lang_cnts.items(), 
            key=lambda item: item[1], reverse=True)}
    print(sorted_cnts)
    with open('lang_cnts.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['lang', 'cnt'])
        for k, v in sorted_cnts.items():
            writer.writerow([k,v])

def get_stopwords(filename):
    with open(filename, 'r') as f:
        stopwords = []
        for line in f:
            w = line.strip()
            stopwords.append(w)
        return stopwords

def get_word_freq(data):
    stopwords = get_stopwords('stopwords.txt')
    texts = get_texts(input_file)
    word_cnts = {}
    for text in texts:
        #text = datum['text']
        tokens = text.split(' ')
        for tok in tokens:
            tok = tok.strip()
            if tok in stopwords:
                continue
            if tok in word_cnts:
                word_cnts[tok] += 1
            else:
                word_cnts[tok] = 1
    sorted_cnts = {k: v for k, v in sorted(word_cnts.items(), 
            key=lambda item: item[1], reverse=True)}
    print(sorted_cnts)
    with open('token_cnts_nostopwords.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['token', 'cnt'])
        for k, v in sorted_cnts.items():
            writer.writerow([k,v])

def select_canada(path, country_dic, city_dic, wf, cnt_total):
    print(path.name)
    with open(path, 'r', encoding='utf-8') as rf:
        for line in rf:
            cnt_total += 1
            data_json = json.loads(line)
            user_id = get_user_id(line)
            users_path = str(path)[:-4] + '.user.txt'
            country = get_country(users_path, user_id)
            if country is None or country == -1:
                continue

            if country in country_dic:
                country_dic[country] += 1
            else:
                country_dic[country] = 1
            if country == 'United States':
                # print(data_json['place'])
                wf.write(line)
    return cnt_total

def get_US(data_dirs, output_file):
    cnt_total = 0
    country_dic = {}
    city_dic = {} # canada city
    with open(output_file, 'w') as wf:
        for data_dir in data_dirs:
            for path in Path(data_dir).iterdir():
                if not str(path).endswith('.user.txt'):
                    cnt_total = select_canada(path,
                        country_dic, city_dic, wf, cnt_total)
    print(country_dic)
    print(city_dic)
    print(cnt_total)

if __name__ == '__main__':
    data_dirs = ['2021/1', '2021/2', '2021/3', '2021/4', '2021/5', '2021/6', '2021/7', '2021/8', '2021/9', '2021/10',
                 '2021/11', '2021/12']
    month_index = int(sys.argv[1])
    month = [data_dirs[month_index]]
    output_file = 'tweets_us_%d.txt' % month_index
    get_US(month, output_file)
