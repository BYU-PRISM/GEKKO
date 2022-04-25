from gekko import GEKKO
m = GEKKO()
# create x / xi arrays
x=[8,8,8,6,6,9,9,9]; n=len(x)
xi = [m.Param(i,lb=6,ub=9,integer=True) for i in x]
# count functions
bins = [6,7,8,9]; nb = len(bins)
bC = m.Array(m.Var,(nb,n))
for j,b in enumerate(bins):
    bL = [m.if3(xi[i]-(b-0.1),0,1) for i in range(n)]
    bU = [m.if3(xi[i]-(b+0.1),1,0) for i in range(n)]
    m.Equations([bC[j,i]==bU[i]*bL[i] for i in range(n)])
k = m.Array(m.Var,nb)
m.Equations([k[j]==m.sum(bC[j,:]) for j in range(nb)])
m.solve()
print('bC=',bC)
print('k=',k)
