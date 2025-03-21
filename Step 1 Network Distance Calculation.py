
from itertools import combinations
from generate_objects import *
from disease import *
import matplotlib.pyplot as plt
import networkx as nx
g_obj.get_degree_binning(1001)
import pandas as pd

# this is used for changing data type
def expand_list(df, list_column, new_column):
    lens_of_lists = df[list_column].apply(len)
    origin_rows = range(df.shape[0])
    destination_rows = np.repeat(origin_rows, lens_of_lists)
    non_list_cols = (
      [idx for idx, col in enumerate(df.columns)
       if col != list_column]
    )
    expanded_df = df.iloc[destination_rows, non_list_cols].copy()
    expanded_df[new_column] = (
      [item for items in df[list_column] for item in items]
      )
    expanded_df.reset_index(inplace=True, drop=True)
    return expanded_df

def cal_fufang(herb_list):
    dis_list = []
    center_dict = defaultdict()
    herb_distance_pd = []
    herb_ingre_center_pd = pd.DataFrame(columns=['pairs', 'herb', 'center_ingredient'])
    for herb_pairs in list(combinations(herb_list, 2)):
        print(herb_pairs)
        herb1, herb2 = herb_pairs[0], herb_pairs[1]
        network_closest = Herb_Pair_network(herb_distance_obj, herb1, herb2, 'closest', 'closest', herb_info)
        huang_gan_dis_pd = network_closest.pd_ingre_pairs_dis
        dis_list.append(huang_gan_dis_pd)
        distance = network_closest.herb_level_distance
        herb1_id = herb_info.herb_pinyin_dic[herb1]
        herb2_id = herb_info.herb_pinyin_dic[herb2]
        herb_distance_pd.append([herb1, herb1_id, herb2, herb2_id, distance])
        network_closest.center_ingredients.update({'distance': distance})
        center_dict[herb1+herb2] = network_closest.center_ingredients

    #center_pd = prepare_center_distance_list(center_dict)
    herb_ingre_dis_pd = pd.DataFrame(herb_distance_pd, columns=['herb id',
                                                                'herb1_name',
                                                                'herb2',
                                                                'herb2_name',
                                                                'distance'])
    ingre_ingre_dis_pd = pd.concat(dis_list)

    # prepare herb ID -ingredeint id
    herb_id_list = [herb_info.herb_pinyin_dic.get(h) for h in herb_list]
    herb_ingre_dict_used = {k: v for k, v in herb_distance_obj.Herb.herb_ingre_dict.items() if k in herb_id_list}
    herb_ingre_id_pairs = pd.DataFrame.from_dict({'herb_id':herb_ingre_dict_used.keys(), 'ingredient_id':herb_ingre_dict_used.values()})
    herb_ingre_id_pairs = expand_list(herb_ingre_id_pairs, 'ingredient_id', 'ingredient_id')
    return herb_ingre_dis_pd, ingre_ingre_dis_pd, herb_ingre_id_pairs
# use herb:center, ingre:closest as final distance, 6.25

