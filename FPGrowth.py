from itertools import chain, combinations #used to get powersets

class node:
    def __init__(self, id, sup=0, parent=None):
        self.id = id
        self.sup = sup
        self.parent = parent
        self.children = []

    def show(self, depth):
        print('id: ' + str(self.id) + ', support: ' + str(self.sup) + ', depth: ' + str(depth))
        for c in self.children:
            c.show(depth + 1)

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def powersetNonInclusive(iterable): #dont include the full set
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

def getCounts(trans, minSup): #generate the counts of each item from the transaction data
    counts = {}
    for i in trans:
        for j in trans[i]:
            if j in counts:
                counts[j] = counts[j] + 1
            else:
                counts[j] = 1
    delete = []
    for i in counts:
        if counts[i]<minSup:
            delete.append(i)
    for d in delete:
        counts.pop(d)
    sortedCounts = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return sortedCounts

def getOrderedTransactions(trans, counts): #generate the ordered transaction data from the counts of each item
    orderedTrans = {}
    for tid in trans:
        orderedTrans[tid] = []
        for c in counts:
            if c[0] in trans[tid]:
                orderedTrans[tid].append(c[0])
    return orderedTrans

def contains(node, item): #finds if a tree contains an item with a certain id and returns the node too
    answer = False
    obj = None
    for c in node.children:
        if c.id == item:
            answer = True
            obj = c
            break
    return answer, obj

def constructFPTree(trans): #create an FP tree from the ordered transaction data
    tree = node(-1)
    for tid in trans:
        curBranch = tree
        for item in trans[tid]:
            cont, foundChild = contains(curBranch, item)
            if cont:
                curBranch = foundChild
                curBranch.sup = curBranch.sup + 1
            else:
                child = node(item, 1, curBranch)
                curBranch.children.append(child)
                curBranch = child
    return tree

def findNodes(tree, id): #find all nodes in the tree with the given id
    Nodes = []
    if tree.id == id:
        Nodes = [tree]
    else:
        for c in tree.children:
            Nodes = Nodes + findNodes(c, id)
    return Nodes

def contructPatternBases(tree, counts): #given the FP tree find the conditional pattern bases for each item
    revCounts = reversed(counts)
    basesTable = {}
    for tup in revCounts:
        nodes = findNodes(tree, tup[0])
        bases = []
        for n in nodes:
            curNode = n
            base = []
            while True:
                if curNode.parent.id == -1:
                    break
                else:
                    base.append(curNode.parent.id)
                    curNode = curNode.parent
            if len(base) > 0:
                revBase = base[::-1]
                bases.append((revBase, n.sup))
        basesTable[tup[0]] = bases
    return basesTable

def cleanFPTree(tree, minSup): #remove nodes from the tree with less than the minimum support
    rem = []
    for c in tree.children:
        if c.sup < minSup:
            rem.append(c)
    for r in rem:
        tree.children.remove(r)
    for c in tree.children:
        cleanFPTree(c, minSup)
    x=1

def constructConditionalFPTrees(condBases, minSup): #construct the conditional FP trees from the pattern bases
    trees = {}
    for item in condBases:
        bases = condBases[item]
        trans = {}
        count = 1
        for b in bases:
            for i in range(b[1]):
                trans[count] = b[0]
                count = count + 1
        counts = getCounts(trans, minSup)
        orderedTrans = getOrderedTransactions(trans, counts)
        fpTree = constructFPTree(orderedTrans)
        cleanFPTree(fpTree,minSup)
        trees[item] = fpTree
    return trees

def findLeaves(tree): #find all the leaves in a tree
    leaves = []
    for c in tree.children:
        if len(c.children) == 0:
            leaves = leaves + [c]
        else:
            leaves = leaves + findLeaves(c)
    return leaves

def findParents(tree): #find a list of the parents of a node
    parents = []
    curNode = tree
    while True:
        if curNode.parent.id == -1:
            break
        else:
            parents.append(curNode.parent.id)
            curNode = curNode.parent
    return parents[::-1]

def generatePatterns(trees): #generate the frequent patterns from the conditional FP trees
    patterns = {}
    for item in trees:
        condTree = trees[item]
        leaves = findLeaves(condTree)
        for l in leaves:
            parents = findParents(l)
            parents.append(l.id)
            bases = tuple(powerset(parents))
            print(bases)
            for b in bases:
                tempList = list(b)
                tempList.append(item)
                b = tuple(tempList)
                tup = tuple(sorted(b))
                if b in patterns:
                    patterns[tup] = patterns[tup] + l.sup
                else:
                    patterns[tup] = l.sup
    return patterns

def findAssociationRules(patterns, minCon): #find the assosiation rules from the list of frequent patterns
    print('Rules:')
    associationRules = []
    for p in patterns:
        if len(p) > 1:
            rules = powersetNonInclusive(p)
            for r in rules:
                if patterns[p]/patterns[r] > minCon:
                    aRule = (list(r), list(set(p) ^ set(r)))
                    associationRules.append(aRule)
                    print(str(list(r)) + " => " + str(list(set(p) ^ set(r))))
    return associationRules



def FPGrowth(trans,minSup,minCon): #run steps of the algorithm
    print(trans)
    counts = getCounts(trans, minSup)
    print(counts)
    orderedTrans = getOrderedTransactions(trans, counts)
    print(orderedTrans)
    fpTree = constructFPTree(orderedTrans)

    condBases = contructPatternBases(fpTree, counts)
    print(condBases)

    num = 4
    condTrees = constructConditionalFPTrees(condBases, minSup)
    condTrees[num].show(0)
    patterns = generatePatterns(condTrees)
    for c in counts:
        t = (c[0],)
        patterns[t] = c[1]
    print(patterns)
    rules = findAssociationRules(patterns, minCon)

# input transaction data as dictionary with items converted to integer ID's
trans = {
    1:[1,2],
    2:[1,3,4,5],
    3:[2,3,4,6],
    4:[1,2,3,4],
    5:[1,2,3,6]
}
# input minimum support (in number of items rather than fraction)
minSup = 2
# input minimum confidence
minCon = 0.6
FPGrowth(trans, minSup, minCon)