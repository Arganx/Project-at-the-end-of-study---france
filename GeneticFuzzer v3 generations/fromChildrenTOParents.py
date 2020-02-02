import random

def parentsToChildren(children,children_cov,parents,parents_cov):
    uniqueSet = set()
    while(len(children) + len(uniqueSet) < len(parents)):
        position = random.choice(range(len(parents)))
        uniqueSet.add(position)
    for x in uniqueSet:
        children.append(parents[x])
        children_cov.append(parents_cov[x])
    return children, children_cov


parents = [1,2,3,4,5,6]
children = [7,8,9]
parents_cov= [324234,4354353456,543534,5435,7565,456]
children_cov=[534543,768768,2436]
if(len(children) < len(parents)):
    parentsToChildren(children,children_cov,parents,parents_cov)
print(parents)
print(parents_cov)
print(children)
print(children_cov)