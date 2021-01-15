import matplotlib.pyplot as plt
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import networkx as nx

def map_setup(n_communities, area, small_network=False):
    # directory of data
    areas = ['London', 'UK']
    
    if area not in areas:
        raise ValueError("Invalid area name. Expected one of: %s" % areas)
    
    dir = '../connectivity_data_' + area + '/'
 
    # poly: spatial boundairies of communities (just useful for visualisation)
    poly = gpd.read_file(os.path.join(dir, 'poly_' + area +'.shp'))

    # points: the spatial centroids of the communities (just useful for visualisation)
    points = poly.copy()
    points.geometry = points['geometry'].centroid
    points.crs = poly.crs
    
    # option: if small network, focus on westminster
    if small_network:
        points = points[points['msoa11nm'].str.contains('Westminster')][:n_communities].reset_index()
        poly = poly[poly['msoa11nm'].str.contains('Westminster')][:n_communities].reset_index()
    
    node_positions = points.apply(lambda x: np.array(x['geometry']), axis=1)
    
    # make graph
    G = nx.Graph()
    G.add_nodes_from(points.index)
    
    return G, node_positions, poly

def init_figure():
    # We will plot the map and the connectivity graph.
    fig, ax = plt.subplots(1, figsize=(15, 15))

    # Turn the axes off.
    plt.axis('off')
    
    return fig, ax
    
def update_plot_parameters(time_index, n_communities, community_active_infections):
    # set up parameters for plotting nodes

    # node style
    node_size = [community_active_infections[time_index][i]**3 for i in range(n_communities)]
    linewidths = [.5*community_active_infections[time_index][i] for i in range(n_communities)]
    
    return node_size, linewidths

def convert_lists_to_timeseries(list):
    timeseries = np.array(list).T
    timeseries = timeseries.astype('float')
    timeseries[timeseries == 0] = np.nan
    return timeseries

def plot_timeseries(n_communities, time, infection_timeseries, symptomatic_timeseries, poly):
    fig, axs = plt.subplots(n_communities, 2, figsize=(10,10))

    for c in range(n_communities):

        axs[c, 0].plot(time, infection_timeseries[c],
                   color='red')
        axs[c, 0].fill_between(time, 0, symptomatic_timeseries[c],
                   color='blue', alpha=.2)

        axs[c, 0].set_ylim([0, np.nanmax(infection_timeseries)])
        axs[c, 0].set_xlim([0, time[-1]])

        poly.loc[c:c].plot(
            alpha=0.2,
            edgecolor='k',
            linewidth=0.8,
            ax=axs[c, 1])

        axs[c, 1].set_axis_off()

    fig.tight_layout()

    return fig


# plt.plot(time, df_to_active(time, dataframe))
# for n in range(n_communities):
#     plt.plot(time, df_to_active(time, dataframe[dataframe['community'] == n]))
def df_to_active(time, df):
    t_isos = sorted(df['isolation time'])
    t_infs = sorted(df['infection time'])

    active = [0]
    t_iso = t_isos.pop(0)
    t_inf = t_infs.pop(0)
    for t in range(1, int(time[-1]) + 1):
        change = 0
        while t > t_iso:
            change -= 1
            t_iso = t_isos.pop(0)
        while t > t_inf:
            change += 1
            t_inf = t_infs.pop(0)
        active.append(active[-1] + change)

    return active


# plt.plot(time, df_to_active(time, dataframe))
# for n in range(n_communities):
#     plt.plot(time, df_to_active(time, dataframe[dataframe['community'] == n]))
def df_to_symptomatic(time, df):
    t_isos = sorted(df['isolation time'])
    t_syms = sorted(df['symptomn onset time'])

    active = [0]
    t_iso = t_isos.pop(0)
    t_sym = t_syms.pop(0)
    for t in range(1, int(time[-1]) + 1):
        change = 0
        while t > t_iso:
            change -= 1
            t_iso = t_isos.pop(0)
        while t > t_sym:
            change += 1
            t_sym = t_syms.pop(0)
        active.append(active[-1] + change)

    return active


# plt.plot(time, df_to_Reff(time, dataframe))
def df_to_Reff(time, df):
    df_sorted = df.sort_values(by='infection time')
    t_infs = list(df_sorted['infection time'])
    parent_ids = list(df_sorted['parent id'])

    children = [0]  # zero infected at t=0
    counted_parent_ids = {None}  # ids of parents who have infected anyone at t=0
    parents = [1]  # number of parents who have infected anyone at t=0
    t_inf, parent_id = t_infs.pop(0), parent_ids.pop(0)  # get next row
    for t in range(1, int(time[-1]) + 1):
        c_change = 0
        while t > t_inf:
            c_change += 1  # increment children
            counted_parent_ids.add(parent_id)  # increment parents if unique
            t_inf, parent_id = t_infs.pop(0), parent_ids.pop(0)  # get next row
        children.append(children[-1] + c_change)
        parents.append(len(counted_parent_ids))

    Reff = [cp[0] / cp[1] for cp in zip(children, parents)]
    return Reff
