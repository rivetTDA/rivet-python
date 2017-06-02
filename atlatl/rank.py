import math
import numpy as np
from atlatl import rivet, barcode, hera, matching_distance
from atlatl.rivet import Point, PointCloud

def find_parameter_of_point_on_line(sl,offset,point):
    #finds the RIVET parameter representation of point on the line (sl,offset).
    #recall that RIVET parameterizes by line length, and takes the point where the line intersets the positive x-axis or y-axis 
    #to be parameterized by 0.  If the line is itself the x-axis or y-axis, then the origin is parameterized by 0.  
    
    #WARNING: Code assumes that the point lies on the line, and does not check this.  
    #Relatedy, the function could be written using only slope or or offset as input, not both.
   
    if sl==90:
       return point[1]
    
    if sl==0:
       return point[0]
   
    #Otherwise the line is neither horizontal or vertical.  
    
    if point[0]==0 or point[1]==0:
       return 0
    
    #Find the point on the line parameterized by 0.
    #If offset is positive, this is a point on the y-axis, otherwise, it is a point on the x-axis.
    
    m=math.tan(math.radians(sl))
    if offset>0:
        y_int=point[1]-m*point[0]
        dist=np.sqrt(pow(point[1]-y_int,2)+pow(point[0],2))    
        if point[0]>0:
            return dist
        else:
            return -dist
    else:
        x_int=point[0]-point[1]/m
        dist=np.sqrt(pow(point[1],2)+pow(point[0]-x_int,2))    
        if point[1]>0:
            return dist
        else:
            return -dist    

def rank(module,a,b):
    """Uses the RIVET precomputed file format for a persistence module M to quickly compute the rank of the internal 
    linear map M(a,b).  
    
    This code could be made more efficient by modifying the code in the guts of RIVET, but this should be adequate 
    our present purposes.  
    
    Note that the rank function is unstable with respect to choice of a,b.  Because of numerical error, this function
    can instead return the value of the rank functon at points a',b' very close to a and b, which can be 
    different.  In a more careful implementation (done by tweaking the innards of RIVET) this could be avoided, 
    but shouldn't be a serious issue in our intended applications.  
    
    Input:
        module: RIVET "precomputed" representations of a persistence
        module, in Bryn's python bytes format

        a,b: each lists representing a point in R^2, with a1<=b1 and a2<=b2
    """

    #Check that the input is appropriate; if not, print a message and return -1.
    if a[0]>b[0] or a[1]>b[1]:
        print("Input to rank function not valid.  Returning -1.")
        return -1
      
    #First, determine the line containing a and b, in RIVET's (slope,offset) format.  
    #If a==b, we will just choose the vertical line.    
    
    #1.Find the slope (in degrees)
    if a[0]==b[0]:
       sl=90
    else:
        sl=(b[1]-a[1])/(b[0]-a[0])  
    
    #2.Find the offset 
    offset=matching_distance.find_offset(sl,a)
        
    #Next, find the coordinates of a and b on this line, with respect to RIVET's chosen parameterization of the line
    a_param=find_parameter_of_point_on_line(sl,offset,a)
    b_param=find_parameter_of_point_on_line(sl,offset,b)
    
    #get the barcode of the slice passing through points a and b
    line_and_barcode=rivet.barcodes(module,[(sl,offset)])[0]
    barcode=line_and_barcode[1].to_array()
    
    #now return the number of bars that are born by a and die after b.  
    count=0
    for i in range(len(barcode)):
        if barcode[i][0]<=a_param and barcode[i][1]>b_param:
            count=count+barcode[i][2]
    return count

def rank_norm(module,grid_size,fixed_bounds=None,use_weights=True,normalize=False,minimum_rank=0):
    """approximately computes the approximate (weighted) L_1-norm of the rank_invariant on a rectangle
    
    TODO: Adapt this to a version that also computes the L_1 norm of the difference between rank functions 
    from two different modules. 
    
    Input:
        module: RIVET "precomputed" representations of a persistence
        modules, in Bryn's python bytes format

        grid_size: This is a non-negative integer which should be at least 2.
            We will compute the norm approximately using a grid_size x grid_size grid.

        fixed_bound: A rivet.bounds object.  Specifies the rectangle over which we compute
        If none, the bounds are taken to be the bounds for the module provided by RIVET.

        use_weights: Boolean; Should we compute the norm in a weighted fashion, so that ranks M(a,b) 
        with a and b lying (close to) a horizontal or vertical line are weighted less?  
        Weights used are the same ones as for computing the matching distance.

        normalize: Boolean; is used only if use_weights=True.  In this case, the weights are chosen as if 
        the bounding rectangle were a rescaled to be a square.
        
        minimum_rank: Treat all ranks below this value as 0.  [Motivation: For hypothethsis testing where the 
        hypothesis is of the form: This data has at least k topological features.]
    """
    
    if fixed_bounds is None:
        # otherwise, determine bounds from the bounds of the two modules
        fixed_bounds = rivet.bounds(module)
        
    LL = fixed_bounds.lower
    UR = fixed_bounds.upper

    x_increment=(UR[0]-LL[0])/(grid_size-1)
    y_increment=(UR[1]-LL[1])/(grid_size-1)
    volume_element=pow(x_increment*y_increment,2)
  
    if volume_element==0:
        print('Rectangle is degenerate!  Behavior of the function in this case is not defined.' )
        return -1
    
    norm_so_far=0
    
    for x_low in range(grid_size):
        for y_low in range(grid_size):
            for x_high in range(x_low,grid_size):
                for y_high in range(y_low,grid_size):   
                          
                    a=[LL[0]+x_low*x_increment,LL[1]+y_low*y_increment]
                    b=[LL[0]+x_high*x_increment,LL[1]+y_high*y_increment]                   
                    
                    #TODO: In weighted case, weight should depend on a,b, and normalize.
                    if use_weights:
                        print('weighted norm not yet implemented')
                        return -1
                    
                    weight=1
                    current_rank=rank(module,a,b)
                    if current_rank<minimum_rank:
                        current_rank=0
                    
                    norm_so_far=norm_so_far+weight*volume_element*current_rank
        
    return norm_so_far
        
        
        