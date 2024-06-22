import pendulum
import calendar
import json
import gzip
import joblib
from pathlib import Path
import csv
import numpy as np
import sys
import pickle
from collections import defaultdict, OrderedDict
import preprocessor as p
from datetime import datetime

from contextualized_topic_models.models.ctm import ZeroShotTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer


def get_week_of_month(year, month, day):
    target_date = pendulum.datetime(year, month, day)
    week_start = target_date.start_of('week')
    week_end = target_date.end_of('week')
    bin_name = '%s-%s' % (week_start.strftime('%m/%d'), week_end.strftime('%m/%d'))
    return bin_name


def binning_weekly(input_prefix, input_num):
    bins = defaultdict(list)

    p.set_options(p.OPT.URL, p.OPT.RESERVED)
    cnt = 0
    for i in range(input_num):
        input_file = '%s_%d.txt' % (input_prefix, i)
        with open(input_file, 'r') as rf:
            for line in rf:
                # date conversion
                data_json = json.loads(line)
                time_expr = data_json['created_at']
                text = data_json['text']
                clean_text = p.clean(text)
                new_time = datetime.strftime(datetime.strptime(time_expr,
                                                               '%Y-%m-%dT%H:%M:%S.%fZ'),
                                             '%Y-%m-%d')
                year, month, day = [int(x) for x in new_time.split('-')]
                # decide on the name of the bin
                bin_name = get_week_of_month(year, month, day)
                # put text into the bin
                bins[bin_name].append(clean_text)
                cnt += 1
    for i, texts in bins.items():
        print('$', i, len(texts))
    return bins


import numpy as np

def find_max_and_index(lst):
    if lst.size == 0:  # Check if the array is empty
        return None, None

    max_item = np.max(lst)  # Find the maximum item
    max_index = np.argmax(lst)  # Find the index of the maximum item

    return max_item, max_index


def contains_any(string, word_list):
    return any(word in string for word in word_list)


def highlight_words(sentence, words_to_highlight):
    highlighted_sentence = []
    for word in sentence.split():
        if word in words_to_highlight:
            highlighted_sentence.append('*' + word + '*')  # Highlight by surrounding with asterisks
        else:
            highlighted_sentence.append(word)
    return ' '.join(highlighted_sentence)


def get_topic_dist(bins, method, model_file, output_file):
    if method != 'CTM':
        # load LDA/NMF model
        model, feature_names, voca = joblib.load(model_file)


    # for each bin, get mean probability
    time_topic = {}

    for i, texts in bins.items():
        doc_topic_dist = None
        if method == 'LDA':
            tf_vectorizer = CountVectorizer(stop_words='english',
                                            vocabulary=voca)
            tf = tf_vectorizer.fit_transform(texts)
            doc_topic_dist = model.transform(tf)
        elif method == 'NMF':
            tfidf_transformer = TfidfTransformer()
            loaded_vec = CountVectorizer(stop_words='english',
                                         vocabulary=voca)
            tfidf = tfidf_transformer.fit_transform(loaded_vec.fit_transform(texts))
            doc_topic_dist = model.transform(tfidf)
        elif method == 'CTM':
            tp = TopicModelDataPreparation("distiluse-base-multilingual-cased")  # instantiate a contextualized model
            tp.vocab.extend(texts)
            ctm = ZeroShotTM(bow_size=len(tp.vocab), contextual_size=512, n_components=5, num_epochs=100)
            ctm.load(
                "contextualized_topic_model_nc_5_tpm_0.0_tpv_0.8_hs_prodLDA_ac_(100, 100)_do_softplus_lr_0.2_mo_0.002_rp_0.99",
                epoch=99)
            testing_dataset = tp.transform(text_for_contextual=texts)
            # n_sample how many times to sample the distribution (see the doc)
            doc_topic_dist = ctm.get_doc_topic_distribution(testing_dataset, n_samples=5)
            if doc_topic_dist is not None:
                for iii, listt in enumerate(doc_topic_dist):
                    max_item, max_index = find_max_and_index(listt)
                    tttt = texts[iii]
                    if max_index == 0:
                        t1_list = ['people', 'children', 'kids', 'covid', 'long', 'get', 'many', 'risk', 'vaccinated', 'deaths']
                        if contains_any(tttt, t1_list):
                            highlighted_text = highlight_words(tttt, t1_list)
                            print("Topic1: " + highlighted_text)
                    if max_index == 1:
                        t2_list = ['day', 'feel', 'like', 'back', 'days', 'year', 'got', 'time', 'pain', 'last']
                        if contains_any(tttt, t2_list):
                            highlighted_text = highlight_words(tttt, t2_list)
                            print("Topic2: " + highlighted_text)
                    if max_index == 2:
                        t3_list = ['symptoms', '19', 'covid', 'long', 'study', 'post', 'patients', 'term', 'infection', 'haulers']
                        if contains_any(tttt, t3_list):
                            highlighted_text = highlight_words(tttt, t3_list)
                            print("Topic3: " + highlighted_text)
                    if max_index == 3:
                        t4_list = ['longcovid', 'mecfs', 'research', 'please', 'cfs', 'support', 'amp', 'pwme', 'help', 'thank']
                        if contains_any(tttt, t4_list):
                            highlighted_text = highlight_words(tttt, t4_list)
                            print("Topic4: " + highlighted_text)
                    if max_index == 4:
                        t5_list = ['fewer', 'ontario', 'vast', 'matters', 'measure', 'amongst', 'likelihood', 'possibility', 'polio', 'contract']
                        if contains_any(tttt, t5_list):
                            highlighted_text = highlight_words(tttt, t5_list)
                            print("Topic5: " + highlighted_text)

        else:
            print('wrong method:', method)

        # compute average
        avg = doc_topic_dist.mean(axis=0)
        time_topic[i] = avg.tolist()

    sorted_dic = {k: time_topic[k] for k in sorted(time_topic)}
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        for k, v in sorted_dic.items():
            new_row = [k] + v
            writer.writerow(new_row)


def run(input_prefix, input_num, method, model_file, output_file):
    tweets_in_bins = binning_weekly(input_prefix, input_num)

    get_topic_dist(tweets_in_bins, method, model_file, output_file)


if __name__ == '__main__':
    input_loc = 'canada'
    input_prefix = 'tweets_%s_en' % input_loc  # _0.txt'
    method = 'CTM'
    model_loc = 'canada_us'
    model_file = '%s_%s_20.model' % (
    model_loc, method)  # model could be different from input e.g., doesn't need to be canada
    input_num = 12  # 5 files
    output_file = 'time_%s_%s_%sTTT.csv' % (input_loc, model_loc, method)
    model_file = 'contextualized_topic_model_nc_5_tpm_0.0_tpv_0.8_hs_prodLDA_ac_(100, 100)_do_softplus_lr_0.2_mo_0.002_rp_0.99'
    run(input_prefix, input_num, method, model_file, output_file)
