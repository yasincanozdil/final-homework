# 🤖 KTÜN Robotiğe Giriş — Final Ödevi
## Servis Robotu / Çoklu Görev QR Doğrulama

**Platform:** ROS1 Noetic + TurtleBot3 + Gazebo  
**Ortam:** AWS RoboMaker Bookstore World

---

## 🎥 Demo Videoları

- **SLAM Haritalama:** `slam_demo.mkv` (repo içinde)
- **Navigasyon + QR Doğrulama:** `demo_video.mkv` (repo içinde)

---

## 📁 Proje Yapısı
---

## ⚙️ Kurulum

### 1. Gereksinimler

```bash
sudo apt install ros-noetic-turtlebot3 \
                 ros-noetic-turtlebot3-simulations \
                 ros-noetic-turtlebot3-navigation \
                 ros-noetic-turtlebot3-slam \
                 ros-noetic-gmapping \
                 ros-noetic-map-server \
                 ros-noetic-amcl \
                 ros-noetic-move-base \
                 ros-noetic-cv-bridge \
                 python3-opencv

pip3 install opencv-python pyzbar qrcode pillow
```

### 2. AWS Bookstore World Kurulumu

```bash
cd ~/catkin_ws/src
git clone https://github.com/aws-robotics/aws-robomaker-bookstore-world.git
cd ~/catkin_ws && catkin_make && source devel/setup.bash
```

### 3. Bu Paketi Kurun

```bash
cd ~/catkin_ws/src
git clone https://github.com/yasincanozdil/final-homework.git turtlebot3_service_robot
cd ~/catkin_ws && catkin_make && source devel/setup.bash
```

### 4. TurtleBot3 Model Ayarı

```bash
echo "export TURTLEBOT3_MODEL=waffle_pi" >> ~/.bashrc
source ~/.bashrc
```

### 5. QR Panellerini Gazebo Model Dizinine Ekleyin

```bash
cp -r ~/catkin_ws/src/turtlebot3_service_robot/models/* ~/.gazebo/models/
```

---

## 🚀 Çalıştırma Adımları

### Adım 1 — Simülasyonu Başlatın

```bash
roslaunch turtlebot3_service_robot simulation.launch
```

### Adım 2 — SLAM ile Harita Çıkarın

```bash
# Terminal 2
roslaunch turtlebot3_service_robot slam.launch

# Terminal 3 (teleop)
rosrun turtlebot3_teleop turtlebot3_teleop_key

# Terminal 4 (haritayı kaydet)
rosrun map_server map_saver -f ~/catkin_ws/src/turtlebot3_service_robot/maps/map
```

### Adım 3 — Navigasyon Başlatın

```bash
roslaunch turtlebot3_service_robot navigation.launch
```

RViz açılınca **2D Pose Estimate** ile robotu lokalize edin.

### Adım 4 — Görevi Başlatın

```bash
roslaunch turtlebot3_service_robot task_manager.launch
```

Robot 4 noktayı sırayla ziyaret eder, QR doğrular ve rapor üretir.

---

## 🔧 Özel Parametreler

```bash
roslaunch turtlebot3_service_robot task_manager.launch timeout:=120
roslaunch turtlebot3_service_robot task_manager.launch qr_retries:=3
```

---

## 📡 ROS Topic / Service / Action Yapıları

### Topics

| Topic | Tür | Açıklama |
|-------|-----|----------|
| `/task_manager/status` | `std_msgs/String` | Anlık görev durumu |
| `/task_manager/report` | `std_msgs/String` | Görev sonu raporu |
| `/qr_reader/result` | `std_msgs/String` | Okunan QR içeriği |
| `/cmd_vel` | `geometry_msgs/Twist` | Hız komutu |
| `/odom` | `nav_msgs/Odometry` | Odometri |
| `/scan` | `sensor_msgs/LaserScan` | LIDAR tarama |
| `/map` | `nav_msgs/OccupancyGrid` | Harita |
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | Robot konumu |
| `/move_base/status` | `actionlib_msgs/GoalStatusArray` | Navigasyon durumu |

### Services

| Servis | Tür | Açıklama |
|--------|-----|----------|
| `/qr_reader/trigger` | `std_srvs/Trigger` | QR okuma tetikleyici |

### Actions

| Action | Tür | Açıklama |
|--------|-----|----------|
| `/move_base` | `move_base_msgs/MoveBaseAction` | Navigasyon hedef gönderme |

---

## 🎯 Görev Durumu Makinesi
---

## 📊 Hata Yönetimi

| Durum | Davranış |
|-------|----------|
| QR okunamaz | 2 kez yeniden dene → SKIPPED |
| QR yanlış eşleşme | 2 kez yeniden dene → SKIPPED |
| move_base başarısız | 1 kez yeniden dene → FAIL |
| move_base timeout (90s) | Hedef iptal et → FAIL |

---

## 📋 Değerlendirme Kriterleri

| Kriter | Puan |
|--------|------|
| SLAM ile haritalama ve map kaydı | 20 |
| Navigasyon ve çoklu waypoint yönetimi | 30 |
| QR kod okuma ve doğrulama | 25 |
| Görev yöneticisi ve hata yönetimi | 15 |
| GitHub dokümantasyonu ve demo videosu | 10 |
| **Toplam** | **100** |
