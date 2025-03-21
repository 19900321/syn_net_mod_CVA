#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 6.6.2019 14.58
# @Author  : YINYIN
# @Site    : 
# @File    : herb_ingre_tar.py
# @Software: PyCharm


import pandas as pd
from proximity_key import *
import numpy as np
from collections import defaultdict
from functools import reduce
# import MySQLdb
# import MySQLdb.cursors
from collections import defaultdict


def qc_herb(data):
    herb_ingre_dict = data.groupby('herb_id')['ingredients_id'].apply(list).to_dict()
    herb_ingre_dict = {key: [m for m in value if isinstance(m, str)] for key, value in herb_ingre_dict.items() if
                       len(value) != 0}
    herb_ingre_dict_2 = {key: [m for m in value if m[1:].isdigit() == True] for
                         key, value in herb_ingre_dict.items()}
    herb_ingre_dict3 = {key: value for key, value in herb_ingre_dict_2.items() if len(value) != 0}
    return herb_ingre_dict3



# map the ingreidnets out
def annotaion_ingredients_from_mqsql():
    # connect mysql
    db_2 = MySQLdb.connect(host="127.0.0.1", user="yin", passwd="Mqxs320321wyy", db="tcm_infor",
                           cursorclass=MySQLdb.cursors.DictCursor,
                           charset="utf8")
    c = db_2.cursor()

    # decide the search code in mysql. It depend on the search key word we use. one of ['smiles', 'inchikey']

    sql = """
           select * from ingreidnet_annotation
           """
    # perform query in mysql, and return the dataframe result
    c.execute(sql)
    inchey_used_2 = c.fetchall()
    pd_result = pd.DataFrame(list(inchey_used_2))
    print(pd_result.shape)
    return pd_result


def annotaion_herbs_from_mqsql():
    # connect mysql
    db_2 = MySQLdb.connect(host="127.0.0.1", user="yin", passwd="Mqxs320321wyy", db="tcm_infor",
                           cursorclass=MySQLdb.cursors.DictCursor,
                           charset="utf8")
    c = db_2.cursor()

    # decide the search code in mysql. It depend on the search key word we use. one of ['smiles', 'inchikey']

    sql = """
           select * from herb_information
           """
    # perform query in mysql, and return the dataframe result
    c.execute(sql)
    inchey_used_2 = c.fetchall()
    pd_result_herb = pd.DataFrame(list(inchey_used_2))
    return pd_result_herb



