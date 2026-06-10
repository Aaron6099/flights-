# flights-

PX4 多机编队仿真实验数据仓库。存放 `diag_monitor.py --log` 生成的飞行日志 CSV、分析脚本和输出图表。

主仿真代码见 [Multi-UAV-simulation](https://github.com/Aaron6099/Multi-UAV-simulation)。

---

## 目录结构

```
flights-/
├── flight_*.csv          # 飞行日志（diag_monitor.py 每秒一行）
├── plot_results.py       # 多场景对比图 + 汇总表
├── plot_wf_comparison.py # trio3 编队权重扫描对比图
├── run_plan_6csv.md      # 6-CSV 最小测试矩阵执行计划
├── figures/              # 输出图片
└── archive_failed/       # 失败/废弃跑的原始数据存档
```

---

## CSV 文件说明

| 文件 | 配置 | 场景 |
|------|------|------|
| `flight_pair2_hover.csv` | pair2 | 悬停 |
| `flight_pair2_hover_fix.csv` | pair2 | 悬停（修复后） |
| `flight_pair2_line.csv` | pair2 | 直线 v0.5 |
| `flight_pair2_line_v2.0.csv` | pair2 | 直线 v2.0 |
| `flight_pair2_perturbed.csv` | pair2 | 扰动出生 |
| `flight_trio3_circle.csv` | trio3 | 圆周 v1.5 wf=0.5 |
| `flight_trio3_circle_v2.0.csv` | trio3 | 圆周 v2.0 wf=0.5 |
| `flight_trio3_circle_wf01.csv` | trio3 | 圆周 v1.5 wf=0.1 |
| `flight_trio3_circle_wf01_v2.csv` | trio3 | 圆周 v2.0 wf=0.1 |
| `flight_trio3_circle_wf005.csv` | trio3 | 圆周 v1.5 wf=0.05 |
| `flight_trio3_circle_wf005_v2.csv` | trio3 | 圆周 v2.0 wf=0.05 |
| `flight_trio3_perturbed.csv` | trio3 | 扰动出生 |
| `flight_trio3_perturbed_fix2.csv` | trio3 | 扰动出生 fix2 |
| `flight_trio3_perturbed_fix3.csv` | trio3 | 扰动出生 fix3 |

**列格式**（每行 ≈ 1 秒）：
`t, d0_x, d0_y, d0_z, d0_arm, d0_poserr, d0_solve_ms, ..., formation_max_err, min_spacing, safety_violations, leader_x, leader_y, leader_vx, leader_vy`

---

## 分析脚本使用

> 脚本默认读 `~/flights/`，输出图到 `~/flights/figures/`。
> 在 Ubuntu 上把本 repo clone 到 `~/flights/` 即可直接使用。

```bash
# 克隆到正确路径（首次）
git clone https://github.com/Aaron6099/flights- ~/flights

# 生成所有场景详图 + 对比图 + 汇总表
python3 ~/flights/plot_results.py

# 生成 trio3 编队权重扫描对比图
python3 ~/flights/plot_wf_comparison.py
```

输出图保存在 `~/flights/figures/`。

---

## 数据来源

仿真运行命令见主仓库 `report/RUN_PLAN_仿真运行清单.md`。
每次跑完用 `diag_monitor.py --log` 记录，日志自动写入 `~/flights/`，跑完后 `git add *.csv && git commit && git push` 同步到本仓库。
