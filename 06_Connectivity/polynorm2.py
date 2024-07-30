def polynorm2(data,n=1,z=1,o=1):
    # function replicating Riks polynom matlab function
    # it performs a polynomial expansion of a single numpy vector - 
    #data upto order n and scales it and orthogonalizes each next degree to previous one
    # Works on numpy arrays and single columns of panda frames, it also gives the intercept
    # no need to demean since if orthogonalizing it will regress out the intercept from the first order term
# see http://davmre.github.io/blog/python/2013/12/15/orthogonal_poly
    
    import numpy as np
    assert data.ndim == 1,'data should be 1-d'

    def orthog(x,y):
    #orthogonalize x with respect to y
        if not y.size:
            o=x;
        else:
            if y.ndim == 1:
                y=np.expand_dims(y,axis=1)
            o=x-y@np.linalg.pinv(y)@x;
        
        return o
    
    if n > data.shape[0]:
        raise Exception("Sory order expansion of %d is not possible for data of length %d"%(n,data.shape[0]))
    
    #X = np.empty_like(data)
    
    for p in range(0,n+1):
        nX = data**p
        if p>0 and o==1:
            nX = orthog(nX,X)
        
        if p>0 and z==1:
            nX = nX/np.std(nX)
            
        if p ==0:
            X = nX
        else:
            X = np.column_stack([X,nX])
            

    
    return X
