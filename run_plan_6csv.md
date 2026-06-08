# 6-CSV 最小测试矩阵执行计划

## 测试清单（共6条）

| # | 机型 | 测试项 | scenario | 额外参数 | CSV文件 | 时长 |
|---|------|--------|----------|----------|---------|------|
| 1 | 双机 | 基线 line v=0.5 | S2_pair2_line | - | flight_pair2_line.csv | ≥120s |
| 2 | 双机 | 速度2.0 | S2_pair2_line | leader_speed:=2.0 | flight_pair2_line_v2.0.csv | ≥120s |
| 3 | 双机 | 出生扰动 | S17_pair2_perturbed | - | flight_pair2_perturbed.csv | ≥120s |
| 4 | 三机 | 基线 circle v=1.5 R=10 | S3_trio3_circle | - | flight_trio3_circle.csv | ≥1-2圈 |
| 5 | 三机 | 速度2.0 | S3_trio3_circle | leader_speed:=2.0 | flight_trio3_circle_v2.0.csv | ≥1-2圈 |
| 6 | 三机 | 出生扰动 | S19_trio3_perturbed | - | flight_trio3_perturbed.csv | ≥1-2圈 |

## 通用规矩

1. **每次测试前完全重启**（否则 world_birth 漂移）
2. **清理命令**: `pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2`
3. **检查清理干净**: `ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep`
4. **CSV输出位置**: `~/flights/*.csv`
5. **完成后拷贝到 Windows**: `report/data/`

## 执行流程（每条测试）

```
终端1: gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
终端2: START_DELAY=5 bash ~/ros2_control_mpc_ws/src/mpc_control/start_N_px4.sh
终端3: MicroXRCEAgent udp4 -p 8888
终端4: cd ~/ros2_control_mpc_ws && source install/setup.bash && ros2 launch mpc_control swarm_launch.py ...
终端5: 可选 - 诊断监控
```

---

## 测试 1: 双机基线 line v=0.5

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 双机
```bash
START_DELAY=5 bash ~/ros2_control_mpc_ws/src/mpc_control/start_2_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S2_pair2_line
```

### 等待运行 ≥120s 后 Ctrl+C 停止

---

## 测试 2: 双机速度2.0

### 清理
```bash
pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2
ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep  # 确认干净
```

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 双机
```bash
START_DELAY=5 bash ~/ros2_control_mpc_ws/src/mpc_control/start_2_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S2_pair2_line leader_speed:=2.0
```

### 等待运行 ≥120s 后 Ctrl+C 停止

---

## 测试 3: 双机出生扰动

### 清理
```bash
pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2
ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep
```

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 双机（扰动出生点）
```bash
SCENARIO=S17_pair2_perturbed bash ~/ros2_control_mpc_ws/src/mpc_control/start_2_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S17_pair2_perturbed
```

### 等待运行 ≥120s 后 Ctrl+C 停止

---

## 测试 4: 三机基线 circle v=1.5 R=10

### 清理
```bash
pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2
ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep
```

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 三机
```bash
START_DELAY=5 bash ~/ros2_control_mpc_ws/src/mpc_control/start_3_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S3_trio3_circle
```

### 等待运行 ≥1-2 圈后 Ctrl+C 停止（约 40-80s，取决于圆周速度）

---

## 测试 5: 三机速度2.0

### 清理
```bash
pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2
ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep
```

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 三机
```bash
START_DELAY=5 bash ~/ros2_control_mpc_ws/src/mpc_control/start_3_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S3_trio3_circle leader_speed:=2.0
```

### 等待运行 ≥1-2 圈后 Ctrl+C 停止

---

## 测试 6: 三机出生扰动

### 清理
```bash
pkill -f px4; pkill -f gz; pkill -f MicroXRCEAgent; pkill -f ros2
ps aux | grep -E "px4|gz|MicroXRCE|ros2" | grep -v grep
```

### 终端1 - Gazebo
```bash
gz sim -r ~/PX4-Autopilot-1.14/Tools/simulation/gz/worlds/default.sdf
```

### 终端2 - PX4 三机（扰动出生点）
```bash
SCENARIO=S19_trio3_perturbed bash ~/ros2_control_mpc_ws/src/mpc_control/start_3_px4.sh
```

### 终端3 - MicroXRCEAgent
```bash
MicroXRCEAgent udp4 -p 8888
```

### 终端4 - Launch
```bash
cd ~/ros2_control_mpc_ws && source install/setup.bash
ros2 launch mpc_control swarm_launch.py scenario:=S19_trio3_perturbed
```

### 等待运行 ≥1-2 圈后 Ctrl+C 停止

---

## 完成后

### 检查 CSV 文件
```bash
ls -lh ~/flights/flight_pair2_*.csv ~/flights/flight_trio3_*.csv
```

### 拷贝到 Windows report/data/
```bash
# 在 Windows 终端或文件管理器中复制以下文件：
# ~/flights/flight_pair2_line.csv
# ~/flights/flight_pair2_line_v2.0.csv
# ~/flights/flight_pair2_perturbed.csv
# ~/flights/flight_trio3_circle.csv
# ~/flights/flight_trio3_circle_v2.0.csv
# ~/flights/flight_trio3_perturbed.csv
```
