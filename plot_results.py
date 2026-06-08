#!/usr/bin/env python3
"""Multi-UAV simulation result plotter.
Generates figures from CSV logs produced by diag_monitor.py.
"""
import os
import sys
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle
from matplotlib.ticker import MaxNLocator

OUT_DIR = os.path.expanduser("~/flights/figures")
os.makedirs(OUT_DIR, exist_ok=True)

FLIGHT_DIR = os.path.expanduser("~/flights")

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

def load(csv_path):
    df = pd.read_csv(csv_path)
    # Drop rows where t is NaN (session boundary artifacts)
    df = df.dropna(subset=["t"]).reset_index(drop=True)
    # Use row index as time in seconds (diag_monitor writes at ~1 Hz)
    df["t_s"] = df.index.astype(float)
    # Clip to valid flight (both drones armed, arm==2)
    arm_cols = [c for c in df.columns if c.endswith("_arm")]
    if arm_cols:
        armed = (df[arm_cols] == 2).all(axis=1)
        first_armed = armed.idxmax() if armed.any() else 0
        df = df.loc[first_armed:].copy().reset_index(drop=True)
        df["t_s"] = df.index.astype(float)
    return df

def drone_cols(df, field):
    """Return list of (drone_id, col_name) for a given field suffix."""
    cols = []
    for c in df.columns:
        if c.endswith(f"_{field}") and c.startswith("d"):
            did = c.split("_")[0]   # e.g. "d0"
            cols.append((did, c))
    return cols

def savefig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {path}")

# ──────────────────────────────────────────────────────────────────────────────
# Single-run detail figure
# ──────────────────────────────────────────────────────────────────────────────
def plot_single(df, title, fname_prefix):
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    t = df["t_s"].values

    # ── 1. XY Trajectory ──────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    for i, (did, _) in enumerate(drone_cols(df, "x")):
        xc = f"{did}_x"; yc = f"{did}_y"
        if xc in df.columns and yc in df.columns:
            ax1.plot(df[xc].values, df[yc].values, color=COLORS[i], lw=1.0, label=did)
            ax1.scatter(float(df[xc].iloc[0]), float(df[yc].iloc[0]), color=COLORS[i], marker="o", s=40, zorder=5)
            ax1.scatter(float(df[xc].iloc[-1]), float(df[yc].iloc[-1]), color=COLORS[i], marker="s", s=40, zorder=5)
    if "leader_x" in df.columns:
        ax1.plot(df["leader_x"].values, df["leader_y"].values, "k--", lw=0.8, alpha=0.6, label="leader")
    ax1.set_xlabel("X [m] (NED North)")
    ax1.set_ylabel("Y [m] (NED East)")
    ax1.set_title("XY Trajectory")
    ax1.legend(fontsize=7)
    ax1.set_aspect("equal", "datalim")
    ax1.grid(True, alpha=0.3)

    # ── 2. Altitude over time ─────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    for i, (did, _) in enumerate(drone_cols(df, "z")):
        zc = f"{did}_z"
        ax2.plot(t, (-df[zc]).values, color=COLORS[i], lw=1.0, label=did)  # NED→altitude
    ax2.axhline(5.0, color="k", ls="--", lw=0.8, alpha=0.5, label="target 5 m")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Altitude [m]")
    ax2.set_title("Altitude (NED z → +up)")
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)

    # ── 3. Formation error ────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    if "formation_max_err" in df.columns:
        ax3.plot(t, df["formation_max_err"].values, color="#d62728", lw=1.2)
        ax3.fill_between(t, 0, df["formation_max_err"].values, alpha=0.15, color="#d62728")
        mu = df["formation_max_err"].median()
        ax3.axhline(mu, color="#d62728", ls="--", lw=0.8, alpha=0.7, label=f"median {mu:.2f} m")
    ax3.set_xlabel("Time [s]")
    ax3.set_ylabel("Max formation error [m]")
    ax3.set_title("Formation Keeping Error")
    ax3.legend(fontsize=7)
    ax3.grid(True, alpha=0.3)

    # ── 4. Min inter-drone spacing ────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    if "min_spacing" in df.columns:
        ax4.plot(t, df["min_spacing"].values, color="#2ca02c", lw=1.2)
        ax4.axhline(1.2, color="red", ls="--", lw=0.9, alpha=0.8, label="d_safe=1.2 m")
        ax4.fill_between(t, 0, df["min_spacing"].values, alpha=0.1, color="#2ca02c")
    ax4.set_xlabel("Time [s]")
    ax4.set_ylabel("Min spacing [m]")
    ax4.set_title("Minimum Inter-drone Spacing")
    ax4.legend(fontsize=7)
    ax4.grid(True, alpha=0.3)

    # ── 5. Per-drone position error ───────────────────────────────────────────
    ax5 = fig.add_subplot(gs[2, 0])
    for i, (did, _) in enumerate(drone_cols(df, "poserr")):
        ec = f"{did}_poserr"
        if ec in df.columns:
            ax5.plot(t, df[ec].values, color=COLORS[i], lw=1.0, label=did)
    ax5.set_xlabel("Time [s]")
    ax5.set_ylabel("Position error [m]")
    ax5.set_title("Per-drone Position Error")
    ax5.legend(fontsize=7)
    ax5.grid(True, alpha=0.3)

    # ── 6. MPC solve time ─────────────────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 1])
    for i, (did, _) in enumerate(drone_cols(df, "solve_ms")):
        sc = f"{did}_solve_ms"
        if sc in df.columns:
            ax6.plot(t, df[sc].values, color=COLORS[i], lw=0.8, alpha=0.8, label=did)
    ax6.axhline(20, color="red", ls="--", lw=0.8, alpha=0.7, label="20 ms budget")
    ax6.set_xlabel("Time [s]")
    ax6.set_ylabel("Solve time [ms]")
    ax6.set_title("MPC Solver Time")
    ax6.legend(fontsize=7)
    ax6.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.01)
    savefig(fig, f"{fname_prefix}_detail.png")

