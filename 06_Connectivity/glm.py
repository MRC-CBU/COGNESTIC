def glm(Y,X,C,tailed=2):
# generic function to run GLM, consider using statsmodels
# Does not deal with missing values
# This runs a GLM from design matrix X on Array of DVs in Y
# X and Y have to be numpy array e.g., X (40,2) and Y (40,741)
# C is the contrast array e.g., [0,1] for a t-test or [[1,0],[0,1]] for an F-test
# % Output
# %    t = T-value
# %    F = F-value
# %    p = p-value
# %    df = degrees of freedom 
# %    R2  = model fit (% variance explained)
# %    cR2 = contrast fit (% variance explained)
# %    B = p betas (parameter estimates)
# %    aR2 = adjusted model fit (% variance explained)
# %    iR2 = hacky incremental model fit (not validated)
# %    Bcov = covariance of B (zero if errors white?)
# This function is converted to Python from Matlab - original function was written by Rik Henson 2004 see here https://github.com/MRC-CBU/riksneurotools/blob/master/GLM/glm.m
    import numpy as np
    from scipy.stats import t as TDIST
    from scipy.stats import f as FDIST

    if not X.size:
        error('Needs Design Matrix')
    if not Y.size:
        error('Needs a DV vector')
    if not C.size:
        error('Needs a contrast vector e.g., [0,1]')
    
    if X.ndim == 1:
        X = np.expand_dims(X,axis=1)
    # needs to add a constant
    if X.shape[1] ==1:
        constant = np.ones((X.shape[0],1))
        X = np.hstack((constant, X))
    if Y.ndim == 1:
        Y = np.expand_dims(Y,axis=1)
        
    if C.ndim == 1:
        C = np.expand_dims(C,axis=1)
    
    B = np.linalg.pinv(X)@Y
    Yhat = np.dot(X,B)
    r = Y - Yhat # residuals
    cE = np.eye(r.shape[0])
    Bcov = np.linalg.pinv(X)@cE@np.linalg.pinv(X).T
    
    if C.shape[1] > C.shape[0]:
        print('Transposing C')
        C = C.T
    
    
    l = C.shape[0]
    if l < X.shape[1]:
        C = np.vstack((C,np.zeros((X.shape[1]-l,C.shape[1]))))
        print('Padding C with zeros!')
        
    df = Y.shape[0] - np.linalg.matrix_rank(X)
    
    # computing T and F seperately
    
    if C.shape[1] == 1:
        s = r.T@r 
        s = np.diag(s)/df # this is needed to make it work with multiple DVs
        s = np.expand_dims(s,axis=1)
        t = np.squeeze((C.T@B)) / np.squeeze(np.sqrt(s@C.T@np.linalg.pinv(X.T@X)@C))
        if tailed == 2:
            p = 2*TDIST.cdf(-np.abs(t),df) # two tailed t test
        else:
            p = TDISC.cdf(t,df) # one tailed
        
        F = t**2
        cR2 = 1*F/(df+1*F) # During testing this was the same as the stats models R2
        R2 = 1-np.diag(r.T@r) / np.diag(Y.T@Y)
        aR2 = 1 - np.diag(r.T@r / df) / np.diag(Y.T@Y / (len(Y) -1))
    else:
        C_0 = np.eye(X.shape[1]) - C@np.linalg.pinv(C)
        X_0 = X@C_0
        R = np.eye(X.shape[0]) - X@np.linalg.pinv(X)
        R_0 = np.eye(X.shape[0]) - X_0@np.linalg.pinv(X_0)
        M = R_0 - R
        df = np.array([np.linalg.matrix_rank(X) - np.linalg.matrix_rank(X_0), X.shape[0] - np.linalg.matrix_rank(X)])
        F = (np.diag((B.T@X.T@M@X@B))/ df[0]) / (np.diag(Y.T@Y) / df[1])
        p = 1 - FDIST.cdf(F,df[0],df[1])
        cR2 = df[0]*F / (df[1] + df[0]*F) # note in python * is hadamar product and @ is matrix product
        R2 = 1 - np.diag(r.T@r) / np.diag(Y.T@Y)
        aR2 = 1 - np.diag(r.T@r / df[-1]) / np.diag(Y.T@Y / (len(Y) - 1))
        
    
    C_0 = np.eye(X.shape[1]) - C@np.linalg.pinv(C)
    X_0= X@C_0
    y_0 = X_0@(np.linalg.pinv(X_0)@Y)
    r_0 = Y - y_0
    iR2 = R2 - (1 - np.diag(r_0.T@r_0)/ np.diag(Y.T @ Y))
    
    return t,F,p,df,R2,cR2,B,r,aR2,iR2,Bcov