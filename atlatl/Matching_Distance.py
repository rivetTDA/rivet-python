import numpy as np
from atlatl import rivet, barcode, hera
from atlatl.rivet import Point, PointCloud

def find_offset(sl,pt):    
    #find the offset parameter for the line of given slope passing through the point
    #slope is in degrees
    
    m=np.tan(np.radians(sl))
    # equation of line is y=mx+(pt[1]-pt[0]m)
    # We want the point x,y which minimizes squared distance to origin.
    #i.e., x^2(1+m^2)+2x(pt[1]m-pt[0]m^2)+c
    # minimized when derivative is 0, i.e., 
    # x=-2(pt[1]m-pt[0]m^2)/(1+m^2)

    b=pt[1]-pt[0]*m
    
    x_minimizer=-2*(pt[1]*m-pt[0]*m**2)/(1+m**2)
    y_minimizer=m*x_minimizer+b
    unsigned_dist=np.sqrt(x_minimizer**2+y_minimizer**2)
    
    if b>0: 
        return unsigned_dist
    else:
        return -unsigned_dist

def matching_distance(Mod1,Mod2,Grid_Parameter,Normalize,Fixed_Bounds):
    #Computes the approximate matching distance between two 2-Parameter persistence modules using
    #RIVET's command-line interface.

    #Input:
    #Mod1,Mod2: RIVET "precomputed" representations of two persistence modules, in Bryn's python bytes format   
    
    #Grid_Parameter: This is a non-negative integer which should be at least 1.
    #We will choose Grid_Parameter values of slope and also choose Grid_Parameter offset values, for each slope.
    
    #Normalize: Boolean; True iff we compute the distances with constants chosen to simulate the situation where
    # the coordinates are rescaled so that UR-LL=[1,1]?
    
    #Fixed_Bounds is a list.  
    #It can be empty.  Alternatively, Fixed_Bounds can be a pair of numbers [LL,UR]
    #which specifies the bounds to work with.  
    #The purpose of this latter option is to allow the user to compute matching distances with 
    #uniform precision over a large collection of 2-D persistence modules, which may exhibit features at different scales.
    
    #TODO: In the future Fixed_Bounds should be an optional agrument, instead of this empty list nonsense.
    
    #First, use Fixed_Bounds to set the upper right corner and lower-left corner to be considered.
    if Fixed_Bounds!=[]:
        [LL,UR]=Fixed_Bounds
    else:
        bounds1=rivet.bounds(Mod1)
        bounds2=rivet.bounds(Mod2)
    
        #If Fixed_Bounds is empty (i.e., not specified) the algorithm chooses its own bounds, 
        #with the lower left bound taken to be the min for the two modules, 
        #and the upper right taken to be the max for the two modules.  
        LL=[min(bounds1.lower[0],bounds2.lower[0]),min(bounds1.lower[1],bounds2.lower[1])]
        UR=[max(bounds1.upper[0],bounds2.upper[0]),max(bounds1.upper[1],bounds2.upper[1])] 
    
    #Now we build up a list of the lines we consider in computing the matching distance.  
    #Each line is given as a (slope,offset) pair.
    List_Of_Lines=[];
    
    for i in range(Grid_Parameter):
        #We will choose Grid_parameter slopes between 0 and 90; 
        #we do not however consider the values 0 and 90, since in view of stability considerations
        #these are not considered in the definition of the matching distance.  
        sl=90*(i+1)/(Grid_Parameter+1)
        
        #find the offset parameters such that the lines with slope sl just touches the upper left corner of the box
        UL=[LL[0],UR[1]]
        UL_Offset=find_offset(sl,UL)
        LR=[UR[0],LL[1]]
        LR_Offset=find_offset(sl,LR)
        
        #Choose the values of offset for this particular choice of sl.
        if Grid_Parameter==1:
            List_Of_Lines.append((sl,UL_Offset-LR_Offset))
        #largest and smallest offsets specify lines that touch 
        #the upper left and lower right corners of the rectangular region of interest.
        else:
            for j in range(Grid_Parameter):
                offset=LR_Offset+j*(UL_Offset-LR_Offset)/(Grid_Parameter-1)    
                List_Of_Lines.append((sl,offset))

    #next, for each of the two 2-D persistence modules, get the barcode associated to the list of lines. 
    multi_bars1=rivet.barcodes(Mod1,List_Of_Lines)
    multi_bars2=rivet.barcodes(Mod2,List_Of_Lines)  
    
    #now compute matching distance
    m_dist=0
    
    for i in range(len(List_Of_Lines)):
        #first compute the unweighted distance between the pairs
        raw_distance=hera.bottleneck_distance(multi_bars1[i][1], multi_bars2[i][1])
                       
        #To determine the weight to use for the line given by (sl,offset), we need to take into account both
        #the weight coming from slope of the line, and also the normalization, which changes both the effective 
        #weight and the effective bottleneck distance.
            
        #first, let's recall how the reweighting works in the unnormalized case.  According to the 
        #definition of the matching distance, we choose 
        #the weight so that if the interleaving distance between Mod1 and Mod2 is 1, then the weighted bottleneck
        #distance between the slices is at most 1.
        
        sl=List_Of_Lines[i][0];
        m=np.tan(np.radians(sl))
            
        if Normalize==False:       
            q=max(m,1/m)
            w=1/np.sqrt(1+q**2)
                
            m_dist=max(m_dist,w*raw_distance)
            
        #next, let's consider the normalized case.  If the unnormalized slope is sl, then the normalized slope 
        #is given as follows
            
        if Normalize==True:  
            delta_x=UR[0]-LL[0]
            delta_y=UR[1]-LL[1]
            if delta_y==0:
                print('corner case where delta_y=0 not addressed.  expect a divide-by-0 problem')
            mn=m*delta_x/delta_y
            
            
            #so the associated weight in the normalized case is given by
            
            q=max(mn,1/mn)
            w=1/np.sqrt(1+q**2)
            
            #of course, this code can be made more compact, but hopfully this way is readible    
                
            #moreover, normalizaion changes the length of a line segment along the line (sl,offset), 
            #and hence also the bottleneck distance, by a factor of             
            bottleneck_stretch=np.sqrt(((m/delta_y)**2+(1/delta_x)**2)/(m**2+1))
            m_dist=max(m_dist,w*raw_distance*bottleneck_stretch)

    return m_dist
