def compute_p_value(My_Module,Permuted_Module_List):

#
# We are given a 2P-persistence module, computed from time series via time delay embeddings, as well as 
# A collection of 2P-persistence modules computed from random permutations of this.  Names are given as strings.
#
# For each module in the collection, we compute the average distance to all others, 
# and we arrange this in a vector V.  
# Then, we return the percentage of values in V that are below the value for My_Module.
# 
# First, we need to compute the rectangle of interest for this computation in 
# 2D parameter space.
#
# Each module has a rectangle of interest; we take the rectangle of interest for the full computation
# to be the maximum of all of these.
#

    all_test_stats=[]

    for i in range(len(Permuted_Module_List):
        all_test_stats.append(test_statistic(Permuted_Module_List[i],Permuted_Module_List))

    all_test_stats.append(test_statistic(My_Module,Permuted_Module_List))all_test_stats.sort()      

    all_test_stats.append(test_statistic(Permuted_Module_List[i],Permuted_Module_List))

def test_statistic(My_Module,Module_List,LL,UR):
    # compute the average distance of My_Module to each module in Module_List

    dist_sum=0
    for i in range Module_List
        dist_sum=dist_sum+matching_distance(My_Module,Module_List[i],LL,UR,100,True)
    return dist_sum/len(Module_List)


                
                