class Herb_Pair_network:
    def __init__(self, herb_distance_obj, herb_from_name, herb_to_name, ingre_method, herb_method, herb_info):
        self.herb_from_name = herb_from_name
        self.herb_to_name = herb_to_name
        self.herb_distance_obj = herb_distance_obj
        self.herb_from = herb_info.herb_pinyin_dic[self.herb_from_name]
        self.herb_to = herb_info.herb_pinyin_dic[self.herb_to_name]
        self.distance_network = herb_distance_obj.herb_herb_dis_all(self.herb_from, self.herb_to)
        self.ingre_method = ingre_method
        self.herb_method = herb_method
        self.ingre_distance_dict_list = self.distance_network[self.ingre_method]['two_level']['length_dict']
        self.herb_level_distance = self.get_herb_level_distance()
        self.pd_ingre_pairs_dis = self.get_ingre_distance_pd()
        self.herb_ingre_id_name = self.get_herb_ingre_id_name_dict()
        self.pd_herb_ingre = self.get_herb_ingre_pd()
        self.center_ingredients = self.get_center_ingredients()
        self.ingre_z_dict = defaultdict()
        self.herb_z_dict = defaultdict()
        self.herb_ingre_z_dict = defaultdict()

    def get_herb_level_distance(self):
        return self.distance_network[self.ingre_method]['two_level']['distances'][self.herb_method]

    def name_find(self, ingre_id):
        return ingredients_obj.ingredients_info(ingre_id)['name']

    def name_trans_herb(self, herb_id):
        return herb_info.pinyin_herbid_dic[herb_id]

    def get_ingre_distance_pd(self):
        pd_ingredients = pd.concat([pd.DataFrame.from_dict(i, orient='index').stack().reset_index()
                                    for i in self.ingre_distance_dict_list])
        pd_ingredients.columns = ['node_from', 'node_to', 'distance']
        pd_ingredients['node_from_name'] = pd_ingredients['node_from'].apply(self.name_find)
        pd_ingredients['node_to_name'] = pd_ingredients['node_to'].apply(self.name_find)
        return pd_ingredients

    def get_herb_ingre_id_name_dict(self):
        return {self.herb_from: {ingre: self.name_find(ingre) for ingre in self.ingre_distance_dict_list[2].keys()},
                self.herb_to: {ingre: self.name_find(ingre) for ingre in self.ingre_distance_dict_list[3].keys()}}

    def get_herb_ingre_pd(self):
        pd_herb_ingre = pd.DataFrame.from_dict({k: v.keys() for k, v in self.herb_ingre_id_name.items()},
                                               orient='index').stack().reset_index()
        pd_herb_ingre.columns = ['node_from', 'index_add', 'node_to']
        pd_herb_ingre = pd_herb_ingre.drop(['index_add'], axis=1)
        pd_herb_ingre['node_from_name'] = pd_herb_ingre['node_from'].apply(self.name_trans_herb)
        pd_herb_ingre['node_to_name'] = pd_herb_ingre['node_to'].apply(self.name_find)

        return pd_herb_ingre

    def get_center_ingredients(self):
        ingredients_from = get_center_one(self.ingre_distance_dict_list[2].keys(), self.ingre_distance_dict_list[2])
        ingredients_to = get_center_one(self.ingre_distance_dict_list[3].keys(), self.ingre_distance_dict_list[3])
        return {self.herb_from_name: {ingre: self.name_find(ingre) for ingre in ingredients_from},
                self.herb_to_name: {ingre: self.name_find(ingre) for ingre in ingredients_to}}

    # def get_disease_herb_ingre_z(self, disease_obj, disease, herb, distance_method, herb_ingre_dict, ingre_tar_dict,
    #                              random_time, seed):
    #     ingre_disease_dict = disease_obj.cal_disease_herb_ingre_z_score(self, disease, herb, distance_method,
    #                                                                     herb_ingre_dict, ingre_tar_dict,
    #                                                                     random_time, seed)
    #     ingre_disease_pd = pd.DataFrame.from_dict(ingre_disease_dict, orient='index',
    #                                               columns=['d', 'z', 'm', 's', 'p_val'])
    #     ingre_disease_pd['herb'] = self.name_trans_herb(herb)
    #     ingre_disease_pd['herb_id'] = herb
    #     ingre_disease_pd['ingre_id'] = ingre_disease_pd.index
    #     ingre_disease_pd['ingre_name'] = ingre_disease_pd['ingre_id'].apply(self.name_find)
    #
    #     return ingre_disease_dict, ingre_disease_pd

    def get_disease_herb_ingre_z(self, disease_from, random_time, seed):
        herb_ingre_disease_z = defaultdict()
        herb_ingre_disease_z_from = self.herb_distance_obj.cal_herb_ingre_disease(disease_from, self.herb_from, 'closest',random_time, seed)
        herb_ingre_disease_z_to = self.herb_distance_obj.cal_herb_ingre_disease(disease_from, self.herb_to, 'closest',random_time, seed)
        herb_ingre_disease_z[self.herb_from] = herb_ingre_disease_z_from
        herb_ingre_disease_z[self.herb_to] = herb_ingre_disease_z_to
        self.herb_ingre_disease_z = herb_ingre_disease_z
        return herb_ingre_disease_z

    def get_disease_herb_z(self, disease_from, random_time, seed):
        self.herb_disease_z = self.herb_distance_obj.cal_herb_disease(disease_from, self.herb_from, 'closest',
                                                                      random_time, seed)
        herb_disease_z = defaultdict()
        herb_disease_z_from = self.herb_distance_obj.cal_herb_disease(disease_from, self.herb_from, 'closest',
                                                                      random_time, seed)
        herb_disease_z_to = self.herb_distance_obj.cal_herb_disease(disease_from, self.herb_to, 'closest',
                                                                      random_time, seed)
        herb_disease_z[self.herb_from] = herb_disease_z_from
        herb_disease_z[self.herb_to] = herb_disease_z_to
        self.herb_disease_z = herb_disease_z
        return herb_disease_z