# ──────────────────────────────────────────────────────────────────────────────
# Comparison figure across scenarios
# ──────────────────────────────────────────────────────────────────────────────
def plot_comparison(datasets, title, fname):
    """datasets: list of (label, df) tuples."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(title, fontsize=13, fontweight="bold")

    for i, (label, df) in enumerate(datasets):
        t = df["t_s"].values
        color = COLORS[i % len(COLORS)]

        # Formation error
        if "formation_max_err" in df.columns:
            axes[0].plot(t, df["formation_max_err"].values, color=color, lw=1.2,
                         label=label, alpha=0.85)
        # Min spacing
        if "min_spacing" in df.columns:
            axes[1].plot(t, df["min_spacing"].values, color=color, lw=1.2,
                         label=label, alpha=0.85)
        # Mean position error across drones
        poserr_cols = [f"{did}_poserr" for did, _ in drone_cols(df, "poserr")
                       if f"{did}_poserr" in df.columns]
        if poserr_cols:
            mean_err = df[poserr_cols].mean(axis=1)
            axes[2].plot(t, mean_err.values, color=color, lw=1.2, label=label, alpha=0.85)

    axes[0].set_title("Formation Max Error [m]")
    axes[0].set_xlabel("Time [s]"); axes[0].set_ylabel("Error [m]")
    axes[0].axhline(1.2, ls="--", color="gray", lw=0.7, alpha=0.6, label="d_safe")
    axes[0].legend(fontsize=7); axes[0].grid(True, alpha=0.3)

    axes[1].set_title("Min Inter-drone Spacing [m]")
    axes[1].set_xlabel("Time [s]"); axes[1].set_ylabel("Spacing [m]")
    axes[1].axhline(1.2, ls="--", color="red", lw=0.9, alpha=0.8, label="d_safe=1.2")
    axes[1].legend(fontsize=7); axes[1].grid(True, alpha=0.3)

    axes[2].set_title("Mean Position Error [m]")
    axes[2].set_xlabel("Time [s]"); axes[2].set_ylabel("Error [m]")
    axes[2].legend(fontsize=7); axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    savefig(fig, fname)

# ──────────────────────────────────────────────────────────────────────────────
# Summary statistics table figure
# ──────────────────────────────────────────────────────────────────────────────
def plot_summary_table(rows, title, fname):
    """rows: list of dicts with keys: Scenario, Formation_Err_med, Formation_Err_p95,
       Min_Spacing_min, MPC_Solve_p95, Safety_Violations, Duration_s"""
    if not rows:
        return
    df = pd.DataFrame(rows)
    col_labels = ["Scenario", "Form.Err\nmedian[m]", "Form.Err\np95[m]",
                  "MinSpacing\nmin[m]", "MPC Solve\np95[ms]", "Safety\nViol.", "Duration\n[s]"]
    cell_text = []
    for _, r in df.iterrows():
        cell_text.append([
            r.get("Scenario", ""),
            f"{r.get('Formation_Err_med', float('nan')):.3f}",
            f"{r.get('Formation_Err_p95', float('nan')):.3f}",
            f"{r.get('Min_Spacing_min', float('nan')):.3f}",
            f"{r.get('MPC_Solve_p95', float('nan')):.2f}",
            str(int(r.get("Safety_Violations", 0))),
            str(int(r.get("Duration_s", 0))),
        ])

    fig, ax = plt.subplots(figsize=(13, max(3, 0.5 * len(rows) + 2)))
    ax.axis("off")
    t = ax.table(cellText=cell_text, colLabels=col_labels,
                 cellLoc="center", loc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.6)
    # Color header
    for j in range(len(col_labels)):
        t[0, j].set_facecolor("#2c7bb6")
        t[0, j].set_text_props(color="white", fontweight="bold")
    # Alternate row shading
    for i in range(1, len(rows) + 1):
        bg = "#f0f4f8" if i % 2 == 0 else "white"
        for j in range(len(col_labels)):
            t[i, j].set_facecolor(bg)
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.97)
    savefig(fig, fname)

# ──────────────────────────────────────────────────────────────────────────────
# Stats extractor
# ──────────────────────────────────────────────────────────────────────────────
def extract_stats(label, df):
    stats = {"Scenario": label, "Duration_s": int(df["t_s"].iloc[-1])}
    if "formation_max_err" in df.columns:
        stats["Formation_Err_med"] = df["formation_max_err"].median()
        stats["Formation_Err_p95"] = df["formation_max_err"].quantile(0.95)
    else:
        stats["Formation_Err_med"] = float("nan")
        stats["Formation_Err_p95"] = float("nan")
    if "min_spacing" in df.columns:
        stats["Min_Spacing_min"] = df["min_spacing"].min()
    else:
        stats["Min_Spacing_min"] = float("nan")
    solve_cols = [f"{did}_solve_ms" for did, _ in drone_cols(df, "solve_ms")
                  if f"{did}_solve_ms" in df.columns]
    if solve_cols:
        stats["MPC_Solve_p95"] = df[solve_cols].max(axis=1).quantile(0.95)
    else:
        stats["MPC_Solve_p95"] = float("nan")
    # safety_violations 是单调递增的累计计数器(diag_monitor.py: self._safety_violations += 1)
    # 总违规数 = max(最后一行的值)，不是 sum()(后者把累计值逐行相加，虚高几百倍)
    stats["Safety_Violations"] = int(df["safety_violations"].max()) if "safety_violations" in df.columns else 0
    # 最大飞行半径(检测失控飞远)
    rmax = 0.0
    for i in range(9):
        cx, cy = f"d{i}_x", f"d{i}_y"
        if cx in df.columns and cy in df.columns:
            r = (df[cx].values ** 2 + df[cy].values ** 2) ** 0.5
            rmax = max(rmax, float(r.max()))
    stats["Max_Radius_m"] = rmax
    return stats

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
SCENARIOS = {
    # csv_glob_pattern: (label, fname_prefix, formation)
    "flight_pair2_line.csv":       ("pair2 line v0.5 (baseline)",   "pair2_line",     "pair2"),
    "flight_pair2_line_v2.0.csv":  ("pair2 line v2.0",              "pair2_line_v2",  "pair2"),
    "flight_pair2_perturbed.csv":  ("pair2 perturbed birth",        "pair2_perturbed","pair2"),
    "flight_pair2_hover_fix.csv":  ("pair2 hover (fixed)",          "pair2_hover",    "pair2"),
    "flight_trio3_circle.csv":        ("trio3 circle v1.5 wf0.5",    "trio3_circle",      "trio3"),
    "flight_trio3_circle_v2.0.csv":  ("trio3 circle v2.0 wf0.5",    "trio3_v2",          "trio3"),
    "flight_trio3_perturbed_fix3.csv":("trio3 perturbed (fixed)",    "trio3_perturbed",   "trio3"),
    "flight_trio3_circle_wf01.csv":   ("trio3 circle v1.5 wf0.1",   "trio3_circle_wf01",  "trio3"),
    "flight_trio3_circle_wf01_v2.csv":("trio3 circle v2.0 wf0.1",  "trio3_v2_wf01",      "trio3"),
    "flight_trio3_circle_wf005.csv":  ("trio3 circle v1.5 wf0.05", "trio3_circle_wf005", "trio3"),
    "flight_trio3_circle_wf005_v2.csv":("trio3 circle v2.0 wf0.05","trio3_v2_wf005",     "trio3"),
}

def main():
    loaded = {}
    for fname, (label, prefix, formation) in SCENARIOS.items():
        path = os.path.join(FLIGHT_DIR, fname)
        if os.path.exists(path):
            try:
                df = load(path)
                if len(df) < 10:
                    print(f"  SKIP {fname} (only {len(df)} rows after arm filter)")
                    continue
                loaded[fname] = (label, df, prefix, formation)
                print(f"  loaded {fname}: {len(df)} rows, {int(df['t_s'].iloc[-1])}s")
            except Exception as e:
                print(f"  ERROR loading {fname}: {e}")
        else:
            print(f"  MISSING {fname}")

    if not loaded:
        print("No CSV files found. Run simulations first.")
        return

    # Per-scenario detail figures
    print("\n=== Generating detail figures ===")
    for fname, (label, df, prefix, formation) in loaded.items():
        print(f"  {label}")
        plot_single(df, label, prefix)

    # pair2 comparison
    pair2 = [(label, df) for _, (label, df, _, f) in loaded.items() if f == "pair2" and len(df) > 50]
    if len(pair2) >= 2:
        print("\n=== Generating pair2 comparison ===")
        plot_comparison(pair2, "pair2 Scenario Comparison", "pair2_comparison.png")

    # trio3 comparison
    trio3 = [(label, df) for _, (label, df, _, f) in loaded.items() if f == "trio3" and len(df) > 50]
    if len(trio3) >= 2:
        print("\n=== Generating trio3 comparison ===")
        plot_comparison(trio3, "trio3 Scenario Comparison", "trio3_comparison.png")

    # All-scenario comparison
    all_data = [(label, df) for _, (label, df, _, _) in loaded.items() if len(df) > 50]
    if len(all_data) >= 2:
        print("\n=== Generating all-scenario comparison ===")
        plot_comparison(all_data, "All Scenarios — Formation Quality", "all_comparison.png")

    # Summary table
    print("\n=== Generating summary table ===")
    stats_rows = [extract_stats(label, df) for _, (label, df, _, _) in loaded.items() if len(df) > 50]
    plot_summary_table(stats_rows, "Simulation Results Summary", "summary_table.png")

    print(f"\nDone. Figures in {OUT_DIR}/")
    for f in sorted(os.listdir(OUT_DIR)):
        if f.endswith(".png"):
            print(f"  {f}")

if __name__ == "__main__":
    main()
