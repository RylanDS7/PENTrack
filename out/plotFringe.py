import sys
import ROOT
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print("No file provided")
    sys.exit(1)

# 1. Open RDataFrame (Lazy loading)
df = ROOT.RDataFrame("neutronspin", file)

# 2. Extract ONLY the particle column to find unique types
print("Finding unique particle types...")
particle_dict = df.AsNumpy(columns=["particle"])
particles = np.unique(particle_dict["particle"])
del particle_dict

data_list = []

# 3. Process data particle-by-particle
for p in particles:
    if p == 21:
        break

    print(f"Processing particle: {p}...")

    # Build the C++ filter dynamically based on data type
    if isinstance(p, (str, bytes)):
        p_str = p.decode("utf-8") if isinstance(p, bytes) else p
        df_p = df.Filter(f'particle == "{p_str}"')
    else:
        df_p = df.Filter(f"particle == {p}")

    # Pull only the columns needed for this particle
    p_dict = df_p.AsNumpy(columns=["t", "Sz", "x", "z"])

    times = p_dict["t"]

    if len(times) < 3:
        continue

    # Sort chronologically
    sort_idx = np.argsort(times)

    times = times[sort_idx]
    Sz = p_dict["Sz"][sort_idx]
    x_vals = p_dict["x"][sort_idx]
    z_vals = p_dict["z"][sort_idx]

    # ---------------------------------------------------------
    # Calculate dSz/dt using a central difference
    #
    # dSz/dt ≈ [Sz(t+1) - Sz(t-1)] / [t(t+1) - t(t-1)]
    # ---------------------------------------------------------
    dt = times[2:] - times[:-2]
    dSz = Sz[2:] - Sz[:-2]

    # Prevent division by zero
    valid = dt != 0

    dSzdt = np.divide(
        dSz,
        dt,
        out=np.zeros_like(dSz),
        where=valid
    )

    # ---------------------------------------------------------
    # Calculate radial distance in the x-z plane
    # relative to the specified center
    # ---------------------------------------------------------
    x_center = -0.31
    z_center = 0.337

    r_xz = np.sqrt(
        (x_vals[1:-1] - x_center)**2 +
        (z_vals[1:-1] - z_center)**2
    )

    # Apply validity mask
    r_xz = r_xz[valid]
    dSzdt = dSzdt[valid]

    if len(r_xz) > 0:
        data_list.append(
            np.column_stack((r_xz, dSzdt))
        )

# 4. Plot the final aggregated dataset
if data_list:
    print("Generating plot...")

    data = np.vstack(data_list)

    plt.figure(figsize=(8, 6))

    plt.scatter(
        data[:, 0],
        data[:, 1],
        alpha=0.1,
        s=1,
        color="blue"
    )

    plt.xlabel(
        r"$\sqrt{(x)^2 + (z)^2}$"
    )
    plt.ylabel(r"$dS_z / dt$")
    plt.title(
        r"Spin Depolarization vs Radial Distance"
    )

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.savefig(
        "depolarizationFringe.png",
        dpi=300
    )

    plt.show()

else:
    print("No data points were calculated.")
