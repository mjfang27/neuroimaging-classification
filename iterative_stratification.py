#Get the minimum label with at least 1 label, breaking ties randomly
def get_argmin_exclude_zero(num_pos_y_remaining):
    argmin = -1
    min_val = max(num_pos_y_remaining) + 1
    ties = []
    for i in range(len(num_pos_y_remaining)):
        if num_pos_y_remaining[i] <= min_val and num_pos_y_remaining[i] != 0:
            if num_pos_y_remaining[i] == min_val:
                ties.append(i)
            else:
                ties = []
                argmin = i
                min_val = num_pos_y_remaining[i]
    ties.append(argmin)
    return np.random.choice(ties)

#get subset with the largest number of desired examples for the label.
#If ties: consider the subset with the largest number of desired examples, picking randomly 
#if there are still ties. 
#c_l: number of desired examples of label l per fold
#c_j: number of desired examples per fold
#returns index of fold to use
def get_subset(c_l, c_j):
    #get max
    argmax = -1
    max_val = -1
    ties = []
    for i in range(len(c_l)):
        if c_l[i] == max_val:
            ties.append(i)
        elif c_l[i] > max_val:
            ties = []
            argmax = i
            max_val = c_l[i]
    ties.append(argmax)
    
    if len(ties) == 1:
        return ties[0]
    else:
        #go by c_j
        argmax = -1
        max_val = -1
        ties = []
        for i in range(len(c_j)):
            if c_j[i] == max_val:
                ties.append(i)
            elif c_j[i] > max_val:
                ties = []
                argmax = i
                max_val = c_j[i]
        ties.append(argmax)
        return np.random.choice(ties)

#X (actually not necessary, but included to match other similar functions...)
#y: labels for X
#k: the number of folds
# returns a list of the indices of k splits into train and test sets. 
def iterative_stratification(X, y, k):
#     np.random.seed(1)
    num_examples = y.shape[0]
    num_labels = y.shape[1]
    D = range(num_examples)
    r = 1/float(k)
    c_j = np.empty(k) 
    c_j.fill(len(D) * r) #the number of desired examples per fold. 
    D_i = np.sum(y, axis = 0)
    c_i_j = np.outer(np.ones(k) * r, D_i) #(k, num_labels)) #breakdown the number of desired examples by label
    
    S = []
    for i in range(k):
        S.append([])

    lmins = []
    while len(D) > 0:
        D_i = np.sum(y[D, :], axis = 0)
        l = get_argmin_exclude_zero(D_i)
        if l == -1: #no labels left? (possible if one ex gets no label?)
            print len(D) , " left, assigning randomly now"
            for elem in D:
                m = np.random.choice(range(k))
                S[m].append(elem)
            break
            
        lmins.append(l)
        removedIndices = set()
        for idx in D:
            if y[idx, l] == 1:
                m = get_subset(c_i_j[:, l], c_j)
                S[m].append(idx)
                removedIndices.add(idx)
                c_i_j[m, np.where(y[idx, :] == 1)] -= 1
                c_j[m] -= 1
        for item in list(D):
            if item in removedIndices:
                D.remove(item)        
    print lmins
    print "labels taken into account: ", len(lmins)

    train_test_splits = []
    for i in range(k):
        train = []
        for j in range(k):
            if j != i:
                train.extend(S[j])
        train_test_splits.append((train, S[i]))
    return train_test_splits