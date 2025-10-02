import ROOT
import re
import sys
import numpy

def ReadOutFile(fn):
    with open(fn, "r") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"{fn} is empty")

    # First line = column names (replace spaces with colons for ROOT TNtuple)
    descriptor = lines[0].strip().replace(" ", ":")
    data = []

    for line in lines[1:]:
        vals = line.strip().split()
        if not vals:
            continue
        try:
            floats = [float(v) for v in vals]
        except ValueError:
            print(f"Skipping non-numeric line: {line}")
            continue

        if len(floats) == len(descriptor.split(":")):
            data.append(floats)
        else:
            print(f"Line has {len(floats)} values, expected {len(descriptor.split(':'))}: {line}")

    return descriptor, data


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_out.py <file.out>")
        sys.exit(1)

    fn = sys.argv[1]
    print(f"Reading {fn}")

    descriptor, data = ReadOutFile(fn)

    # Open ROOT file
    out = ROOT.TFile("out.root", "RECREATE")
    treename = re.sub(r"\.out$", "", fn)  # e.g. "BFCut"
    tree = ROOT.TNtupleD(treename, treename, descriptor)

    # Fill tree
    for row in data:
        tree.Fill(numpy.array(row, dtype=numpy.float64))

    print(f"{treename} has {tree.GetEntries()} entries, {len(descriptor.split(':'))} columns")

    # Save
    out.Write()
    out.Close()


if __name__ == "__main__":
    main()
