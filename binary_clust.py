import csv
import numpy as np
import math
import time
import json

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

# cache results I guess...
gd_cache = dict()
def group_distance(g1, g2):
    if frozenset([g1,g2]) in gd_cache:
        return gd_cache[frozenset([g1,g2])]

    dist = 0
    for a in g1:
        for b in g2:
            dist = dist + distmat[a,b]
    gd_cache[frozenset([g1,g2])] = dist/(len(g1)*len(g2))
    return dist/(len(g1)*len(g2))

finished_grouping = False
group_tier = -1

previous_groups = [frozenset([i]) for i in range(len(names))]

major_groupings = [list(previous_groups)]

named_groupings = [{name} for name in names]
priority_group = None

while not finished_grouping:
    group_tier += 1
    print(group_tier)
    print(previous_groups)
    grouped_groups = []
    new_groups = []
    previous_groups_ = list(previous_groups)
    finished_tier = False
    while not finished_tier:
        if priority_group is not None:
            priority_distances = [
                group_distance(priority_group, g2)
                if g2 != priority_group
                else 1e7
                for g2 in previous_groups
                
            ]
            min_dist = min(priority_distances)
            g1 = priority_group
            g2 = previous_groups[priority_distances.index(min_dist)]
            new_groups.append((g1 | g2))

            previous_groups.remove(g1)
            previous_groups.remove(g2)
            print('priority combining %s and %s' % (ascii(g1), ascii(g2)))
            priority_group = None
            if len(previous_groups) == 1:
                new_groups.append(previous_groups[0])
                priority_group = previous_groups[0]
                finished_tier = True
                print('only doing priority match this round...one singleton left')
            elif len(previous_groups) == 0:
                print('singleton match finished off groups')
                finished_tier = True
            continue

        group_dist_array = np.asarray([
            [
                group_distance(g1, g2)
                if g1 != g2
                else 1e6
                for g1 in previous_groups
            ]
            for g2 in previous_groups
        ])
        min_dist_idx = group_dist_array.argmin(1)
        if np.min(group_dist_array) == 1e6:
            new_groups.extend(previous_groups)
            finished_tier = True
        else:
            g1 = previous_groups[min_dist_idx[0]]
            g2 = previous_groups[min_dist_idx[1]]
            new_groups.append((g1 | g2))

            previous_groups.remove(g1)
            previous_groups.remove(g2)
            print('combining %s and %s' % (ascii(g1), ascii(g2)))

        if len(previous_groups) == 1:
            new_groups.append(previous_groups[0])
            priority_group = previous_groups[0]

            finished_tier = True
        elif len(previous_groups) == 0:
            finished_tier = True


    major_groupings.append(list(new_groups))
    previous_groups = list(new_groups)
    #print(new_groups)
    named_groupings.append([frozenset([names[i] for i in group]) for group in new_groups])
    if len(new_groups) == 1:
        finished_grouping=True
print('NG')
print(named_groupings)
print('MG')
print(major_groupings)
        
merge_history = list()
cluster_definitions = {g:-(i+1) for i, g in enumerate(major_groupings[0])}
heights = []
order_dict = {}

cluster_index_counter = 1

"""
for i, grouping in enumerate(major_groupings):
    if i == 0:
        continue
    for group in grouping:
        # find clusters
        clusters = [
            c 
            for g, c in cluster_definitions.items()
            if group.issuperset(g) 
        ]
        group_subelements = [
            g 
            for g, c in cluster_definitions.items()
            if group.issuperset(g) 
        ]
        if len(group_subelements) == 2:

            heights.append(group_distance(group_subelements[0], group_subelements[1]))

            cluster_definitions[group] = cluster_index_counter
            cluster_index_counter+=1

            merge_history.append(
                clusters
            )
"""

class Node(object):
    def __init__(self, row_num, fs_val, cluster_val=None):
        self.children = []
        self.row_num = row_num
        self.fs_val = fs_val
        self.cluster_val = cluster_val

    def set_parent(self, parent):
        self.parent = parent
        parent.children.append(self)
        self.child_ord = len(parent.children) - 1

    def find_parent(self):
        global cluster_idx

        if self.row_num == len(node_tree)-1:
            self.parent = None
            return None
        parent_row = node_tree[self.row_num + 1]
        for candidate in parent_row:
            if candidate.fs_val.issuperset(self.fs_val):
                self.set_parent(candidate)
                # make cluster join if two children exist for a given parent
                if len(self.parent.children) == 2:
                    self.parent.cluster_val = cluster_idx
                    cluster_idx += 1
                    merge_history.append([
                        self.parent.children[0].cluster_val, 
                        self.parent.children[1].cluster_val
                    ])
                    heights.append(
                        group_distance(
                            self.parent.children[0].fs_val,
                            self.parent.children[1].fs_val,
                        )+2*self.row_num
                    )
                return candidate
        print('Warning: should have found candidate by now!')
        return None
        
    def get_overall_ord(self):
        if self.parent is None:
            return 0
        overall_ord = 2**(self.row_num) * self.child_ord + self.parent.get_overall_ord()
        return overall_ord

# tree structure
cluster_idx = 1
node_tree = [
    [
        Node(row_num, val, -list(val)[0]-1) if row_num == 0
        else Node(row_num, val, None) 
        for val in row
    ] for row_num, row in enumerate(major_groupings)
]

for node_group in node_tree:
    for node in node_group:
        node.find_parent()
    # for nodes that do not have cluster assigned to them,
    # assign child node cluster to avoid issues
    for node in node_group:
        if node.parent is None:
            continue
        if len(node.parent.children) == 1:
            print('updating cluster val for node with one child')
            node.parent.cluster_val = node.cluster_val
    
orders = [node.get_overall_ord() + 1 for node in node_tree[0]]
# switch order to rank

print('orders:')
sorted_orders = sorted(orders)
orders = [sorted_orders.index(e)+1 for e in orders]
ranks = [orders.index(i)+1 for i in range(1, len(orders) + 1)]
print(ranks)



print('merge hist')
print(merge_history)
print('heights')
print(heights)

result_data = {
    'merge': merge_history,
    'order': ranks,
    'height': heights,
    'labels': names,
    'method': 'ward.D2',
    'dist.method': 'ward.D2',
    'call': '',
}

with open('result_data.json', 'w') as f:
    json.dump(result_data, f)

print(json.dumps(result_data, indent=2))
print(len(node_tree[0]))
