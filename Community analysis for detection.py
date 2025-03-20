import networkx as nx
import pandas as pd
from communities.algorithms import louvain_method
from sklearn.preprocessing import MinMaxScaler


def file_pre_processing(HHf, IIf, DHf, DIf):
    HH = pd.read_csv(HHf).drop_duplicates()
    II = pd.read_csv(IIf).drop_duplicates()
    DH = pd.read_csv(DHf).drop_duplicates()
    DI = pd.read_csv(DIf).drop_duplicates()
    HH_pro = HH.rename(columns={'herb1': 'node_from', 'herb2': 'node_to'})
    II['Combination'] = II[['ingre1', 'ingre2']].apply(lambda x: ''.join(sorted(x)), axis=1)
    II_pro = II.drop_duplicates(subset=['Combination', 'distance']).drop(columns=['Combination'])
    II_pro.columns = ['node_from', 'node_to', 'distance']
    DH_pro = DH.iloc[:, [0, 2, 3]].rename(
        columns={'Disease': 'node_from', 'Herb name': 'node_to', 'distance': 'distance'}).drop_duplicates()
    DI_pro = DI.iloc[:, [0, 4, 5]].rename(
        columns={'Disease name': 'node_from', 'Ingredient name': 'node_to', 'distance': 'distance'}).drop_duplicates()
    sum_file = pd.concat([II_pro, DH_pro, DI_pro,HH_pro], axis=0)
    return sum_file,DH_pro,DI_pro,DH,DI

def detect_communities(sum_file):
    sum_file['distance1'] = max(sum_file['distance']) - sum_file['distance']
    sum_file = sum_file.iloc[:, [0, 1, 3]]
    sum_file.columns = ['node1', 'node2', 'weight']
    unique_values = pd.unique(sum_file[['node1', 'node2']].values.ravel())
    node_self = pd.DataFrame({'node1': unique_values, 'node2': unique_values, 'weight': 1})
    combined_data = pd.concat([node_self, sum_file], axis=0).drop_duplicates()
    G = nx.Graph()
    for i in range(len(combined_data)):
        node1 = combined_data.iloc[i]['node1']
        node2 = combined_data.iloc[i]['node2']
        weight = combined_data.iloc[i]['weight']
        if not G.has_edge(node1, node2):
            G.add_edge(node1, node2, weight=weight)
    adj_matrix = nx.to_scipy_sparse_matrix(G)
    adj_matrix_np = adj_matrix.toarray()
    communities, frames = louvain_method(adj_matrix_np)
    return  G,  adj_matrix_np, communities, frames

def communities_result_of_disease(G,communities,DI,DH):
    node_list = list(G.nodes())
    node_df = pd.DataFrame(node_list, columns=['Value'])
    node_index = node_list.index("Cough Variant Asthma")
    print("Node 'Cough Variant Asthma' is at index:", node_index)
    for i, s in enumerate(communities):
        if node_index in s:
            print("The element {} is in the {} set.".format(node_index, i + 1))
            break
    else:
        print("The element {} is not in any set.".format(node_index))
    set = communities[i]
    DHI_result = node_df.loc[node_df.index.isin(set)]
    subset_data_I= DI[DI['Ingredient name'].isin(DHI_result['Value'])]
    subset_data_H= DH[DH['Herb name'].isin(DHI_result['Value'])]
    return  DHI_result,subset_data_I,subset_data_H

def communities_result_of_all_result(G,communities):
    node_list = list(G.nodes())
    node_detect_df = pd.DataFrame(node_list, columns=['Value'])
    node_detect_df['community_id'] = None
    for community_id, community_set in enumerate(communities):
        node_detect_df.loc[node_detect_df.index.isin(community_set), 'community_id'] = community_id
    return node_detect_df

def deal_admet_file(DHC,DIC,ADMET):
    ADMET1 = ADMET[['tcmsp_ingredient_name','tcmsp_ingredient_ob',
                    'tcmsp_ingredient_drug_likeness']]
    DHC_select = DHC[(DHC['Z-score'] < 0) & (DHC['p-value'] < 0.05) ]
    DIC_ADMET = pd.merge(DIC, ADMET1, left_on='Ingredient name', right_on='tcmsp_ingredient_name',
                         how='left').drop_duplicates()
    DIC_ADMET = DIC_ADMET[(DIC_ADMET['tcmsp_ingredient_ob'] > 30) & (DIC_ADMET['tcmsp_ingredient_drug_likeness'] > 0.18)]

    return DHC_select,DIC_ADMET

def deal_file_for_sum(SZfile, SHfile, HLfile, JWfile, SGfile):
    JWfile['FJ'] = 'JWDCT'
    SGfile['FJ'] = 'SGMHT'
    SHfile['FJ'] = 'SHZKJN'
    SZfile['FJ'] = 'SZJQT'
    HLfile['FJ'] = 'HLZKKL'
    sum_file = pd.concat([SZfile, SHfile, HLfile, JWfile, SGfile], axis=0)
    return sum_file

