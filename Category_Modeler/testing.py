from ete3 import Tree, TreeStyle, TextFace  # @UndefinedVariable

rand_newick = "((water, estuarine_open_water, inland_water)Water_bodies, artificial_surface, cloud, shadow, forest, grassland)Root;"
rand_tree = "rand_tree"
with open(rand_tree, 'w') as TREE:
    TREE.write(rand_newick)

# Reading tree t1 and t2
t1 = Tree(rand_newick, format=8)   # @UndefinedVariable

#t2 = Tree(rand_tree)         # @UndefinedVariable
ts = TreeStyle()
ts.show_leaf_name = True
ts.branch_vertical_margin = 20
t1.add_face(TextFace("Root "), column=0, position = "branch-top")
for node in t1.traverse():
    if node.name == "Water_bodies":
        node.add_face(TextFace("Water_bodies"), column=0, position = "branch-top")
ts.title.add_face(TextFace("Auckland LCDB", fsize=20), column=0)
ts.scale = 50
print(t1)
t1.render("mytree.png", tree_style=ts, dpi=300)