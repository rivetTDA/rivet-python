import numpy as np

def matching_distance(Mod1,Mod2,Grid_Parameter,Normalize,Bounds):
    #Computes the approximate matching distance between two 2-Parameter persistence modules using
    #RIVET's command-line interface.

    #Input:
    #Mod1,Mod2: RIVET "precomputed" representations of two persistence modules, in Bryn's python bytes format   
    
    #Bounds is a list.  #It can be empty.  Alternatively, bounds can be a pair of numbers [LL,UR]
    #which specifies the bounds to work with.  
    #The purpose of this latter option is to allow the user to compute matching distances with 
    #uniform precision over a large collection of 2-D persistencem odules, which may exhibit features at different scales.
    
    #TODO: In the future Bounds should be an optional agrument, instead of this empty list nonsense.
    
    #Grid_Parameter: This is a non-negative integer which should be at least 1.
    #We choose Grid_parameter slopes between 0 and 90; we do not however consider the values 0 and 90, since
    #these are not considered in the definition of the matching distance.
    
    #Normalize: Do we compute the distances with constants chosen to simulate the situation where
    # the coordinates are rescaled so that UR-LL=[1,1]?
    
    if a!=[]
        [LL,UR]=Bounds
    else
        bounds1=bounds(mod1)
        bounds2=bounds(mod2)
    
        #in this case the algorithm chooses its own bounds, 
        #with the lower left bound taken to be the min for the two modules, 
        #and the upper right taken to be the max for the two modules.  
        LL=[np.min(bounds1[0][0],bounds2[0][0]),np.min(bounds1[0][1],bounds2[0][1])] 
        UR=[np.mmax(bounds1[1][0],bounds2[1][0]),np.max(bounds1[1][1],bounds2[1][1])] 
    
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
            barcode1=rivet.barcodes(computed1,[(i,j)])
            barcode2=rivet.barcodes(computed2,[(i,j)])
            raw_distance=hera.bottleneck_distance(multi_bars1[0], multi_bars2[0]))
            
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


