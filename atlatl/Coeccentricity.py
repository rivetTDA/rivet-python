import math
def coeccentricity(dist_matrix):
    
    #The function computes a coeccentricity function on a finite metric space.
    #This is represented as a list of length equal to the number of elements in
    #the metric space.  The ith entry is equal to the -1 * (the sum of distance of the ith
    #point to each other point).  
    
    coeccen=[]
    for i in range(len(dist_matrix)):
        coeccen.append(-1*(sum(dist_matrix[i])))
    return coeccen
