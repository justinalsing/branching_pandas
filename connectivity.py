import numpy as np
import pickle


# "null" conenctivity model (single community)
class SingleCommunityConnectivity():

    def __init__(self):

        self.n_communities = 1

    # locations of children are all zeros irrespective of anything
    def draw_locations_of_children(self, c, n):

        return np.zeros(n).astype(int)

# three component connectivity class splitting into school/work/other and fixing transmission to occur 1/3 in home/work or school/out and about
class ThreePartConnectivity():
    
    def __init__(self, filename):
        
        self.school_occupancy, self.work_occupancy, self.home_interaction, self.gravity_interaction, self.p_school, self.p_workplace, self.p_occupation = pickle.load(open(filename, 'rb'))
   
        self.n_communities = len(self.work_occupancy)

   # draw locations of children given community of parent, c, and how many children to draw, n
    def draw_locations_of_children(self, c, n):

        # is the parent at school, working, or other?
        occupation = np.random.choice(np.arange(3), p=self.p_occupation[c,:])

        # if school
        if occupation == 0:

            school_location = np.random.choice(np.arange(self.n_communities), p=self.p_school[c,:])

            K = (2./3.)*self.school_occupancy[:,school_location]
            + (1./6)*self.home_interaction[c,:]
            + (1./6.)*self.gravity_interaction[c,:]
            K = K/np.sum(K)

        # if work
        if occupation == 1:

            work_location = np.random.choice(np.arange(self.n_communities), p=self.p_workplace[c,:])

            K = (2./3.)*self.work_occupancy[:,work_location]
            + (1./6.)*self.home_interaction[c,:]
            + (1./6.)*self.gravity_interaction[c,:]
            K = K/np.sum(K)

        # if other
        if occupation == 2:

            K = (1./2.)*self.home_interaction[c,:]
            + (1./2.)*self.gravity_interaction[c,:]
            K = K/np.sum(K)

        communities_of_children = np.random.choice(np.arange(self.n_communities), p=K, size=n)

        return communities_of_children


# three component connectivity class splitting into school/work/other and fixing transmission to occur 1/3 in home/work or school/out and about
class ThreePartConnectivityHeterogeneous():
    
    def __init__(self, filename):
        
        self.school_occupancy, self.work_occupancy, self.home_interaction, self.gravity_interaction, self.p_school, self.p_workplace, self.p_occupation = pickle.load(open(filename, 'rb'))
   
        self.n_communities = len(self.work_occupancy)

    # draw school location
    def draw_school_location(self, c):

        return np.random.choice(np.arange(self.n_communities), p=self.p_school[c,:])

    # draw school location
    def draw_work_location(self, c):

        return np.random.choice(np.arange(self.n_communities), p=self.p_workplace[c,:])

    # school infection locations
    def draw_school_infection_communities(self, c, n):

        K = self.school_occupancy[:,c]
        K = K/np.sum(K)

        return np.random.choice(np.arange(self.n_communities), p=K, size=n)

    # work infection locations
    def draw_work_infection_communities(self, c, n):

        K = self.work_occupancy[:,c]
        K = K/np.sum(K)

        return np.random.choice(np.arange(self.n_communities), p=K, size=n)

    # community infection locations
    def draw_community_infection_communities(self, c, n):

        K = self.gravity_interaction[c,:]
        K = K/np.sum(K)

        return np.random.choice(np.arange(self.n_communities), p=K, size=n)