def cal_fufang_disease(herb_list, herb_distance_obj, Disease,  disease_from_list):
    # prepare herb-disease,
    herb_disease_list = []
    herb_disease_ingre_list = []
    for herb_from_name in herb_list:
        herb_from = herb_info.herb_pinyin_dic.get(herb_from_name)
        print(herb_from)
        for disease_from in disease_from_list:
            disease_ingre_pd = herb_distance_obj.cal_herb_ingre_disease(disease_from, herb_from, 'closest', 100, 333)
            disease_herb_pd = herb_distance_obj.cal_herb_disease(disease_from, herb_from, 'closest',100, 333)
            herb_disease_list.append(disease_herb_pd)
            herb_disease_ingre_list.append(disease_ingre_pd)
    herb_disease_pd = pd.concat(herb_disease_list, axis=0)
    herb_disease_ingre_pd = pd.concat(herb_disease_ingre_list, axis=0)

    return herb_disease_pd, herb_disease_ingre_pd

def cal_fufang_paired(herb_list, herb_distance_obj):
    dis_list = []
    center_dict = defaultdict()
    herb_distance_pd = []
    herb_ingre_center_pd = pd.DataFrame(columns=['pairs', 'herb', 'center_ingredient'])
    herb_disease_list = []
    # prepare herb-disease,

    for herb_pairs in list(combinations(herb_list, 2)):
        print(herb_pairs)
        herb1, herb2 = herb_pairs[0], herb_pairs[1]
        network_closest = Herb_Pair_network(herb_distance_obj, herb1, herb2, 'closest', 'closest', herb_info)

        huang_gan_dis_pd = network_closest.pd_ingre_pairs_dis
        huang_gan_dis_pd['herb1_name'] = herb1
        huang_gan_dis_pd['herb2_name'] = herb2
        dis_list.append(huang_gan_dis_pd)

        distance = network_closest.herb_level_distance
        herb1_id = herb_info.herb_pinyin_dic[herb1]
        herb2_id = herb_info.herb_pinyin_dic[herb2]

        herb_distance_pd.append([herb1, herb1_id, herb2, herb2_id, distance])
        network_closest.center_ingredients.update({'distance': distance})
        center_dict[herb1 + herb2] = network_closest.center_ingredients

    # center_pd = prepare_center_distance_list(center_dict)
    herb_ingre_dis_pd = pd.DataFrame(herb_distance_pd, columns=['herb id',
                                                                'herb1_name',
                                                                'herb2',
                                                                'herb2_name',
                                                                'distance'])


    ingre_ingre_dis_pd = pd.concat(dis_list)

    # prepare herb ID -ingredeint id
    herb_id_list = [herb_info.herb_pinyin_dic.get(h) for h in herb_list]
    herb_ingre_dict_used = {k: v for k, v in herb_distance_obj.Herb.herb_ingre_dict.items() if k in herb_id_list}
    herb_ingre_id_pairs = pd.DataFrame.from_dict(
        {'herb_id': herb_ingre_dict_used.keys(), 'ingredient_id': herb_ingre_dict_used.values()})
    herb_ingre_id_pairs = expand_list(herb_ingre_id_pairs, 'ingredient_id', 'ingredient_id')
    herb_ingre_id_pairs['herb_name'] = herb_ingre_id_pairs['herb_id'].apply(lambda x:herb_info.pinyin_herbid_dic[x])
    herb_ingre_id_pairs['ingredient_name'] = herb_ingre_id_pairs['ingredient_id'].apply(lambda x:ingredients_obj.ingre_id_name_dict_value[x])
    return herb_ingre_dis_pd, ingre_ingre_dis_pd, herb_ingre_id_pairs


# generate all methods in center,
def get_ingre_dis(herb_distance_obj, herb_info, method_list):
    dis_list = []
    center_dict = defaultdict()
    for m in method_list:
        huang_gan_network = Herb_Pair_network(herb_distance_obj, 'HUANG QI', 'GAN CAO', m, 'center', herb_info)
        huang_gan_dis_pd = huang_gan_network.pd_ingre_pairs_dis
        dis_list.append(huang_gan_dis_pd)
        distance = huang_gan_network.herb_level_distance
        huang_gan_network.center_ingredients.update({'distance': distance})
        center_dict[m] = huang_gan_network.center_ingredients
    return dis_list, center_dict


