import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.patches as patches
import plotly.graph_objs as go
import plotly.express as px
from sklearn import preprocessing
import itertools
import copy
import time

from callmine.callmine_focus.gen2Out.gen2out import gen2Out
from callmine.callmine_focus.gen2Out.utils import sythetic_group_anomaly, plot_results

from callmine.callmine_focus.LookOut.iForest import iForest, forest_outliers
from callmine.callmine_focus.LookOut.helper import get_coverage, generate_frequency_list
from callmine.callmine_focus.LookOut.LookOut import LookOut
from callmine.callmine_focus.LookOut.ranklist import generate_graph
from callmine.callmine_focus.LookOut.structures import Graph

# Global variables
fs = [6, 5] # Figure size
keys = ['out_degree', 'in_degree',
        'core', 'weighted_out_degree',
        'weighted_in_degree', 'in_median_iat',
        'in_call_count', 'in_median_measure',
        'out_median_iat', 'out_call_count',
        'out_median_measure']
min_max_scaler = preprocessing.MinMaxScaler()


def generate_feature_combinations(key_features, d=1):
    """
    Generate feature combinations with the
    set of informed features
    
    Parameters
    ----------
    key_features: array of str
        features to be combined
    d: int
        dimensionality, i.e., the number of
        features per combination
    """
    combinations = []
    plot_dict = {}
    
    for subset in itertools.combinations(keys, r=d):
        combinations.append(list(subset)[:])

    for i, c in enumerate(combinations):
        plot_dict[i] = c
    
    return combinations, plot_dict


def runGen2Out(ids, features, option=1):
    """
    Run gen2Out for anomaly detection
    
    Parameters
    ----------
    ids: array of str
        row ids
    features: array of str
        set of features to consider
        while running gen2Out
    option: int
        1 for point anomaly, 2 for group anomaly
    """
    model = gen2Out(lower_bound=9,
                upper_bound=12,
                max_depth=7,
                rotate=True,
                contamination='auto',
                random_state=0)
    
    if option==1: # point anomaly
        scores = model.point_anomaly_scores(X=features)
        tuples = [(ids[i], float(scores[i])) for i in range(0, len(ids))]
        scores = sorted(tuples, key = lambda x: x[1], reverse = True)
    else: # group anomaly
        scores, gindices = model.group_anomaly_scores(X=features,
                                                      x_ideal=0.1, y_ideal=1)
        
        tuples = [(ids[i], float(scores[0])) for i in gindices[0]]
        scores = sorted(tuples, key = lambda x: x[1], reverse = True)
        
    return scores
    

