"""
Plot the magnetic field B profile along the y-axis from a .out field map file.

Usage:
    python plot_B_profile.py <filename.out>

The script:
  - Filters rows where x == 0 and z == 0 (pure y-axis points)
  - Plots Bx, By, Bz, and |B| as a function of y
  - Falls back to all data sorted by y if no pure on-axis points are found
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# -- 1. Load file --------------------------------------------------------------
if len(sys.argv) < 2:
    print("Usage: python plot_B_profile.py <filename.out>")
    sys.exit(1)

filepath = sys.argv[1]

df = pd.read_csv(filepath, sep=r"\s+", comment="#")

# Normalise column names (strip whitespace, lower-case)
df.columns = [c.strip() for c in df.columns]
print(df)
required = {"x", "y", "z", "Bx", "By", "Bz"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing expected columns: {missing}\nFound: {list(df.columns)}")

# 2. Extract y-axis slice (x = -0.31, z = 0.337)
tol = 1e-3  # absolute tolerance for "on-axis"
x_target, z_target = -0.31, 0.337

on_axis = df[
    (np.abs(df["x"] - x_target) <= tol) &
    (np.abs(df["z"] - z_target) <= tol)
].copy()

if len(on_axis) < 2:
    print("Warning: fewer than 2 points with x=0, z=0 found. "
          "Plotting all data sorted by y instead.")
    on_axis = df.copy()

on_axis = on_axis.sort_values("y").reset_index(drop=True)

y  = on_axis["y"].values
Bx = on_axis["Bx"].values
By = on_axis["By"].values
Bz = on_axis["Bz"].values
dBxdy = on_axis["dBxdy"].values
dBydy = on_axis["dBydy"].values
dBzdy = on_axis["dBzdy"].values
B  = np.sqrt(Bx**2 + By**2 + Bz**2)

# -- 3. Plot -------------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

ax1, ax2 = axes

# --- Components ---
ax1.plot(y, Bx, label=r"$B_x$", color="#e05c5c", linewidth=1.8)
ax1.plot(y, By, label=r"$B_y$", color="#4a90d9", linewidth=1.8)
ax1.plot(y, Bz, label=r"$B_z$", color="#5cba6e", linewidth=1.8)
ax1.axhline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.4)
ax1.set_xlim((-3,-1))
ax1.set_ylabel("B components (T)", fontsize=12)
ax1.legend(fontsize=11, framealpha=0.9)
ax1.grid(True, linestyle=":", alpha=0.5)
ax1.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
ax1.set_title("Magnetic field profile along the y-axis", fontsize=13, fontweight="bold")

# --- Derivative ---
ax2.plot(y, dBxdy, label=r"$\frac{dB_x}{d_y}$", color="#e05c5c", linewidth=2)
ax2.plot(y, dBydy, label=r"$\frac{dB_y}{d_y}$", color="#4a90d9", linewidth=2)
ax2.plot(y, dBzdy, label=r"$\frac{dB_z}{d_y}$", color="#5cba6e", linewidth=2)
ax2.set_ylabel(r"$\frac{dB}{d_y}$ (T)", fontsize=12)
ax2.set_xlabel("y (m)", fontsize=12)
ax2.set_xlim((-3,-1))
ax2.legend(fontsize=11, framealpha=0.9)
ax2.grid(True, linestyle=":", alpha=0.5)
ax2.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax2.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

plt.tight_layout()

outfile = "B_profile_y.png"
plt.savefig(outfile, dpi=150, bbox_inches="tight")
print(f"Plot saved to: {outfile}")
plt.show()
