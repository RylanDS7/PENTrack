import sys
import ROOT
import matplotlib.pyplot as plt

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print("No file provided")

tfile = ROOT.TFile.Open(file)
endBranch = tfile.Get("neutronend")

# prob of spin up measurement from Szend
probUp = []

for entry in endBranch:
    probUp += [(endBranch.Szend + 1)/2]

plt.hist(probUp, bins=100)
plt.show()