def run(N_val, B_val, P_val, df_features, features, rank_matrix, plot_combinations, outlier_ids):
    """
    Run CallMine-Focus
    
    Parameters
    ----------
    N_val: int
        number of outliers
    B_val: int
        budget, i.e., the number of plots to show
    P_val: int
    df_features: pandas DataFrame
        dataframe with features, node_ID
    features: array of str
        feature keys to consider
    rank_matrix: nd-array of float
        matrix with rows ranked by features
    plot_combinations: nd-array of str
        combinations of features
    outlier_ids: array
        ids of detected outliers
    """
    # Create graph between outliers and plots
    print("Generating Bipartite Graph")
    scaled_matrix, normal_matrix = generate_graph(P_val, rank_matrix, outlier_ids)
    saved_graph = Graph(scaled_matrix)
    print("Graph Generated Successfully")

    # Run appropriate algorithm to get list of selected graphs
    scatter_plots = len(plot_combinations)
    file = open("" + "log_CallMine-Focus.txt", 'w')

    algos = ["LookOut"]

    for algo in algos:
        print("\nIteration " + algo)
        graph = copy.deepcopy(saved_graph)
        print( "N_val = ", N_val, " Budget = ", B_val )

        start_time = time.time()
        print( "Running " + algo + " Algorithm" )
        plots = LookOut(graph, B_val, algo)
        frequencies = generate_frequency_list(plots, scaled_matrix)
        print('frequencies:', frequencies)
        
        print(algo + " Complete")
        elapsed_time = time.time() - start_time

        print("Saving Plots")
        coverage, max_coverage = get_coverage(plots, N_val, normal_matrix)
        
        print( "\t-> Total Plots Generated = ", end='' ); print(scatter_plots)
        print( "\t-> Total Plots Chosen = ", end='' ); print(len(plots))
        print( "\t-> Coverage = ", end='' ); print("{0:.3f} / {1:.3f}".format(coverage, max_coverage))

        # Inverse norm (for plotting)
        df_features[keys] = min_max_scaler.inverse_transform(df_features[keys])
        # features = min_max_scaler.inverse_transform(features)
        # df_features = pd.DataFrame(data=features, columns=keys)
        # df_features = df_features.rename_axis('node_ID').reset_index()

        # Save selected plots as png images
        for i, plot in enumerate(plots):
            pair = plot_combinations[plot]
              
            if dimensionality == 1:
                imgname = str(i) + '_' + str(plot) + '_histogram_plot'
                print(str(plot), end=' ')
                for p in pair:
                    imgname += '_' + p
                    print(str(p), end=' ')
                print()
                
                plotHistogram(df=df_features,
                            c1=pair[0],
                            frequencies=frequencies,
                            plot_number=plot,
                            figname=imgname+'.png',
                            show_plots=True)

            elif dimensionality == 2:
                imgname = str(i) + '_' + str(plot) + '_pair_plot'
                print(str(plot), end=' ')
                for p in pair:
                    imgname += '_' + p
                    print(str(p), end=' ')
                print()
                
                # plotScatterPlot
                # plotScatterPlot2
                # plotScatterPlot3
                # plotScatterPlot4

                plotScatterPlot3(df=df_features,
                            c1=pair[0],
                            c2=pair[1],
                            frequencies=frequencies,
                            plot_number=plot,
                            figname=imgname+'.png',
                            show_plots=False)

            elif dimensionality > 2:
                imgname = str(i) + '_' + str(plot) + '_parallel_coordinates'
                print(str(plot), end=' ')
                for p in pair:
                    imgname += '_' + p
                    print(str(p), end=' ')
                print()
                
                plot_parallel_coordinates(df_features,
                                          pair,
                                          frequencies=frequencies,
                                          plot_number=plot,
                                          figname=imgname+'.html',
                                          show_plots=True)
            
    file.close()
    print( "Finished" )
    return plots


def plotHistogram(df, c1, frequencies, plot_number, figname='2d-histogram.png', show_plots=True):
    """
    Plot 1-d histogram
    
    Parameters
    ----------
    df: pandas DataFrame
        features
    c1: string
        feature to plot
    frequencies: nd-array
        frequency of outliers
    plot_number: int
        number of plot to show
    figname: str
        name of figure to save
    show_plots: boolean
        option to show plot
    """
    plt.figure(figsize=fs)
    colors = len(df) * ['#808080']
    
    plt.hist(x=np.log10(df[c1]+1), bins=100)
    
    for outlier in frequencies.keys():
        if plot_number == frequencies[outlier][1]:
            plt.vlines(x = np.log10(df[c1].iloc[outlier]+1), ymin=0, ymax=plt.ylim()[1], linestyles='dashed', colors='red')##5C1A1B')
        else:
            plt.vlines(x = np.log10(df[c1].iloc[outlier]+1), ymin=0, ymax=plt.ylim()[1], linestyles='dashed', colors='green')#556270')
    
        plt.xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
        plt.ylabel('count')
    plt.yscale('log')
    plt.grid()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    plt.savefig(output_path+figname)

    if show_plots:
        plt.show()

