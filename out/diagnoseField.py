import sys
import ROOT
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print("No file provided")
    sys.exit(1)

# 1. Open RDataFrame (Lazy loading - consumes 0 MB of RAM right now)
df = ROOT.RDataFrame("neutronspin", file)

# 2. Extract ONLY the particle column to find unique types
# This uses a fraction of the memory compared to loading all columns
print("Finding unique particle types...")
particle_dict = df.AsNumpy(columns=["particle"])
particles = np.unique(particle_dict["particle"])
del particle_dict  # Free up memory immediately

data_list = []

# 3. Process data chunk-by-chunk (One particle type at a time)
for p in particles:
    if p == 21:
        break
    
    print(f"Processing particle: {p}...")
    
    # Build the C++ string filter dynamically based on data type
    if isinstance(p, (str, bytes)):
        p_str = p.decode('utf-8') if isinstance(p, bytes) else p
        df_p = df.Filter(f'particle == "{p_str}"')
    else:
        df_p = df.Filter(f'particle == {p}')
    
    # Pull ONLY the columns for this specific particle into RAM
    p_dict = df_p.AsNumpy(columns=["t", "Sz", "y"])
    
    times = p_dict["t"]
    if len(times) < 3:
        continue  # Skip if not enough points for central difference
        
    # Sort chronologically using fast NumPy indexing
    sort_idx = np.argsort(times)
    times = times[sort_idx]
    Sz = p_dict["Sz"][sort_idx]
    y_vals = p_dict["y"][sort_idx]
    
    # 4. Vectorized Central Differences (Instantaneous calculation)
    dt = times[2:] - times[:-2]
    dSz = Sz[2:] - Sz[:-2]
    
    # Prevent division by zero
    valid = dt != 0
    dSzdt = np.divide(dSz, dt, out=np.zeros_like(dSz), where=valid)
    y_center = y_vals[1:-1][valid]
    dSzdt = dSzdt[valid]
    
    # Printing millions of rows inside a loop will freeze your terminal.
    # Un-comment the next 2 lines ONLY if you have a small dataset:
    # for y, deriv in zip(y_center, dSzdt):
    #     print(f"{y}: {deriv}")
        
    if len(y_center) > 0:
        data_list.append(np.column_stack((y_center, dSzdt)))

# 5. Plot the final aggregated dataset
if data_list:
    print("Generating plot...")
    data = np.vstack(data_list)
    
    plt.figure(figsize=(8, 6))
    # 's=1' and 'alpha=0.1' keep the plot legible even with millions of points
    plt.scatter(data[:, 0], data[:, 1], alpha=0.1, s=1, color='blue')
    plt.xlabel('y')
    plt.ylabel('dSz / dt')
    plt.title('Spin Depolarization vs Axial Distance')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('depolarizationLocations.png')
    plt.show()
else:
    print("No data points were calculated.")
