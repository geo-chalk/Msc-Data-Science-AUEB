"""
Code used to generate huge_graph.txt
"""
import snap

f = open("huge_graph.txt", "w")
UGraph1 = snap.GenRndGnm(snap.TUNGraph, 100, 350)
for NI in UGraph1.Nodes():
    f.write(str(NI.GetId()))
    f.write(" ")
    out = NI.GetOutDeg()
    for i in range(out):
        f.write(str(NI.GetNbrNId(i)))
        f.write(" ")
    f.write("\n")


"""
Code used to generate huge_graph.gdf
"""
f = open("huge_graph.gdf", "w")
f.write("nodedef>name VARCHAR, community INT\n")

with open("part-m-00000.txt", "r") as fr:
    for line in fr.readlines():
        f.write(",".join(line.split()))
        f.write("\n")

f.write("edgedef>node1 VARCHAR,node2 VARCHAR\n")
with open("huge_graph.txt", "r") as fr:
    for line in fr.readlines():
        root = line.split()[0]
        for node in line.split()[1:]:
            f.write(f"{root},{node}")
            f.write("\n")