###Data Processing Before Sankey Diagram
def data_processing_before_sankey_diagram(sum_ADMET_file):
    sankey_diagram_file= sum_ADMET_file.iloc[:, [0,2,4,5]].drop_duplicates()
    sankey_diagram_file.columns = ['disease', 'herb', 'ingredient','distance']
    return sankey_diagram_file
###Data Processing for_hierarchical_cluster
def deal_cluster_result_for_matrix(DH_file,sankey_diagram_file):
    DH_file=DH_file.iloc[:, [0,2,3,8]].drop_duplicates()
    DH_file.columns = ['node_from', 'node_to', 'distance', 'FJ']
    DI_file=sankey_diagram_file.iloc[:, [0,2,3,4]].drop_duplicates()
    DI_file.columns = ['node_from', 'node_to', 'distance', 'FJ']
    matrix_pre_file = pd.concat([DI_file,DH_file])
    return matrix_pre_file

def matrix_file_for_hierarchical_cluster(sum_file,pre_file):
    sum_file['adjusted_distance']=max(sum_file['distance'])-sum_file['distance']
    sum_file_combined = pd.concat([
        sum_file.iloc[:, [0, 1, 4]],
        sum_file.iloc[:, [1, 0, 4]].rename(columns={'node_to': 'node_from', 'node_from': 'node_to'})
    ]).drop_duplicates()
    sum_file_combined.columns = ['node_from', 'node_to','distance']
    node_rela= sum_file_combined[sum_file_combined['node_from'].isin(pre_file['node_to']) & sum_file_combined['node_to'].isin(pre_file['node_to'])]
    unique_nodes = set(node_rela['node_from'].unique()).union(set(node_rela['node_to'].unique()))
    all_nodes = pd.DataFrame({
        'node_from': list(unique_nodes),
        'node_to': list(unique_nodes),
        'distance': max(sum_file['distance'])
    })
    node_matrix_file=pd.concat([all_nodes, node_rela], axis=0).drop_duplicates().reset_index(drop=True)
    node_matrix_file = node_matrix_file.drop_duplicates(["node_from", "node_to"])
    scaler = MinMaxScaler()
    node_matrix_file['distance'] = scaler.fit_transform(node_matrix_file['distance'].values.reshape(-1, 1))
    final = node_matrix_file.pivot(index="node_from", columns="node_to", values="distance")
    for label in final.index:
        final.loc[label, label] = 1
    min_value = final.min().min()  # 找到最小值
    matrix_filled = final.fillna(min_value)
    type_file = pre_file.iloc[:, [1, 3]].drop_duplicates()
    return matrix_filled,min_value,type_file




# ##Using Suhuang as an example for demonstration.
# ADMETf='XX/admet.xlsx'
# ADMET = pd.read_excel(ADMETf).drop_duplicates()
# HHf='XX/suhuangzhike/herb_herb_distance.csv'
# IIf='XX/suhuangzhike/ingre_ingre_distance.csv'
# DHf='XX/suhuangzhike/herb_disease_pd.csv'
# DIf='XX/suhuangzhike/herb_disease_ingre_pd.csv'
# SHsum_file,SH_DH_por, SH_DI_por,SH_DH,SH_DI = file_pre_processing( HHf, IIf, DHf, DIf)
# SHsum_file = SHsum_file[(SHsum_file['distance'] < 1.3)|(SHsum_file['node_from'] == 'Cough Variant Asthma') | (SHsum_file['node_to'] == 'Cough Variant Asthma')]
# SH_G, SH_adj_matrix_np, SH_communities, SH_frames = detect_communities(SHsum_file)
# print(list(SH_frames[-1].items())[1])
# SHresult,SHsubset_data_I,SHsubset_data_H = communities_result_of_disease(SH_G,SH_communities,SH_DI,SH_DH)
# SHDHC_select,SHDIC_ADMET= deal_admet_file(SHsubset_data_H,SHsubset_data_I,ADMET)
# SH_node_detect_df=communities_result_of_all_result(SH_G,SH_communities)
#
#
# ##Results merged for the five formulas.
# DIC_all_ADMET_file = deal_file_for_sum(SZDIC_ADMET, SHDIC_ADMET, HLDIC_ADMET, JWDIC_ADMET, SGDIC_ADMET)
# sankey_diagram_file=data_processing_before_sankey_diagram(DIC_all_ADMET_file)
# sankey_diagram_file.to_csv('/sankey_diagram_file.csv', index=None)
# ##matrix_pre_file
# DHC_all_file=deal_file_for_sum(SZDHC_select, SHDHC_select, HLDHC_select, JWDHC_select, SGDHC_select)
# matrix_pre_file=deal_cluster_result_for_matrix(DHC_all_file,sankey_diagram_file)
# matrix_sum_file=deal_file_for_sum(SZsum_file, SHsum_file, HLsum_file, JWsum_file, SGsum_file)
# matrix_sum_file.to_csv('/FJ_sum_file.csv')



