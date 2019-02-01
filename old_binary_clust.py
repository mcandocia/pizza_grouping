import csv
import numpy as np
import math
import time

distmat_array = []
with open('similarity.csv', 'r') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i == 0:
            names = row[1:]
        else:
            distmat_array.append([float(x) for x in row[1:]])

distmat = np.asarray(distmat_array)

#print(distmat)

def group_distance(g1, g2):
    dist = 0
    for a in g1:
        for b in g2:
            dist = dist + distmat[a,b]
    return dist/(len(g1)*len(g2))

finished_grouping = False
group_tier = -1

previous_groups = [frozenset([i]) for i in range(len(names))]

major_groupings = [previous_groups]
named_groupings = [{name} for name in names]

while not finished_grouping:
    group_tier += 1
    print(group_tier)
    time.sleep(0.01)
    print(previous_groups)
    grouped_groups = []
    new_groups = []
    previous_groups_ = list(previous_groups)
    for i, group in enumerate(previous_groups_):
        #print(i)
        if group in grouped_groups:
            #print('skipping...')
            continue
        if i == len(previous_groups_)-1:
            #print('not able to group this group %d in this tier, continuing...' % i)
            grouped_groups.append(group)
            new_groups.append(group)
            continue


        distances = [
            group_distance(group, g2) 
            if g2 not in grouped_groups
            else 1e6
            for g2 in previous_groups_[i+1:] 
        ]


        if (len(distances) == 0) or min(distances)==1e6:
            #print('not able to group this group %d in this tier, continuing....' % i)
            #print(grouped_groups)
            grouped_groups.append(group)
            new_groups.append(group)
            continue            

        min_index = i + distances.index(min(distances))+1
        # update grouped groups and new groups
        print('previously grouped groups: %s' % ascii(grouped_groups))
        print('Joining %s and %s' % (ascii(group), ascii(previous_groups[min_index])))
        new_groups.append(group | previous_groups[min_index])
        grouped_groups.append(group)
        grouped_groups.append(previous_groups[min_index])

    if len(previous_groups) == 1:
        finished_grouping=True

    previous_groups = new_groups
    major_groupings.append(new_groups)
    named_groups = [{names[i] for i in group} for group in new_groups]
    named_groupings.append(named_groups)

print(major_groupings)        
print(named_groupings)
        
        