def plotScatterPlot(df, c1, c2, frequencies, plot_number, figname='pair_plot.png', show_plots=True):
    """
    Plot 2-d histogram
    
    Parameters
    ----------
    df: pandas DataFrame
        features
    c1: string
        first feature to plot
    c2: string
        second feature to plot
    frequencies: nd-array
        frequency of outliers
    plot_number: int
        number of plot to show
    figname: str
        name of figure to save
    show_plots: boolean
        option to show plot
    """
    plt.figure(figsize=fs)
    plt.hexbin(np.log10(df[c1]+1), np.log10(df[c2]+1), mincnt=1, cmap='jet', bins='log')
    plt.xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
    plt.ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
    plt.colorbar()
    
    for outlier in frequencies.keys():
        size = frequencies[outlier][0]*10
        
        if plot_number == frequencies[outlier][1]:
            plt.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    # c='k',
                    facecolors='none',
                    edgecolor='red', linewidth=1, s = int(size))
        else:
            plt.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    facecolors='none',
                    edgecolor='blue', linewidth=1, s = int(size))
        
        plt.xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
        plt.ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
    
    plt.grid()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    plt.savefig(output_path+figname)
    
    if show_plots:
        plt.show()

def plotScatterPlot2(df, c1, c2, frequencies, plot_number, figname='pair_plot.png', 
                    show_plots=True, with_category=True, class_col='class'):
    """
    Plot 2-d histogram with outlier detection
    
    Parameters
    ----------
    df: pandas DataFrame
        features
    c1: string
        first feature to plot
    c2: string
        second feature to plot
    frequencies: nd-array
        frequency of outliers
    plot_number: int
        number of plot to show
    figname: str
        name of figure to save
    show_plots: boolean
        option to show plot
    with_category: boolean
        if True, plot categories in separate subplot
    class_col: string
        name of column containing class labels (1=lícito, 2=ilícito, 3=desconhecido)
    """
    
    if with_category and class_col is None:
        raise ValueError("class_col must be provided when with_category=True")
    
    # Configurar figura
    if with_category:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=fs)
    
    # Plot 1: Hexbin com outliers (comportamento original)
    hb = ax1.hexbin(np.log10(df[c1]+1), np.log10(df[c2]+1), mincnt=1, cmap='jet', bins='log', gridsize=50)
    ax1.set_xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
    ax1.set_ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
    plt.colorbar(hb, ax=ax1)
    
    for outlier in frequencies.keys():
        size = frequencies[outlier][0]*10
        
        if plot_number == frequencies[outlier][1]:
            ax1.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    facecolors='none', edgecolor='red', linewidth=2, s=int(size), 
                    label='Outlier principal' if outlier == list(frequencies.keys())[0] else '')
        else:
            ax1.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    facecolors='none', edgecolor='blue', linewidth=1, s=int(size),
                    label='Outros outliers' if outlier == list(frequencies.keys())[0] else '')
    
    ax1.grid(alpha=0.3)
    ax1.set_title('Distribuição com Outliers Destacados', fontweight='bold')
    
    # Plot 2: Scatter por categoria (se solicitado)
    if with_category:
        colors = {1: 'red', 2: 'green', 3: 'gray'}
        labels = {1: 'Ilícito', 2: 'Lícito', 3: 'Desconhecido'}
        
        for category in [1, 2, 3]:
            mask = df[class_col] == category
            ax2.scatter(np.log10(df[mask][c1]+1), np.log10(df[mask][c2]+1),
                       c=colors[category], alpha=0.5, s=20, label=labels[category],
                       edgecolors='black', linewidths=0.5)
        
        # Destacar outliers com borda preta grossa
        for outlier in frequencies.keys():
            size = frequencies[outlier][0]*10
            ax2.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                       facecolors='none', edgecolor='black', linewidth=2, s=int(size))
        
        ax2.set_xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
        ax2.set_ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
        ax2.grid(alpha=0.3)
        ax2.legend(loc='best')
        ax2.set_title('Distribuição por Categoria', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path + figname, dpi=100, bbox_inches='tight')
    
    if show_plots:
        plt.show()
    
    plt.close()

