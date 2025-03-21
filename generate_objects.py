import pickle
import pandas as pd
from herb_ingre_tar import *
from construct_network import *
from herb_distance_generation import *
from herb_herb_pairs import *
import disease


g_obj = Construct_Network("source_data/toy.sif")

filename = 'source_data/stitch_database_chemical_target_sum.xlsx'
ingredients_obj = Ingredients(filename, 700, 'hum')
ingredients_obj.ingredients_target_dict(g_obj.G.nodes)

filename_2 = 'source_data/herb_ingre_info.csv'
herb_obj = Herb(filename_2)
herb_obj.herb_ingre_dic(ingredients_obj.ingre_tar_dict)
herb_obj.herb_ingretargets_dic(ingredients_obj.ingre_tar_dict)

filename_3 = 'source_data/herb_info.csv'
herb_info = Herb_Info(filename_3 )

fangji = FangJi('source_data/prescription.txt', herb_info.herb_pinyin_dic)
disease_file_name = 'source_data/disease_genes.csv'
disease_obj = disease.Disease(disease_file_name, g_obj)

herb_distance_obj = Herb_Distance(g_obj, ingredients_obj, herb_obj, disease_obj, herb_info)

result_dict = {'g_obj': g_obj,
                'ingredients_obj': ingredients_obj,
                'herb_obj': herb_obj,
                'herb_distance_obj': herb_distance_obj,
                'fangji': fangji,
               'herb_info': herb_info,
               'diseease_obj':disease_obj}

