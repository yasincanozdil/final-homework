# 🤖 KTÜN Robotiğe Giriş — Final Ödevi
## Servis Robotu / Çoklu Görev QR Doğrulama

**Platform:** ROS1 Noetic + TurtleBot3 + Gazebo  
**Ortam:** AWS RoboMaker Bookstore World

---

## 📁 Proje Yapısı

```
turtlebot3_service_robot/
├── launch/
│   ├── simulation.launch    # Gazebo + Bookstore World + TurtleBot3
│   ├── slam.launch          # gmapping SLAM (haritalama)
│   ├── navigation.launch    # AMCL + move_base (lokalizasyon + navigasyon)
│   └── task_manager.launch  # QR okuyucu + Görev Yöneticisi
├── src/
│   ├── task_manager.py      # Ana görev yöneticisi node
│   └── qr_reader.py         # QR kod okuyucu node
├── config/
│   └── mission.yaml         # Waypoint ve QR beklenti tanımları
├── maps/
│   ├── map.yaml             # SLAM sonrası kaydedilen harita (metadata)
│   └── map.pgm              # SLAM sonrası kaydedilen harita (görsel)
├── models/
│   ├── qr_information_desk/ # Gazebo QR panel modeli
│   ├── qr_science_section/
│   ├── qr_novel_section/
│   └── qr_checkout_area/
├── CMakeLists.txt
├── package.xml
└── README.md
```

---

## ⚙️ Kurulum

### 1. Gereksinimler

```bash
# ROS Noetic temel paketleri
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

# Python QR kütüphanesi
pip3 install opencv-python pyzbar qrcode pillow
```

### 2. AWS Bookstore World Kurulumu

```bash
cd ~/catkin_ws/src
git clone https://github.com/aws-robotics/aws-robomaker-bookstore-world.git

# Bağımlılıkları kur
cd aws-robomaker-bookstore-world
pip3 install -r requirements.txt 2>/dev/null || true

# Build
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 3. Bu Paketi Kurun

```bash
cd ~/catkin_ws/src
# Repoyu buraya kopyalayın veya git clone yapın
# cp -r turtlebot3_service_robot .

cd ~/catkin_ws
catkin_make
source devel/setup.bash
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

**Terminal 2:**
```bash
roslaunch turtlebot3_service_robot slam.launch
```

**Terminal 3 (teleop — robot gezdirme):**
```bash
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

Tüm ortamı gezdikten sonra haritayı kaydedin:

**Terminal 4:**
```bash
rosrun map_server map_saver -f ~/catkin_ws/src/turtlebot3_service_robot/maps/map
```

> ✅ `map.yaml` ve `map.pgm` dosyaları `maps/` klasörüne kaydedilir.

SLAM ve teleop terminallerini kapatın.

---

### Adım 3 — Waypoint Koordinatlarını Güncelleyin

RViz açıkken harita üzerindeki noktaları belirleyin:
- Her hedef nokta için fareyi haritanın üzerine getirip koordinatları okuyun.
- `config/mission.yaml` dosyasını bu koordinatlarla güncelleyin.

```yaml
INFORMATION_DESK:
  goal:
    x: 1.5     # ← Kendi koordinatınız
    y: 0.0
    yaw: 0.0
```

---

### Adım 4 — QR Panellerini Gazebo Dünyasına Yerleştirin

Gazebo arayüzünden:
1. **Insert** sekmesini açın
2. `qr_information_desk`, `qr_science_section`, `qr_novel_section`, `qr_checkout_area` modellerini her görev noktasının yakınına sürükleyin
3. Paneli robotun kamerasının görebileceği yüksekliğe ayarlayın (~0.5m)

---

### Adım 5 — Navigasyon Başlatın

```bash
roslaunch turtlebot3_service_robot navigation.launch
```

RViz açıldıktan sonra:
- **2D Pose Estimate** butonuna tıklayın
- Robotu haritada doğru konuma yerleştirin (ok yönü = bakış yönü)
- Robot lokalize olana kadar bekleyin (ok kümeleri yoğunlaşacak)

---

### Adım 6 — Görevi Başlatın

```bash
roslaunch turtlebot3_service_robot task_manager.launch
```

Robot otomatik olarak:
1. `INFORMATION_DESK` → `SCIENCE_SECTION` → `NOVEL_SECTION` → `CHECKOUT_AREA` sırasıyla gidecek
2. Her noktada QR kodu okuyacak ve doğrulayacak
3. Sonunda raporu ekrana yazdıracak

---

## 🔧 Özel Parametreler

```bash
# Farklı mission dosyası kullanmak için:
roslaunch turtlebot3_service_robot task_manager.launch \
  mission_file:=/tam/yol/mission.yaml

# Navigasyon timeout süresini değiştirmek için:
roslaunch turtlebot3_service_robot task_manager.launch \
  timeout:=120

# QR yeniden deneme sayısını değiştirmek için:
roslaunch turtlebot3_service_robot task_manager.launch \
  qr_retries:=3
```

---

## 📡 ROS Topic / Service / Action Yapıları

### Topics

| Topic | Tür | Açıklama |
|-------|-----|----------|
| `/task_manager/status` | `std_msgs/String` | Anlık görev durumu |
| `/task_manager/report` | `std_msgs/String` | Görev sonu raporu |
| `/qr_reader/result` | `std_msgs/String` | Okunan QR içeriği |
| `/camera/rgb/image_raw` | `sensor_msgs/Image` | Kamera görüntüsü |
| `/cmd_vel` | `geometry_msgs/Twist` | Hız komutu |
| `/odom` | `nav_msgs/Odometry` | Odometri |
| `/scan` | `sensor_msgs/LaserScan` | LIDAR tarama |
| `/map` | `nav_msgs/OccupancyGrid` | Harita |

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

```
INIT
  │  (sistem hazır)
  ▼
GO_TO_LOCATION(i)
  │  (move_base hedef gönder)
  │  [başarısız → FAIL → NEXT]
  ▼
QR_VERIFY(i)
  │  (kameradan QR oku + doğrula)
  │  [okunamaz → SKIPPED → NEXT]
  ▼
REPORT(i)
  │  SUCCESS / FAIL / SKIPPED kaydet
  ▼
NEXT_LOCATION
  │  (i < toplam?) ────► GO_TO_LOCATION(i+1)
  │  (i == toplam?)
  ▼
FINISH
  │  Genel rapor yayınla
```

---

## 📊 Hata Yönetimi

| Durum | Davranış |
|-------|----------|
| QR okunamaz | 2 kez yeniden dene → SKIPPED |
| QR yanlış eşleşme | 2 kez yeniden dene → SKIPPED |
| move_base başarısız | 1 kez yeniden dene → FAIL |
| move_base timeout | Hedef iptal et, yeniden dene → FAIL |

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