def plotScatterPlot3(df, c1, c2, frequencies, plot_number, figname='pair_plot.png', 
                    show_plots=True, with_category=True, class_col='class', exclude_unknown=True):
    """
    Plot 2-d histogram with outlier detection
    
    Parameters
    ----------
    df: pandas DataFrame
        features
    c1: string
        first feature to plot
    c2: string
        second feature to plot
    frequencies: nd-array
        frequency of outliers
    plot_number: int
        number of plot to show
    figname: str
        name of figure to save
    show_plots: boolean
        option to show plot
    with_category: boolean
        if True, plot categories in separate subplot
    class_col: string
        name of column containing class labels (1=lícito, 2=ilícito, 3=desconhecido)
    """
    
    if with_category and class_col is None:
        raise ValueError("class_col must be provided when with_category=True")
    
    # Configurar figura
    if with_category:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=fs)
    
    # Plot 1: Hexbin com outliers (comportamento original)
    # gridsize controla o tamanho dos hexágonos (menor = maior)
    hb = ax1.hexbin(np.log10(df[c1]+1), np.log10(df[c2]+1), 
                    mincnt=1, cmap='jet', bins='log', gridsize=80)  # Era padrão 100
    ax1.set_xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
    ax1.set_ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
    plt.colorbar(hb, ax=ax1)
    
    for outlier in frequencies.keys():
        size = frequencies[outlier][0]*10
        
        if plot_number == frequencies[outlier][1]:
            ax1.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    facecolors='none', edgecolor='red', linewidth=2, s=int(size))
        else:
            ax1.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                    facecolors='none', edgecolor='blue', linewidth=1, s=int(size))
    
    ax1.grid(alpha=0.3)
    ax1.set_title('Distribuição com Outliers Destacados', fontweight='bold')
    
    # Plot 2: Scatter por categoria (se solicitado)
    if with_category:
        colors = {1: 'red', 2: 'green', 3: 'gray'}
        labels = {1: 'Ilícito', 2: 'Lícito', 3: 'Desconhecido'}
        categories = [1, 2]
        if exclude_unknown == False:
            categories.append(3)

        for category in categories:
            mask = df[class_col] == category
            ax2.scatter(np.log10(df[mask][c1]+1), np.log10(df[mask][c2]+1),
                       c=colors[category], alpha=1, s=20, label=labels[category],
                       edgecolors='black', linewidths=0.5)
        
        # Destacar outliers com borda preta grossa
        for outlier in frequencies.keys():
            size = frequencies[outlier][0]*10
            ax2.scatter(np.log10(df.iloc[outlier][c1]+1), np.log10(df.iloc[outlier][c2]+1),
                       facecolors='none', edgecolor='black', linewidth=2, s=int(size))
        
        ax2.set_xlabel(c1.replace('_', ' ') + ' - log10(x+1)')
        ax2.set_ylabel(c2.replace('_', ' ') + ' - log10(x+1)')
        ax2.grid(alpha=0.3)
        ax2.legend(loc='best')
        ax2.set_title('Distribuição por Categoria', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path + figname, dpi=100, bbox_inches='tight')
    
    if show_plots:
        plt.show()
    
    plt.close()

def plot_parallel_coordinates(df_features,
                              columns, 
                              frequencies,
                              plot_number,
                              figname='parallel_coordinates.html',
                              show_plots=True):
    """
    Plot n-d parallel coordinates
    
    Parameters
    ----------
    df: pandas DataFrame
        features
    columns: array of str
        features to plot
    frequencies: nd-array
        frequency of outliers
    plot_number: int
        number of plot to show
    figname: str
        name of figure to save
    show_plots: boolean
        option to show plot
    """    
    
    colors = len(df_features) * [0]
    
    for outlier in frequencies.keys():
        if plot_number == frequencies[outlier][1]:
            colors[outlier] = 2
        else:
            colors[outlier] = 1
    
    df_features['colors'] = colors
    
    fig_parallel_coordinates = px.parallel_coordinates(
                               df_features[columns],
                               columns,
                               color_continuous_scale=['grey', 'blue', 'red'],
                               color=df_features['colors'], color_continuous_midpoint=1
                            )
    
    fig_parallel_coordinates.update_layout(#width=900,
                        height=550)
    fig_parallel_coordinates.update_layout(
                        font_size=22)
    
    fig_parallel_coordinates.write_html(output_path+figname)
    
    if show_plots:
        fig_parallel_coordinates.show()
    
