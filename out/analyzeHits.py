import sys
import ROOT
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print("No file provided")
    sys.exit(1)

dfH = ROOT.RDataFrame("neutronhit", file)
dfS = ROOT.RDataFrame("neutronspin", file)

# Get all collision times per particle
dfHd = dfH.Filter("solid2==4")
dfHd_np = dfHd.AsNumpy(['particle', 't'])

# Build dict of particle -> sorted list of hit times
hit_times = {}
for particle, t in zip(dfHd_np['particle'], dfHd_np['t']):
    hit_times.setdefault(particle, []).append(t)
for particle in hit_times:
    hit_times[particle].sort()

def plot_Sz_after_nth_collision(n):
    """Plot Sz histogram for all particles after their nth collision (1-indexed)."""

    # Build map of particle -> nth hit time (if they have at least n collisions)
    nth_hit = {p: times[n-1] for p, times in hit_times.items() if len(times) >= n}

    if not nth_hit:
        print(f"No particles found with at least {n} collision(s).")
        return

    # Declare the map in C++ (redeclaring will error, so use a unique name per n)
    map_name = f"nth_hit_map_{n}"
    entries = ", ".join(f"{{{p}, {t}}}" for p, t in nth_hit.items())
    ROOT.gInterpreter.Declare(
        f"std::map<int, double> {map_name} = {{{entries}}};"
    )

    dfS_filtered = dfS.Filter(
        f"{map_name}.count(particle) > 0 && t == {map_name}.at(particle)"
    )

    dfS_filtered_np = dfS_filtered.AsNumpy(['Sz'])
    Sz_filtered = dfS_filtered_np['Sz']

    if len(Sz_filtered) == 0:
        print(f"No spin entries found after collision {n}.")
        return

    plt.figure(figsize=(10, 6))
    plt.hist(Sz_filtered, bins=100, color='steelblue', edgecolor='black', linewidth=0.5)
    plt.xlabel('Sz')
    plt.ylabel('Counts')
    plt.title(f'Neutron Sz at collision {n} (all particles)')
    plt.tight_layout()
    plt.show()

# Plot for whichever collisions you want
plot_Sz_after_nth_collision(1)
plot_Sz_after_nth_collision(2)
plot_Sz_after_nth_collision(3)