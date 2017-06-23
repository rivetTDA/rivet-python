import math
def codensity_estimate(dist_matrix,p,use_percentile=True,use_gaussian=False):
    
    #The function computes a codensity estimate on a finite metric space.
    #By a codensity estimate we simply mean -1 times a density estimate
    #If use_percentile=True, then we take the density estimate to use
    #the ball estimator with radius parameter equal to the p^{th} percentile of
    #the non-zero values in the distance matrix.
    
    #If use_percentile=False, then the radius parameter is simply taken to be p.
    
    #TODO: Introduce a normalization option?
    

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

    codens_vector=[]
    for i in range(len(dist_matrix)):
        if not use_gaussian:
            #count the number of entries of dist_matrix[i] which are smaller than or equal to radius
            #and multiply by -1
            codens_vector.append(-1*(sum(d<=radius for d in dist_matrix[i])-1))
        else:
            #use radius as a bandwidth for the gaussian
            codens_vector.append(-1*(sum(math.exp(-d**2/(2*radius**2))/(radius*math.sqrt(2*math.pi)) for d in dist_matrix[i])-1))
    return codens_vector
