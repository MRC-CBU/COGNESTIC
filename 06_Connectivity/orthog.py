def orthog(x,y):
#orthogonalize x with respect to y
# that means we fit y to X and take the regressors x~y and grab residuals
    if not y.size:
        o=x;
    else:
        if y.ndim == 1:
            y=np.expand_dims(y,axis=1)
        o=x-y@np.linalg.pinv(y)@x;
        
    return o
