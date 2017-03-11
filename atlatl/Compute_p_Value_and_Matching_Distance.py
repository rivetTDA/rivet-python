t
def compute_p_value(My_Module,Permuted_Module_List):
import numpy as np

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


def get_Corners(My_Module):
    # return format: [[x-lower-left,y-lower-left],[x-upper-right,y-upper-right]]
    # to be inherited from a function in RIVET
    #TODO: Implement in RIVET

def test_statistic(My_Module,Module_List,LL,UR):
    # compute the average distance of My_Module to each module in Module_List

    dist_sum=0
    for i in range Module_List
        dist_sum=dist_sum+matching_distance(My_Module,Module_List[i],LL,UR,100,True)
    return dist_sum/len(Module_List)    
    
    
def find_offset(sl,pt)    
    #find the offset parameter for the line of given slope passing through the point
    #slope is in degrees
    
    m=np.tan(np.radians(sl)
    # equation of line is y=mx+(pt[1]-pt[0]m)
    # We want the point x,y which minimizes squared distance to origin.
    #i.e., x^2(1+m^2)+2x(pt[1]m-pt[0]m^2)+c
    # minimized when derivative is 0, i.e., 
    # x=-2(pt[1]m-pt[0]m^2)/(1+m^2)

    b=pt[1]-pt[0]*m
    
    x_minimizer=-2*(pt[1]*m-pt[0]*m^2)/(1+m^2)
    y_minimizer=m*x_minimizer+b
    unsigned_dist=np.sqrt(x_minimizer^2+y_minimizer^2)
    
    if b>0: 
        return unsigned_dist
    else:
        return -unsigned_dist
            

def matching_distance(Mod1,Mod2,LL,UR,Grid_Parameter,Normalize):
    #Computes the approximate matching distance between two 2-Parameter persistence modules using
    #RIVET's command-line interface.

    #Input:
    #Mod1,Mod2: Two persistence modules, given as file names (RIVET output files)    
    ##LL, UR, Lower Left and Upper Right Coordinates of box in which we will consider slices

    #Grid_Parameter: This is a non-negative integer which should be at least 1.
    #We choose Grid_parameter slopes between 0 and 90; we do not however consider the values 0 and 90, since
    #these are not considered in the definition of the matchin distance.
    
    #Normalize: Do we compute the distances with constants chosen to simulate the situation where
    # the coordinates are rescaled so that UR-LL=[1,1]?
    

    matching_distance=0;

    for i in range(Grid_Parameter)
    #the ith slope is 90*i/Grid_parameter 
        sl=90*(k+1)/(Grid_Parameter+1)
    
        #find the offset parameters such that the lines with slope sl just touches the upper left corner of the box
        UL=[LL[1],UR[2]]
        UL_Offset=find_offset(sl,UL)
        LR=[UR[1],LL[2]]
        LR_Offset=find_offset(sl,LR)
        
        for j in range(Grid_Parameter):
            offset=LR_Offset+(k+1)*(UL_Offset-LR_Offset)/(Grid_Parameter+1)
        
            #this is the raw bottleneck distance computed with RIVET and Hera
            raw_distance=0;
            
            #To determine the weight to use for the line given by (sl,offset), we need to take into account both
            #the weight coming from slope of the line, and also the normalization, which changes both the effective 
            #weight and the effective bottleneck distance.  
            
            #first, let's recall how the reweighting works in the unnormalized case.  According to the 
            #definition of the matching distance, we choose 
            #the weight so that if the interleaving distance between Mod1 and Mod2 is 1, then the weighted bottleneck
            #distance between the slices is at most 1.
            
            m=np.tan(np.radians(sl))
            
            if Normalize=False:       
                q=max(m,1/m)
                w=1/np.sqrt(1+q^2)
                
                matching_distance=np.max([matching_distance,w*raw_distance])
            
            #next, let's consider the normalized case.  If the unnormalized slope is sl, then the normalized slope 
            #is given as follows
            
            if Normalize=True:  
                delta_x=UR[1]-LL[1]
                delta_y=UR[2]-LL[2]
                mn=m*delta_x/delta_y
            
            #so the associated weight in the normalized case is given by
            
                q=max(mn,1/mn)
                w=1/np.sqrt(1+q^2)
            
            #of course, this code can be made more compact, but hopfully this way is readible    
                
            #moreover, normalizaion changes the length of a line segment along the line (sl,offset), 
            #and hence also the bottleneck distance, by a factor of 
            
                bottleneck_stretch=sqrt(((m/delta_y)^2+(1/delta_x)^2)/(m^2+1))
                matching_distance=np.max([matching_distance,w*raw_distance*bottleneck_stretch])
                
                
