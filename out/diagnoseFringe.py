import sys
import ROOT
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) == 2:
    file = sys.argv[1]
else:
    print("No file provided")
    sys.exit(1)

# 1. Open RDataFrame
df = ROOT.RDataFrame("neutronspin", file)

# 2. Extract particle types
print("Finding unique particle types...")
particle_dict = df.AsNumpy(columns=["particle"])
particles = np.unique(particle_dict["particle"])
del particle_dict

data_list = []

# Circle center and radius
x_center = -0.31
z_center = 0.337
radius = 0.05

# Threshold for dSz/dt
threshold = 100

# 3. Process data particle-by-particle
for p in particles:
    if p == 21:
        break

    print(f"Processing particle: {p}...")

    # Build the C++ filter dynamically
    if isinstance(p, (str, bytes)):
        p_str = p.decode("utf-8") if isinstance(p, bytes) else p
        df_p = df.Filter(f'particle == "{p_str}"')
    else:
        df_p = df.Filter(f"particle == {p}")

    # Pull only required columns
    p_dict = df_p.AsNumpy(
        columns=["t", "Sz", "x", "z"]
    )

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

    # Corresponding spatial locations are the central points
    x_centered = x_vals[1:-1]
    z_centered = z_vals[1:-1]

    # Apply validity mask
    x_centered = x_centered[valid]
    z_centered = z_centered[valid]
    dSzdt = dSzdt[valid]

    # ---------------------------------------------------------
    # Select locations where dSz/dt exceeds 100
    # ---------------------------------------------------------
    threshold_mask = dSzdt > threshold

    x_threshold = x_centered[threshold_mask]
    z_threshold = z_centered[threshold_mask]

    if len(x_threshold) > 0:
        data_list.append(
            np.column_stack((x_threshold, z_threshold))
        )

# 4. Plot the selected (x,z) locations
if data_list:
    print("Generating plot...")

    data = np.vstack(data_list)

    x_plot = data[:, 0]
    z_plot = data[:, 1]

    plt.figure(figsize=(8, 8))

    # Scatter points where dSz/dt > 100
    plt.scatter(
        x_plot,
        z_plot,
        s=2,
        alpha=0.5,
        color="blue",
        label=r"$dS_z/dt > 100$"
    )

    # ---------------------------------------------------------
    # Overlay circle
    # ---------------------------------------------------------
    circle = plt.Circle(
        (x_center, z_center),
        radius,
        fill=False,
        color="red",
        linewidth=2,
        label=r"$r=0.05$"
    )

    plt.gca().add_patch(circle)

    # Mark circle center
    plt.scatter(
        x_center,
        z_center,
        color="red",
        marker="+",
        s=100,
        linewidths=2
    )

    plt.xlabel("x")
    plt.ylabel("z")
    plt.title(r"Locations where $dS_z/dt > 100$")

    plt.axis("equal")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        "fringeLocations.png",
        dpi=300
    )

    plt.show()

else:
    print("No locations found where dSz/dt exceeds 100.")
