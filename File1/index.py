def index():
    import os
    import numpy as np
    N=216
    M=np.zeros((1,N))
    for i in range(1,N+1):
        M[0][i-1] = i
    np.savetxt("index.txt",M, delimiter=',', fmt='%0i',newline='\n')
index()