def prepare_center_distance_list(center_dict):
    center_pd = pd.DataFrame.from_dict(center_dict, orient='index')
    center_pd['methods'] = list(center_pd.index)
    center_pd_2 = center_pd.melt(id_vars=['methods', 'distance'], var_name='herb')
    center_prepared = []
    for index, value in center_pd_2.iterrows():
        dict_col = value['value']
        for k, v in dict_col.items():
            col_S = [value['methods']] + [value['herb']] + [k] + [v] + [value['distance']]
            center_prepared.append(col_S)
    center_prepared_new = pd.DataFrame(center_prepared, columns=['methods',  'herb', 'ingre_id', 'ingre_name', 'distance'])
    return center_prepared_new


def prepare_center_distance_list_2(center_dict, mean_pd_top):
    center_pd = pd.DataFrame.from_dict(center_dict, orient='index')
    center_pd['Ingredient-level distance type'] = list(center_pd.index)
    center_pd['HUANG QI_2'] = center_pd['HUANG QI'].apply(lambda x: list(x.values()))
    center_pd['GAN CAO_2'] = center_pd['GAN CAO'].apply(lambda x: list(x.values()))

    mean_pd_top = mean_pd_top[mean_pd_top['Herb-level distance type'] == 'center']
    pre_pd = pd.merge(mean_pd_top, center_pd, 'inner', left_on='Ingredient-level distance type', right_on='Ingredient-level distance type')
    # prepare to paper format
    center_pd = pre_pd.copy()
    center_pd['center of HUANG QI'] = center_pd['HUANG QI_2'].apply(lambda x: ';'.join(x))
    center_pd['center of GAN CAO'] = center_pd['GAN CAO_2'].apply(lambda x: ';'.join(x))
    center_pd = center_pd.rename(
        columns={'random': 'Distance for random herb pairs', 'distance': 'Distance for HuangQiGanCao', 'top': 'Distance for top herb pairs',
                 'herb_method': 'Herb-level distance type',
                 'ingre_method': 'Ingredient-level distance type'})
    center_pd = center_pd[['center of HUANG QI',
                           'center of GAN CAO',
                           'Ingredient-level distance type',
                           'Distance for HuangQiGanCao',
                           'Distance for top herb pairs',
                           'Distance for random herb pairs']]
    center_pd = center_pd.round(decimals=2)
    return pre_pd, center_pd

# prepare cytoscape
def ingre_target_network(ingre_1_list, ingre_2_list, g_obj, ingredients_obj, how):
    ingre_name_1 = ';'.join([ingredients_obj.ingre_id_name_dict_value[ingre_1] for ingre_1 in ingre_1_list])
    ingre_name_2 = ';'.join([ingredients_obj.ingre_id_name_dict_value[ingre_2] for ingre_2 in ingre_2_list])
    t1 = []
    for ingre_1 in ingre_1_list:
        t1 += ingredients_obj.ingre_tar_dict[ingre_1]

    t2 = []
    for ingre_2 in ingre_2_list:
        t2 += ingredients_obj.ingre_tar_dict[ingre_2]

    t_s = list(set(t1 + t2))
    t_all = []
    for t_1, t_2 in combinations(t_s, 2):
        nodes_related = nx.shortest_path(g_obj.G, t_1, t_2)
        t_all += nodes_related

    t_all = list(set(t_all))
    g_sub_focus =  nx.Graph(g_obj.G.subgraph(t_all))

    # add ingre-target
    edge_1 = [(ingre_1, i) for i in list(ingredients_obj.ingre_tar_dict[ingre_1]) for ingre_1 in ingre_1_list ]
    edge_2 = [(ingre_2, i) for i in list(ingredients_obj.ingre_tar_dict[ingre_2]) for ingre_2 in ingre_2_list]
    ingre_list = ingre_1_list + ingre_2_list
    g_sub_focus.add_edges_from(edge_1)
    g_sub_focus.add_edges_from(edge_2)


     # change lable
    node_label = {t:get_symble_from_entries(t[1:]) if t not in ingre_list else ingredients_obj.ingre_id_name_dict_value[t] for t in g_sub_focus.nodes }
    print(node_label.values())

    # genrate node color dict by group
    node_color_dict = defaultdict()
    for t in g_sub_focus.nodes:
        if t in t1 and t not in t2:
            node_color_dict[node_label[t]] = 'red'
        elif t in t2 and t not in t1:
            node_color_dict[node_label[t]] = 'green'
        elif t in t2 and t in t1:
            node_color_dict[node_label[t]] = 'yellow'
        elif t in ingre_list:
            node_color_dict[node_label[t]] = 'orange'
        else:
            node_color_dict[node_label[t]] = 'grey'

    H = nx.relabel_nodes(g_sub_focus, node_label)
    node_color = []
    for n in H.nodes:
        node_color.append(node_color_dict[n])
    options = {
        'node_color': node_color,
        'node_size': 2000,
        'width': 2,
        'alpha': 0.9,
        'font_size':12
    }
    ax = plt.figure(figsize=(15, 10))
    nx.draw(H, with_labels= True,
            edge_color = 'grey',
            font_weight='bold',
            **options)
    plt.title('center ingredient nodes {} (yellow node) and {} (blue nodes)'.format(ingre_name_1, ingre_name_1))
    print('center ingredient nodes {} of GAN CAO (red node) and {} of HUANG QI (green nodes)'.format(ingre_name_1, ingre_name_2))
    if how == 'save_figure':
        plt.savefig('figure/Figure 6.png')
    elif how == 'plot_figure':
        plt.show()
    return H

