import math
def density_estimate(dist_matrix,p,use_percentile=True):

#The function computes a density estimate on a finite metric space.
#If use_percentile=True, then we take the density estimate to use 
#the ball estimator with radius parameter equal to the p^{th} percentile of 
#the non-zero values in the distance matrix.

#If use_percentile=False, then the raduis parameter is simply taken to be p.
    
    #get the radius parameter
    if not use_percentile:
        radius=p
    else:
        #put matrix entries in list form
        dist_list= [x for sublist in dist_matrix for x in sublist]
        
        #remove zeros from list
        dist_list=[x for x in dist_list if x !=0]
        
        dist_list.sort()
       
        index=math.floor(len(dist_list)*p/100)
        
        #edge cases with small numbers of points are a bit funny for this
        radius=dist_list[max(index-1,0)]
        
    dens_vector=[]
    for i in range(len(dist_matrix)):
        #count the number of entries of dist_matrix[i] which are smaller than or equal to radius
        dens_vector.append(sum(d<=radius for d in dist_matrix[i])-1)     
    return dens_vector
