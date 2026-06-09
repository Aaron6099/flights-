#!/usr/bin/env python3
"""专用：trio3 circle w_formation 三轮对比图"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FLIGHTS = os.path.expanduser("~/flights")
OUT = os.path.expanduser("~/flights/figures")
os.makedirs(OUT, exist_ok=True)

DATASETS = [
    # (label, csv, color, linestyle)
    ("wf=0.50 v1.5", "flight_trio3_circle.csv",        "#d62728", "-"),
    ("wf=0.10 v1.5", "flight_trio3_circle_wf01.csv",   "#ff7f0e", "-"),
    ("wf=0.05 v1.5", "flight_trio3_circle_wf005.csv",  "#2ca02c", "-"),
    ("wf=0.50 v2.0", "flight_trio3_circle_v2.0.csv",   "#d62728", "--"),
    ("wf=0.10 v2.0", "flight_trio3_circle_wf01_v2.csv","#ff7f0e", "--"),
    ("wf=0.05 v2.0", "flight_trio3_circle_wf005_v2.csv","#2ca02c","--"),
]

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("trio3 Circle — w_formation Parameter Sweep", fontsize=14, fontweight="bold")

for label, fname, color, ls in DATASETS:
    path = os.path.join(FLIGHTS, fname)
    if not os.path.exists(path):
        print(f"  SKIP {fname}")
        continue
    df = pd.read_csv(path).dropna(subset=["t"])
    df = df.reset_index(drop=True)
    df["t_s"] = df.index.astype(float)
    # 仅取有效行
    arm_cols = [c for c in df.columns if c.endswith("_arm")]
    armed = (df[arm_cols] == 2).all(axis=1)
    if armed.any():
        df = df.loc[armed.idxmax():].reset_index(drop=True)
        df["t_s"] = df.index.astype(float)
    t = df["t_s"].values

    # Formation error
    if "formation_max_err" in df.columns and df["formation_max_err"].notna().sum() > 10:
        axes[0].plot(t, df["formation_max_err"].values, color=color, ls=ls, lw=1.3,
                     label=label, alpha=0.85)

    # Min spacing
    if "min_spacing" in df.columns:
        axes[1].plot(t, df["min_spacing"].values, color=color, ls=ls, lw=1.3,
                     label=label, alpha=0.85)

    # 累计安全违规
    if "safety_violations" in df.columns:
        axes[2].plot(t, df["safety_violations"].values, color=color, ls=ls, lw=1.3,
                     label=label, alpha=0.85)

axes[0].set_title("Formation Max Error [m]")
axes[0].set_xlabel("Time [s]"); axes[0].set_ylabel("Error [m]")
axes[0].legend(fontsize=7); axes[0].grid(True, alpha=0.3)
# 截顶 y 轴：wf0.1 v1.5 失稳会冲到 100m+，撑爆坐标轴使其余曲线不可读。
# 截到 35m 让稳定/边界区清晰，超出部分在标题注明。
_FERR_CAP = 35.0
axes[0].set_ylim(0, _FERR_CAP)
axes[0].annotate("wf0.1 v1.5 unstable peak off-chart (>100 m)",
                 xy=(0.02, 0.95), xycoords="axes fraction",
                 fontsize=7, color="#ff7f0e", va="top")

axes[1].set_title("Min Inter-drone Spacing [m]")
axes[1].set_xlabel("Time [s]"); axes[1].set_ylabel("Spacing [m]")
axes[1].axhline(1.5, color="red", ls=":", lw=1.0, label="d_safe=1.5")
axes[1].legend(fontsize=7); axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(bottom=0)

axes[2].set_title("Cumulative Safety Violations")
axes[2].set_xlabel("Time [s]"); axes[2].set_ylabel("Violations")
axes[2].legend(fontsize=7); axes[2].grid(True, alpha=0.3)

plt.tight_layout()
out = os.path.join(OUT, "trio3_wf_sweep.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"saved → {out}")

# ── 汇总 bar chart ───────────────────────────────────────────────────────────
stats = []
for label, fname, color, ls in DATASETS:
    path = os.path.join(FLIGHTS, fname)
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path).dropna(subset=["t"]).reset_index(drop=True)
    ferr = df["formation_max_err"].dropna()
    stats.append({
        "label": label,
        "ferr_med": ferr.median() if len(ferr) > 0 else float("nan"),
        "ferr_p95": ferr.quantile(0.95) if len(ferr) > 0 else float("nan"),
        "minsp": df["min_spacing"].min(),
        "viol": int(df["safety_violations"].max()),  # 累计计数器取max，非sum
        "color": color,
        "ls": ls,
    })

fig2, axes2 = plt.subplots(1, 3, figsize=(14, 4))
fig2.suptitle("trio3 Circle — w_formation Sweep Summary", fontsize=13, fontweight="bold")

labels = [s["label"] for s in stats]
x = np.arange(len(labels))
w = 0.6

axes2[0].bar(x, [s["ferr_med"] for s in stats], width=w,
             color=[s["color"] for s in stats], alpha=0.8)
axes2[0].set_title("Formation Error Median [m]")
axes2[0].set_xticks(x); axes2[0].set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
axes2[0].set_ylabel("Error [m]"); axes2[0].grid(True, axis="y", alpha=0.3)

axes2[1].bar(x, [s["minsp"] for s in stats], width=w,
             color=[s["color"] for s in stats], alpha=0.8)
axes2[1].axhline(1.5, color="red", ls="--", lw=1.0, label="d_safe")
axes2[1].set_title("Min Spacing [m]")
axes2[1].set_xticks(x); axes2[1].set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
axes2[1].set_ylabel("Spacing [m]"); axes2[1].legend(fontsize=8); axes2[1].grid(True, axis="y", alpha=0.3)

axes2[2].bar(x, [s["viol"] for s in stats], width=w,
             color=[s["color"] for s in stats], alpha=0.8)
axes2[2].set_title("Total Safety Violations")
axes2[2].set_xticks(x); axes2[2].set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
axes2[2].set_ylabel("Count"); axes2[2].grid(True, axis="y", alpha=0.3)

plt.tight_layout()
out2 = os.path.join(OUT, "trio3_wf_sweep_bar.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig2)
print(f"saved → {out2}")
