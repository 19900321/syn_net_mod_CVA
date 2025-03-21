#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 6.6.2019 16.27
# @Author  : YINYIN
# @Site    : 
# @File    : herb_herb_pairs.py
# @Software: PyCharm

import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
import operator


def reoder_tuple(x):
    if len(x) ==2:
        if x[0] <= x[1]:
            return x
        else:
            return tuple([x[1], x[0]])
    else:
        return x


import itertools
from collections import Counter
# import matplotlib.pyplot as plt
# import seaborn as sns
from collections import defaultdict

class FangJi():

    def __init__(self, filename, herb_yin_id_dic):
        self.herb_pinyin_id_dict = herb_yin_id_dic
        self.data = self.read_data(filename)
        self.fangji_herb_dict = self.fangji_herb_dic()
        self.fangji_herbid_dict  = self.fangji_herbid_dic()
        self.fangji_herb_pair_id_dict = self.fangji_herb_pair_id_dic(2)
        self.fangji_herb_pair_pinyin_dict = self.fangji_herb_pair_pinyin_dic(2)
        self.herb_frequency_dict = self.herb_frequency(1)
        self.herbid_frequency_dict = self.herbid_frequency_dic(2)
        self.herbpinyin_frequency_dict = self.herbpinyin_frequency_dic(2)

        #self.herb_triple_frequency_dict = self.herb_frequency(3)

    def read_data(self, filename):
        data = pd.read_csv(filename, sep=':', encoding='utf-8')
        data['data_number'] = data.index
        data['pinyin_name'] = data['pinyin_name'] + data['data_number'].astype(str)
        return data


    def fanfji_serach(self, fungji_name):
        return self.data[self.data['herb-id'] == fungji_name]

    def fangji_herb_dic(self):
        self.data['herb_list'] = [i.strip(',').split(',') for i in self.data['pinyin_composition']]
        fangji_herb_dict = dict(zip(self.data['pinyin_name'], self.data['herb_list']))
        return fangji_herb_dict

    def herb_frequency(self, number):
        herb_frequency_dict = Counter(
            ((reoder_tuple(pair) for ls in self.fangji_herb_dict.values() if len(ls) >= number
             for pair in itertools.combinations(ls, number))))
        return herb_frequency_dict

    def fangji_herbid_dic(self):
        fangji_herbid_dict = {k: [self.herb_pinyin_id_dict[herb] for herb in herbs if herb in self.herb_pinyin_id_dict.keys()]
         for k, herbs in self.fangji_herb_dict.items()}
        return fangji_herbid_dict


    def fangji_herb_pair_id_dic(self, number):
        fangji_herb_pair_id_dict = {}
        for k, ls in self.fangji_herbid_dict.items():
            if len(ls) >= number:
                pairs_list = []
                for pair in itertools.combinations(ls, number):
                    pairs_list.append(reoder_tuple(pair))
                fangji_herb_pair_id_dict.update({k:pairs_list})
        return fangji_herb_pair_id_dict
    def fangji_herb_pair_pinyin_dic(self, number):
        fangji_herb_pair_pinyin_dict = {}
        for k, ls in self.fangji_herb_dict.items():
            if len(ls) >= number:
                pairs_list = []
                for pair in itertools.combinations(ls, number):
                    pairs_list.append(reoder_tuple(pair))
                fangji_herb_pair_pinyin_dict.update({k:pairs_list})
        return fangji_herb_pair_pinyin_dict

    def herbid_frequency_dic(self, number):

        herbid_frequency_dict = Counter(
            (reoder_tuple(pair) for ls in self.fangji_herbid_dict.values() if len(ls) >= number
             for pair in itertools.combinations(ls, number)))
        return herbid_frequency_dict
    def herbpinyin_frequency_dic(self, number):

        herbpinyin_frequency_dict = Counter(
            (reoder_tuple(pair) for ls in self.fangji_herb_dict.values() if len(ls) >= number
             for pair in itertools.combinations(ls, number)))
        return herbpinyin_frequency_dict

    def choose_common_herbpairs(self, start, number, herb_ingre_dict, pinyin_herbid_dic ):
        herb_pairs_list = []
        n = 0
        cal_able_list = herb_ingre_dict.keys()

        for herb_pairs in self.herbid_frequency_dict.most_common()[start:]:
            if n < number:
                herb1 = herb_pairs[0][0]
                herb2 = herb_pairs[0][1]
                frequency = herb_pairs[1]
                if all([herb in cal_able_list for herb in [herb1, herb2]]):
                    herb1_name = pinyin_herbid_dic[herb1]
                    herb2_name = pinyin_herbid_dic[herb2]
                    n += 1
                    herb_pairs_list += [(herb1, herb1_name, herb2, herb2_name, frequency)]
        return herb_pairs_list

    def generate_random_pairs(self, number, herb_list, pinyin_herbid_dic):
        top_pairs = list(map(lambda x: set(x), list(dict(self.herbid_frequency_dict).keys())))
        n = 0
        herb_pairs_list = []
        herb_pairs_visited = []
        while n < number:
            pair = random.sample(set(herb_list), 2)
            if set(pair) not in top_pairs and set(pair) not in herb_pairs_visited:
                herb1 = pair[1]
                herb2 = pair[0]
                herb1_name = pinyin_herbid_dic[herb1]
                herb2_name = pinyin_herbid_dic[herb2]
                frequency = 0
                herb_pairs_visited += [set([herb1, herb2])]
                herb_pairs_list += [(herb1, herb1_name, herb2, herb2_name, frequency)]
                n += 1
        return herb_pairs_list

    def plot_one_herb_frequency(self, top_number):
        if top_number != 0:
            values = dict(self.herbid_frequency_dict.most_common(top_number)).values()
            bins = 30
        else:
            values = list(dict(self.herb_frequency_dict).values())
            bins = [i * 50 for i in range(0, 30)] + [max(values)]

        f, ax = plt.subplots(figsize=(11, 9))
        sns.distplot(values, bins)
        plt.ylabel('Frequency')
        plt.title('herb appearance frequency')
        plt.show()

    def plot_pair_herb_freqency(self,  top_number):
        if top_number != 0:
            values = list(dict(self.herb_pair_frequency_dict.most_common(top_number)).values())
            bins = 30
        else:
            values = list(dict(self.herb_pair_frequency_dict).values())
            bins = [i * 100 for i in range(0, 14)]

        f, ax = plt.subplots(figsize=(11, 9))
        plt.hist(values, bins = bins, hist = True)
        plt.ylabel('Frequency')
        plt.title('Herb pairs appearance frequency')
        plt.show()

    def plot_one_herb_frequency_log(self):
        import numpy as np
        f, ax = plt.subplots(figsize=(11, 9))
        plt.hist(self.herb_frequency_dict.values(),
                 log=True,
                 bins=2 ** np.arange(15),
                 color='#0504aa',
                 lw=2, alpha=0.7,
                 rwidth=0.85)
        plt.xscale('log')
        plt.ylabel('log count')
        plt.title('log-log histogram of the ingredient appearance count')
        plt.show()

    def plot_triple_herb_frequency(self, top_number):
        if top_number != 0:
            values = dict(self.herb_triple_frequency_dict.most_common(top_number)).values()
            bins = 30
        else:
            values = dict(self.herb_triple_frequency_dict).values()
            bins = [0, 1, 2, 10, 50, 100, 200, 300, 400]

        f, ax = plt.subplots(figsize=(11, 9))
        plt.hist(values, bins, alpha=0.5)
        plt.ylabel('frequency')
        plt.title('herb triple appearance frequency')
        plt.show()


def main():
    result = FangJi('source_data/prescription.txt')
    return result