class Ingredients:
    def __init__(self, filename, score, species):
        self.filename = filename
        self.species = species
        self.data = self.read_file()
        self.score = score

        self.target_name = 'entrez_id_{}'.format(self.species)
        self.score_name = 'combined_score_{}'.format(self.species)
        self.ingredients = self.data.index.tolist()
        self.ingretar_dict_all = self.ingredients_target_dict_all()
        self.entry_ensymbl_dict = self.target_enrty_ensymbl()
        self.ingre_id_name_dict_value = self.ingre_id_name_dict()

    def read_file(self):
        #data = pd.read_csv(self.filename, sep = '\t')
        data = pd.read_excel(self.filename, sheet_name='Sheet1')
        colu_import_c =[i+self.species for i in ['length_',  'SYMBOL_id_','entrez_id_','UNIPROT_id_', 'combined_score_']]

        data = data[ ['ingredients_id', 'inchikey', 'name', 'smiles_mesh', 'inchi_mesh', 'iupac_name_mesh','chemical' ] + colu_import_c]

        data = data.dropna(axis=0, how='any')
        data['ingredients_id_2'] = 'I' + data['ingredients_id'].astype(str)
        data = data.set_index('ingredients_id_2')
        return data

    def ingredients_info(self, ingredient):
        ingredient_dict = defaultdict()
        if 'stitch_name' in  self.data.columns:
            ingredient_dict['stitch_name'] = self.data.loc[ingredient, 'stitch_name']
        ingredient_dict['name'] = self.data.loc[ingredient, 'name']
        #print(ingredient)
        ingredient_dict['target_ensymble'] = self.data.loc[ingredient, 'SYMBOL_id_{}'.format(self.species)].split(',')
        ingredient_dict['target'] = self.data.loc[ingredient, self.target_name].split(',')
        ingredient_dict['score'] = self.data.loc[ingredient, self.score_name].split(',')
        return ingredient_dict


    def ingre_id_name_dict(self):
        self.data['ingre_2'] = 'I' + self.data['ingredients_id'].astype(str)
        ingre_id_name_dict_value = dict(zip(self.data['ingre_2'], self.data['name']))
        return ingre_id_name_dict_value


    def ingredients_target_dict_all(self):
        ingretar_dict_all = defaultdict()
        for ingredient in self.ingredients:
            ingretar_dict_all[ingredient] = self.ingredients_info(ingredient)['target']
        return ingretar_dict_all


    def ingredients_target(self, ingredient, G_nodes):
        ingredient_dict = self.ingredients_info(ingredient)

        if len(ingredient_dict['target']) == len(ingredient_dict['score']):
            target_left = ['T' + str(ingredient_dict['target'][m]) for m,n in enumerate(ingredient_dict['score'])
                        if float(n) > self.score]
            target_left = [t for t in target_left if t in G_nodes]
            ingredient_dict['left_target'] = target_left
        else:
            ingredient_dict['left_target'] = ['T' + str(t) for t in ingredient_dict['target'] if 'T' + str(t) in G_nodes]
        return ingredient_dict


    def target_enrty_ensymbl(self):
        entry_ensymbl_dict = {}
        for ingredient in self.ingredients:
            ingredient_dict = self.ingredients_info(ingredient)
            ensymble = ingredient_dict['target_ensymble']
            targets_changed = ['T' + t for t in ingredient_dict['target']]
            if len(ensymble) == len(targets_changed):
                entry_ensymbl_dict_one = dict(zip(targets_changed, ensymble))
                entry_ensymbl_dict.update(entry_ensymbl_dict_one)
        return entry_ensymbl_dict

    def ingredients_target_dict(self, G_nodes):
        self.ingre_tar_dict = defaultdict()
        for ingredient in self.ingredients:
            targets = self.ingredients_target(ingredient, G_nodes)['left_target']
            if len(targets) != 0:
                self.ingre_tar_dict[ingredient] = targets
        return self.ingre_tar_dict


    def ingre_ingre_dis(self, ingre_from, ingre_to, network, distance_method):
        if any(ingre not in self.ingre_tar_dict.keys() for ingre in [ingre_from, ingre_to]):
            print('{} or {} not in dictionary'.format(ingre_from, ingre_to))
            return None
        else:
            nodes_from = self.ingre_tar_dict[ingre_from]
            nodes_to = self.ingre_tar_dict[ingre_to]
            length_dict = Sets_Lengths(nodes_from, nodes_to).target_lengths(network)
            dis_obj = Network_Distance(nodes_from, nodes_to, length_dict)
            distance = dis_obj.network_distance(distance_method)
            return distance

    def ingre_ingre_dis_all(self, ingre_from, ingre_to, network):

        distance_method_list = ['separation', 'closest', 'shortest', 'kernel', 'center']

        return {method: self.ingre_ingre_dis(ingre_from, ingre_to, network, method)
                for method in distance_method_list}


class Herb_Info( ):

    def __init__(self, filename):
        #self.data = pd.read_csv(filename, sep='\t', encoding ='utf-8')
        self.data = pd.read_csv(filename,  encoding='utf-8')
        self.data['herb-id'] =  self.data['herb-id'].astype(str)
        self.herb_pinyin_dic = self.herb_pinyin_id_dic()
        self.pinyin_herbid_dic = self.pinyin_herb_id_dic()
        self.herb_names = self.herb_names()

    # herb-id, Pinyin Name, Chinese Name, English Name, Latin Name
    def herb_search(self, key_words):
        return self.data[self.data.where(self.data == key_words).any(axis=1)]

    def herb_names(self):
        return self.data.columns

    def herb_names_transfer(self, key_words, name_type):
        return self.data.loc[self.data.where(self.data == key_words).any(axis=1), name_type]

    def herb_pinyin_id_dic(self):
        herb_pinyin_dic = dict(zip(self.data['Pinyin Name'], self.data['herb-id']))
        return herb_pinyin_dic

    def pinyin_herb_id_dic(self):
        herb_pinyin_dic = dict(zip(self.data['herb-id'], self.data['Pinyin Name'],))
        return herb_pinyin_dic