def define_node_mapping(df):
    # ids únicos e ordenados
    unique_nodes = sorted(df['node_ID'].unique())

    # string -> int
    node_to_int = {node: i for i, node in enumerate(unique_nodes)}

    # int -> string (reverso)
    int_to_node = {i: node for node, i in node_to_int.items()}
    return node_to_int, int_to_node

# ===================================================================
# MAIN
# ===================================================================
def call_mine_main(argv):
    global detection_option, num_outliers, budget, dimensionality, output_path

    path_features       = argv[1]
    detection_option    = int(argv[2])
    num_outliers        = int(argv[3])
    budget              = int(argv[4])
    dimensionality      = int(argv[5])
    output_path         = argv[6]

    print("Running CallMine-Focus")
    print("Reading input file")

    df_raw = pd.read_csv(path_features)#, nrows=200)
    node_to_int, int_to_node = define_node_mapping(df_raw)

    print("Normalize features")
    df_features = df_raw.copy()
    df_features = df_features[['node_ID'] + keys]
    df_features[keys] = min_max_scaler.fit_transform(df_features[keys])
    df_features['node_ID'] = df_features['node_ID'].map(node_to_int)
    df_features = df_features.sort_values(by='node_ID').reset_index(drop=True)

    # df_features = min_max_scaler.fit_transform(df_features[keys].values)
    # df_features = pd.DataFrame(data=df_features, columns=keys)
    # df_features = df_features.rename_axis('node_ID').reset_index()

    print(df_features.head())

    print("Generate feature combinations")
    combinations, plot_dict = generate_feature_combinations(key_features=keys,
                                                            d=dimensionality)

    print("Rank outliers with feature combinations")
    rank_matrix =[]

    for i, combination in enumerate(combinations):
        print("Run Isolation Forest / gen2Out and get Scores (every pair of features) " + str(i+1) + " / " + str(len(combinations)),
                end="\r")
        
        if dimensionality == 1:
            scores = iForest(ids = df_features['node_ID'],
                                features = np.asarray(df_features[combination], dtype = float))
        else:
            scores = runGen2Out(ids = df_features['node_ID'],
                                features = np.asarray(df_features[combination], dtype = float),
                                option=detection_option)
        
        rank_matrix.append(scores)

    print("Run Isolation Forest / gen2Out and get Scores (all features)")
    if dimensionality == 1:
        scores = iForest(ids = df_features['node_ID'],
                            features = np.asarray(df_features[keys], dtype = float))
    else:
        scores = runGen2Out(ids = df_features['node_ID'],
                            features = np.asarray(df_features[keys], dtype = float),
                            option=detection_option)


    print("Get top outliers")
    outliers = forest_outliers(N=num_outliers, scores=scores)

    print('#scores:', len(scores))
    print('#df_features:', len(df_features))
    print('outliers:', outliers)
    outlier_circle_size = 40

    print(df_features.head())
    df_features['node_ID'] = df_features['node_ID'].map(int_to_node)
    df_features = df_features.merge(
        df_raw[['node_ID', 'class']],
        on='node_ID',
        how='left'
    )

    print(df_features.head())
    print(df_features['class'].value_counts())

    resulting_plots = run(N_val=num_outliers,
                        B_val=min(budget, len(combinations)),
                        P_val=1.0,
                        df_features=df_features,
                        features=np.asarray(df_features[keys], dtype = float),
                        rank_matrix=rank_matrix,
                        plot_combinations=plot_dict,
                        outlier_ids=outliers)


if __name__ == "__main__":
    if (len(sys.argv) != 7):
        print('Wrong number of input parameters.')
        print('Usage: <file path> <detection option (1 iForest, 2 gen2Out)> <num_outliers> <budget> <dimensionality> <output_path>')
    else:
        print('Running CallMine\'s attention routing...')
        call_mine_main(sys.argv)
        print('Done.')
