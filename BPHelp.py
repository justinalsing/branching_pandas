import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.special import softmax
import pandas as pd
import tqdm

import os
import imageio
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

#def extend_community_record(community_active_infections, active_infection_dataframe, n_communities):
#    infected_communities = active_infection_dataframe['community'].value_counts().index.values
#    infection_rates = active_infection_dataframe['community'].value_counts().values
#    current_community_active_infections = np.zeros(n_communities)
#    current_community_active_infections[infected_communities] = infection_rates
#    return np.append(community_active_infections,
#                                        np.expand_dims(current_community_active_infections, axis=0),
#                                        axis=0)

def current_community_infections(infection_dataframe, n_communities):
    infected_communities = infection_dataframe['community'].value_counts().index.values
    #print(infected_communities)
    infection_rates = infection_dataframe['community'].value_counts().values
    current_community_active_infections = np.zeros(n_communities)
    if len(infected_communities)>0:
        current_community_active_infections[infected_communities] = infection_rates
    return np.expand_dims(current_community_active_infections, axis=0)

#return np.append(community_active_infections,
#                                        np.expand_dims(current_community_active_infections, axis=0),
#                                        axis=0)



def make_connectivity(area='London'):
    
    areas = ['London', 'UK']
    
    if area not in areas:
        raise ValueError("Invalid area name. Expected one of: %s" % areas)
    
    dir = '../connectivity_data_' + area + '/'

    # flow: each element is the number of people who commute from one community to the other
    flow = pd.read_json(os.path.join(dir, 'connectivity_' + area + '.json')).values.T

    # population: number of people who live in a community
    population = pd.read_json(os.path.join(dir, 'population_' + area + '.json')).values.T[0]

    # number of commuters that live in (and leave from) each community
    num_commuters = np.sum(flow, axis = 1)

    # weight for each community staying at home is:
    # total population - commuters + commuters spending half of their time at home
    home_weight = np.diag(population - num_commuters)

    # weight of people having left each community to go to work
    work_weight = flow

    # connectivity
    connectivity = home_weight + work_weight

    # normalise connectivity
    row_sums = connectivity.sum(axis=1)
    connectivity = connectivity / row_sums[:, np.newaxis]

    n_communities = len(connectivity)

    fig, ax = plt.subplots(1);
    plot = ax.pcolormesh(np.log(connectivity), cmap = 'Reds')
    fig.colorbar(plot)
    ax.set_title('connectivity matrix')
    
    return connectivity, n_communities, population, fig