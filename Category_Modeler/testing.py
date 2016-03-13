from ete3 import Tree

rand_newick = "((((a,b), c), d), (e,f));"
rand_tree = "rand_tree"
with open(rand_tree, 'w') as TREE:
    TREE.write(rand_newick)

# Reading tree t1 and t2
t1 = Tree(rand_newick)   # @UndefinedVariable
t2 = Tree(rand_tree)         # @UndefinedVariable

print(t2)
t2.render("mytree.png")