def plot_center_network(center_dict, method, g_obj, ingredients_obj, how):
    ingre_1_list = list(center_dict[method]['GAN CAO'].keys())
    ingre_2_list = list(center_dict[method]['HUANG QI'].keys())
    ingre_target_network(ingre_1_list, ingre_2_list, g_obj, ingredients_obj, how)



#The final file generation and processing.
def fangji_rela_calcu(herb_info,fangji_list):
    herb_all = herb_info.data
    is_in_column = herb_all['Pinyin Name'].isin(fangji_list)
    rows_containing_elements = herb_all[is_in_column]
    herb_list = rows_containing_elements['Pinyin Name'].tolist()
    herb_herb_dis_pd, ingre_ingre_dis_pd, herb_ingre_id_pairs = cal_fufang_paired(herb_list, herb_distance_obj)
    herb_herb_dis = herb_herb_dis_pd.iloc[:, [0, 2, 4]]
    herb_herb_dis.columns = ['herb1', 'herb2', 'distance']
    herb_herb_dis = herb_herb_dis.drop_duplicates().dropna()
    ingre_ingre_dis=ingre_ingre_dis_pd.iloc[:,[3,4,2]]
    ingre_ingre_dis['Combination'] = ingre_ingre_dis[['node_from_name', 'node_to_name']].apply(lambda x: ''.join(sorted(x)), axis=1)
    ingre_ingre_dis = ingre_ingre_dis.drop_duplicates(subset=['Combination', 'distance'])
    ingre_ingre_dis =ingre_ingre_dis.drop(columns=['Combination'])
    ingre_ingre_dis =ingre_ingre_dis.dropna().drop_duplicates()
    ingre_ingre_dis.columns=['ingre1','ingre2','distance']
    herb_ingre_pairs = herb_ingre_id_pairs.iloc[:, [2, 3]]
    herb_ingre_pairs=herb_ingre_pairs.dropna().drop_duplicates()
    herb_ingre_pairs.columns = ['herb', 'ingredient']
    return herb_list, herb_herb_dis, ingre_ingre_dis, herb_ingre_pairs

#Taking Suhuang Zhike Capsules as an example
def main():
    fangji_herb_list=['MA HUANG','ZI SU YE','ZI SU ZI','CHAN TUI','QIAN HU','NIU BANG ZI','WU WEI ZI','DI LONG','PI PA YE']
    disease_list = ['Cough Variant Asthma']
    herb_list, herb_herb_dis, ingre_ingre_dis, herb_ingre_pairs=fangji_rela_calcu(herb_info,fangji_herb_list)
    herb_disease_pd, herb_disease_ingre_pd = cal_fufang_disease(herb_list, herb_distance_obj, disease_obj,
                                                                disease_list)
    ##save_file
    # herb_herb_dis.to_csv('result/SH_herb_herb_distance.csv', index=None)
    # ingre_ingre_dis.to_csv('result/SH_ingre_ingre_distance.csv', index=None)
    # herb_ingre_pairs.to_csv('result/SH_herb_ingredient_pairs.csv', index=None)
    # herb_disease_pd.to_csv('result/SH_herb_disease_pd.csv', index=None)
    # herb_disease_ingre_pd.to_csv('result/SH_herb_disease_ingre_pd.csv', index=None)




