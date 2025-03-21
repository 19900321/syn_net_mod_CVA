import pandas as pd

from proximity_key import *
from collections import defaultdict

class Herb_Distance:
    def __init__(self, G_obj, Ingredients_obj, Herb_obj, disease_obj, herb_info):
        self.G_ogj = G_obj
        self.G = self.G_ogj.g
        self.Ingredients = Ingredients_obj
        self.Herb = Herb_obj
        self.Disease = disease_obj
        self.Herb_info = herb_info

    def length_fuc(self, nodes_from, nodes_to, distance_method):
        distance = self.Ingredients.ingre_ingre_dis(nodes_from, nodes_to, self.G, distance_method)
        return distance

    def herb_herb_length_dict(self, nodes_from, nodes_to, distance_method):

        length_dict = Sets_Lengths(nodes_from, nodes_to).ingre_length(self.length_fuc, distance_method)

        return length_dict

    def herb_herb_dis(self, herb_from, herb_to, distance_method, distance_method_herb_list):
        if any([herb not in self.Herb.herb_ingre_dict.keys() for herb in [herb_from, herb_to]]):
            print('herb {} or {} not in herb_ingre dictionary'.format(herb_from, herb_to))
            return None
        else:
            nodes_from = self.Herb.herb_ingre_dict[herb_from]
            nodes_to = self.Herb.herb_ingre_dict[herb_to]
            length_dict = self.herb_herb_length_dict(nodes_from, nodes_to, distance_method)
            saved_lengthes_dict = defaultdict()

            for distance_method_herb in distance_method_herb_list:
                dis_obj = Network_Distance(nodes_from, nodes_to, length_dict)
                distance = dis_obj.network_distance(distance_method_herb)
                saved_lengthes_dict[distance_method_herb] = distance

            distances = {'ingre_method': distance_method,
                    'two_level' : {'length_dict':length_dict,
                    'distances':saved_lengthes_dict}}
            return distances


    def herb_herb_distance_uni(self, herb_from, herb_to, distance_method):
        if any([herb not in self.Herb.herb_ingretargets_dic.keys() for herb in [herb_from, herb_to]]):
            print('herb {} or {} not in herb_ingretarget dictionary'.format(herb_from, herb_to))
            return None
        else:
            nodes_from = self.Herb.herb_ingretargets_dic[herb_from]
            nodes_to = self.Herb.herb_ingretargets_dic[herb_to]
            length_dict = Sets_Lengths(nodes_from, nodes_to).target_lengths(self.G)
            dis_obj = Network_Distance(nodes_from, nodes_to, length_dict)
            distance = dis_obj.network_distance(distance_method)
            distances = {'ingre_method': distance_method,
                    'one_level': {'union': distance}}
            return distances

    def herb_herb_dis_all(self, herb_from, herb_to):
        if any([herb not in self.Herb.herb_ingre_dict.keys() for herb in [herb_from, herb_to]]):
            print('herb {} or {} not in herb_ingre dictionary'.format(herb_from, herb_to))
            return None
        else:
            # method_list_ingre = ['separation', 'closest', 'shortest', 'kernel', 'center']
            # method_list_herb = ['separation', 'closest', 'shortest', 'kernel', 'center']
            method_list_ingre = ['closest', 'shortest', 'kernel', 'center']
            method_list_herb = [ 'closest', 'shortest', 'kernel', 'center']
            dis_dict = defaultdict()
            for method_ingre in method_list_ingre:
                values_two_level = self.herb_herb_dis(herb_from, herb_to,
                                                 method_ingre, method_list_herb)
                values_one_level = self.herb_herb_distance_uni(herb_from, herb_to, method_ingre)

                dis_dict[method_ingre] = {'two_level': values_two_level['two_level'],
                                          'one_level': values_one_level['one_level']}
            return dis_dict


    def generator_result(self, herb_pairs_list):
        herb_pairs_distances = defaultdict()
        n = 0
        k = 1
        for herb_pairs in herb_pairs_list:
            herb1, herb1_name, herb2, herb2_name, frequency = herb_pairs
            try:
                distances = self.herb_herb_dis_all(herb1, herb2)
                print('yes, herb pairs {} and {} are successful'.format(herb1, herb2))
                for ingre_method in distances.keys():
                    dict_1 = distances[ingre_method]['two_level']['distances']
                    #dict_2 = distances[ingre_method]['one_level']
                    #dict_1.update(dict_2)
                    dict_1.update({
                        'Ingredient-level distance type': ingre_method,
                        'herb1': herb1,
                        'herb1_name': herb1_name,
                        'herb2': herb2,
                        'herb2_name': herb2_name,
                        'frequency': frequency
                    })
                    n += 1
                    herb_pairs_distances[n] = dict_1
                k += 1
                print('this is the {}th successful pairs'.format(k))
            except:
                continue
        return pd.DataFrame.from_dict(herb_pairs_distances, orient='index')

    def cal_herb_disease(self, disease_from, herb_to, method, random_time, seed):
        d, z, m, s, pval = self.Disease.cal_disease_herb_z_score(disease_from, herb_to, method,
                                                            self.Herb.herb_ingretargets_dic, 10, 3333)
        herb_name = self.Herb_info.pinyin_herbid_dic.get(herb_to)
        herb_distance_dict = {'Disease': [disease_from], 'Herb ID':[ herb_to], 'Herb name': [herb_name],
         'distance': [d], 'Z-score': [z],
         'Mean-value': [m], 'stand_deviation': [s],
         'p-value': [pval[0]]}
        distance_pd = pd.DataFrame.from_dict(herb_distance_dict)
        return distance_pd

    def cal_herb_ingre_disease(self, disease_from, herb_to, distance_method, random_time, seed):
        herb_name = self.Herb_info.pinyin_herbid_dic.get(herb_to)
        ingre_z_score_dict = self.Disease.cal_disease_herb_ingre_z_score(disease_from, herb_to, distance_method,
                                                                         self.Herb.herb_ingre_dict,
                                                                         self.Ingredients.ingre_tar_dict,
                                                                         random_time, seed)

        columns_need = ['Disease name', 'Herb ID','Herb name',
                        'Ingredient ID', 'Ingredient name','distance', 'Z-score',
                                              'Mean-value', 'stand_deviation',
                                              'p-value']
        data = []
        for ingre, values in ingre_z_score_dict.items():
            ingre_name = self.Ingredients.ingre_id_name_dict_value.get(ingre)
            rows_add = [disease_from,  herb_to, herb_name, ingre, ingre_name] + list(values)
            data.append(rows_add)
        herb_ingre_disease_pd = pd.DataFrame(data, columns=columns_need )

        return herb_ingre_disease_pd