class Herb:
    def __init__(self, filename):
        self.filename = filename

        self.data_all = self.read_data2()
        self.data = self.precess_data()
        self.herb_ingre_dict_all = qc_herb(self.data)
        self.herbs = list(self.herb_ingre_dict_all.keys())
        self.ingredients = list(self.herb_ingre_dict_all.values())

    def precess_data(self):
        data_left = self.data_all.dropna(subset= ['ingredients_id'], axis=0)
        return data_left


    def herb_ingre_dict_all(self):
        return qc_herb(self.data)

    def herb_ingre_dic(self, ingredients_target_dict):
        self.herb_ingre_dict = {k: [v_2 for v_2 in v if v_2 in ingredients_target_dict.keys() ]
                                for k, v in self.herb_ingre_dict_all.items()
                                }

        self.herb_ingre_dict = {k: v
                                for k, v in self.herb_ingre_dict.items() if len(v) != 0
                                }
        return self.herb_ingre_dict

    def herb_ingretargets(self, herb, ingredients_target_dict):
         ingre_target_list = [ingredients_target_dict[ingre]
                              for ingre in self.herb_ingre_dict_all[herb] if ingre in ingredients_target_dict.keys()]
         if len(ingre_target_list) == 0:
             return None
         else:
            return list(set((reduce(lambda x, y: x+y, ingre_target_list))))

    def herb_ingretargets_dic(self, ingredients_target_dict):
        self.herb_ingretargets_dic = defaultdict()
        for herb in list(self.herbs):
            targets = self.herb_ingretargets(herb, ingredients_target_dict)
            if targets != None:
                self.herb_ingretargets_dic[herb] = self.herb_ingretargets(herb, ingredients_target_dict)
        return self.herb_ingretargets_dic

    def read_data2(self):
        data = pd.read_csv(self.filename, sep=',')
        data['ingredients_id'] = 'I' + data['ingredients_id'].astype(str)
        data['herb_id'] = data['herb_id'].astype(str)
        return data

    def add_herb_info(self, file_herb_info_path):
        herb_info_obj = Herb_Info(file_herb_info_path)
        self.data_info = herb_info_obj.data
        self.herb_pinyin_dic = herb_info_obj.herb_pinyin_dic
        self.pinyin_herbid_dic = herb_info_obj.pinyin_herbid_dic
        self.herb_names = herb_info_obj.herb_names


class Ingredients_simple:
    def __init__(self, filename, G):
        self.filename = filename
        self.G = G
        self.ingre_target_pd = pd.read_csv(self.filename)
        self.ingre_target_dict_all = self.prepare_ingre_target_all()

    def prepare_ingre_target_all(self):
        ingre_target_dict_all = dict(self.ingre_target_pd.groupby('inchikey_x')['ENSEMBL'].apply(list))
        return ingre_target_dict_all

    def prepare_ingre_target_used(self):
        nodes_ppi = self.G.nodes
        ingre_target_dict_used = {ingre: [t for t in target if t in nodes_ppi] for ingre, target in self.ingre_target_dict_all.items()}
        self.ingre_target_dict_used = {ingre: target for ingre, target in
                                  ingre_target_dict_used.items() if len(target) != 0 }


    def cal_ingre_closest_distance(self, ingre_1, ingre_2):
        nodes_from = self.ingre_target_dict_used[ingre_1]
        nodes_to = self.ingre_target_dict_used[ingre_2]

        # distance in simple way
        closest_dis = closest_distance(self.G, nodes_from, nodes_to)
        return closest_dis


class Herb_simple():
    def __init__(self, filename):
        self.filename = filename
        self.herb_ingre_pd = pd.read_csv(self.filename)
        self.herb_ingre_dict = self.prepare_herb_ingre_dict()

    def prepare_herb_ingre_dict(self):
        herb_ingre_dict = dict(self.herb_ingre_pd.groupby('中文名')['inchikey'].apply(list))
        return herb_ingre_dict

    def cal_herb_closest_distance(self, ingre_simple_obj, herb1, herb2):
        ingres_from = self.herb_ingre_dict[herb1]
        ingres_to = self.herb_ingre_dict[herb2]

        ingre_ingre_dis_dict = defaultdict()
        ingre_ingre_dis_list = []
        for ingre1 in ingres_from:
             for ingre2 in ingres_to:
                 ingre_ingre_dis = ingre_simple_obj.cal_closest_distance(ingre1, ingre2)
                 ingre_ingre_dis_dict[tuple([ingre1, ingre2])] = ingre_ingre_dis
                 ingre_ingre_dis_list.append(ingre_ingre_dis)
        herb_herb_distance = np.mean(ingre_ingre_dis_list)
        return herb_herb_distance, ingre_ingre_dis_dict


def main():
    # filename = 'source_data/stitch/new_database_chemical_target_sum.xlsx'
    filename = 'source_data/wbNBI/chemical_predict_target_screen.xlsx'
    ingredients_obj = Ingredients(filename, 0, 'hum')
    # ingre_obj = Ingredients(filename, 700, 'hum')

    # filename_2 = 'source_data/all ingredient intergration/herb_ingre_id_23_0909_2.csv'
    # herb_obj = Herb(filename_2)
    return ingredients_obj