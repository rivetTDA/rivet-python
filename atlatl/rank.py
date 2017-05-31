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

