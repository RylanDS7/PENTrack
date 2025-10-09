import ROOT
import matplotlib.pyplot as plt

tree = ROOT.TFile.Open("000000000010.root")
branch = tree.Get("neutronend")

Sz = []

for entry in branch:
  Sz.append(entry.Szend)
  
plt.hist(Sz, bins=20)
plt.yscale("log")
plt.xlabel("Ending Sz")
plt.ylabel("Count")
plt.title("Ending Sz Components")

plt.show()

