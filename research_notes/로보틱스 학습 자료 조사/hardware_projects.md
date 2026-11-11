# Hands-on Robotics Hardware Kits, Open-Source Platforms, and Project-Based Learning Resources (as of 2026-11-11)

Scope note: all prices are retailer/aggregator listings observed Nov 2026 unless marked "launch price". KRW figures were NOT found on Korean retailers for most items (see Gaps); where a KRW estimate is given it is an inference at an assumed ~1,400 KRW/USD and must be verified. 2026 is a bad year for compute pricing: a global DRAM shortage drove repeated Raspberry Pi 5 and NVIDIA Jetson price hikes (see §4), so any kit that bundles a Pi 5 or Jetson is more expensive than 2024–2025 guides suggest.

## Key Question 1 — Mobile robots: which platforms/kits exist, what do they cost, and which have the best teaching materials?

### Takeaway
For a ROS 2 curriculum the TurtleBot3 Burger (~€895 / ~$550–750 class, ROBOTIS, Korean company with a full free e-Manual) and the Duckiebot DB21 ($299 official, with a free ETH Zürich edX MOOC and a full "Learning Experiences" curriculum) have the strongest teaching materials; TurtleBot 4 (~$1,465 Lite / ~$2,575 Standard) is the "official" ROS 2 reference but rests on the now-retired iRobot Create 3 base. Sub-$100 Elegoo/Freenove Arduino cars and ~$160–195 Pololu 3pi+/Zumo 2040 cover the pre-ROS embedded tier; Yahboom/Hiwonder Pi 5 ROS 2 kits ($340–$1,080) are the budget ROS 2 middle tier but documentation quality is weaker.

### Cited Findings

**TurtleBot3 (ROBOTIS, Korea) — https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/ ; store https://www.robotis.us/ ; Korean mall https://www.robotis.com/shop/**
- Launch MSRP was $549 (Burger) and $1,799 (Waffle) — [IEEE Spectrum review](https://spectrum.ieee.org/automaton/robotics/robotics-hardware/review-robotis-turtlebot-3); the $549 figure for the Pi-3 kit is also given by [LinuxGizmos](https://linuxgizmos.com/ubuntu-driven-turtlebot-gets-a-major-rev-with-a-pi-or-joule-in-the-drivers-seat/).
- Burger ships with Raspberry Pi 4 as standard since Sept 2021 and the LDS-02 360° LiDAR — [ROBOTIS e-Manual features page](https://emanual.robotis.com/docs/en/platform/turtlebot3/features/).
- Current EU price: €894.92 incl. VAT / €745.87 excl. VAT with RPi4-4GB and LDS-02, 3 in stock, 24–48h shipping (Nov 2026) — [Generation Robots](https://www.generationrobots.com/en/402707-turtlebot3-burger-mobile-robot.html). Other EU listings: ~€460 without LiDAR, ~€714–789 with RPi4 — [Funduino (no LiDAR)](https://funduinoshop.com/en/robotics/robotis/robotik/robotis-turtlebot3-burger-without-lidar), [Funduino RPi4-4GB](https://funduinoshop.com/en/robotics/robotis/robotik/robotis-turtlebot3-burger-rpi4-4gb), [Robot Italy](https://robot-italy.com/en/products/robotis-turtlebot3-burger).
- Burger drive-wheel Dynamixel (XL430) replacement price listed at $27.50 in a 2026 price guide — [GrabARobot ROBOTIS/TurtleBot price guide 2026](https://grabarobot.com/blog/robotis-turtlebot-dynamixel-price-guide-2026/). (Note: when fetched, the page said it "does not establish a current educational robot transaction price" and asks for quotes; treat as weak.)
- The e-Manual is the canonical curriculum: covers ROS 2 (Humble/Jazzy) setup, SLAM, Navigation, simulation (Gazebo), manipulation (with OpenMANIPULATOR-X), machine learning, and autonomous driving examples — [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/). A Korean-language community guide (모두의연구소) also summarises the TurtleBot series — [modulabs notion](https://modulabs.notion.site/10-65340cb0d83f4a70b047f923ba65c05f).
- The Korean ROBOTIS mall (robotis.com/shop) has TurtleBot3 (category ca_id=4050) and OpenMANIPULATOR (ca_id=4030) menu entries; the fetched Dynamixel category showed only motor prices in KRW (e.g., YM080-230-R099-RH 2,937,000원) — [ROBOTIS Korea shop](https://www.robotis.com/shop/list.php?ca_id=20). Direct TurtleBot3 KRW listing was not retrieved (see Gaps).

**TurtleBot 4 (Clearpath Robotics, Canada; base = iRobot Create 3) — https://clearpathrobotics.com/turtlebot-4/ ; docs https://turtlebot.github.io/turtlebot4-user-manual/**
- Launch prices: Standard $1,850, Lite $1,195 (2022) — [Robotics 24/7](https://www.robotics247.com/article/clearpath_robotics_open_robotics_launch_turtlebot_4_ros_2_support).
- Current RobotShop US listings: Lite $1,465 (tariffs included) — [RobotShop TB4 Lite](https://www.robotshop.com/products/clearpath-robotics-turtlebot-4-lite-mobile-robot); Standard $2,575 — [RobotShop TB4 Standard](https://www.robotshop.com/products/clearpath-robotics-turtlebot-4-mobile-robot); TurtleBot 4 Pro €3,206.50 — [RobotShop EU](https://eu.robotshop.com/products/turtlebot-4-pro).
- The Clearpath TB4 landing page is a lead-capture form that gates the docs; no public prices — [Clearpath TurtleBot 4](https://clearpathrobotics.com/turtlebot-4/).
- RISK: iRobot's knowledge base states it "has retired its Create 3 product" but will honour the warranty period; troubleshooting goes to the Create 3 forum — [iRobot Education KB](https://experience.irobot.com/en/irobot-education-support/what-is-your-return-policy). iRobot paused all non-floorcare development in Jan 2024 and the Create 3 shop link broke Nov 2, 2024 — [RobotShop community thread](https://community.robotshop.com/forum/t/irobot-and-the-create3/110122). iRobot entered Chapter 11 (expected to finish by Feb 2026) and was taken over by Picea — [A3 / Automate.org](https://www.automate.org/robotics/industry-insights/irobot-files-for-bankruptcy).

**iRobot Create 3 — https://iroboteducation.github.io/create3_docs/**
- Retired (see above). Standalone purchase is no longer possible from iRobot; only legacy stock/TurtleBot 4 bundles remain — [iRobot Education KB](https://experience.irobot.com/en/irobot-education-support/what-is-your-return-policy).

**Husarion ROSbot 3 (Poland) — https://husarion.com/manuals/rosbot/ ; store https://store.husarion.com/products/rosbot-3**
- Husarion store sale price €2,749 with one-year warranty — [Husarion store](https://store.husarion.com/products/rosbot-3); UK £2,345 (was £2,814) — [RoboSavvy](https://robosavvy.co.uk/husarion-rosbot-3.html); ROSbot 3 PRO C$6,209.97 — [Canada Satellite](https://www.canadasatellite.ca/Husarion-ROSbot-3-PRO.htm).
- Manual covers ROSbot 3 and legacy 2R/2 PRO — [Husarion manual](https://husarion.com/manuals/rosbot/).

**Duckietown / Duckiebot DB21 (Duckietown Foundation; ETH Zürich / MIT origin) — https://duckietown.com ; store https://get.duckietown.com ; docs https://docs.duckietown.com**
- Official store: Duckiebot DB-J (DB21 series, Jetson Nano) $299, one snapshot showed "Sold out" — [Duckietown store](https://get.duckietown.com/products/duckiebot-db21). Classroom Kit (30) also listed — [classroom kit 30](https://get.duckietown.com/collections/frontpage/products/classroom-kit-30). Upgrade kit DB21M/J → DB21J v3 exists — [upgrade kit](https://get.duckietown.com/products/duckiebot-upgrade-kit-db21m-or-db21j-to-db21j-v3).
- Resellers: RS UK DB21-J without Jetson £215.58 ex-VAT — [RS Online UK](https://uk.rs-online.com/web/p/stem-invention-kits/2268899); RobotShop MOOC Founders kit with Jetson Nano 4GB + nav starter pack $669 (47 in stock) — [RobotShop](https://www.robotshop.com/products/duckietown-mooc-founders-edition-kit-db21-m-k).
- Free MOOC "Self-Driving Cars with Duckietown" on edX (ETH Zürich, U. Montréal, TTIC); free to audit, pay only for graded certificate; covers lane following, object detection, planning with Python, ROS, Docker; from the 2025 edition it supports virtual Duckiebots (no hardware required) — [Duckietown MOOC page](https://duckietown.com/mooc/), [edX course](https://www.edx.org/learn/technology/eth-zurich-self-driving-cars-with-duckietown), [Instructor manual: MOOC curriculum](https://docs.duckietown.com/ente/duckietown-manual/80-instructor-manual/sample-curricula/mooc/index.html).
- Education page lists hands-on "Learning Experiences" (ROS Basics, Kinematics & Odometry, PID Control, Computer Vision, EKF Localization, Object Detection, Collision Checker, Planning, Braitenberg Vehicles), each with slides/notes/videos, runnable in simulation ("Duckiematrix") or on robot; pricing tiers for independent learners/universities/enterprise — [Duckietown Education](https://duckietown.com/education/).
- Duckiebot DB21 runs on Jetson Nano, which NVIDIA is retiring (see §4) — [NVIDIA blog on Duckietown + Jetson Nano 2GB](https://blogs.nvidia.com/blog/jetson-nano-2gb-duckietown).

**Yahboom / Hiwonder (China) ROS 2 kits on Raspberry Pi 5 / Jetson**
- Hiwonder MentorPi A1 Standard (Pi 5 8GB, LiDAR SLAM, ROS 2 Humble) $639.99; TurboPi (Pi 5 8GB, Python) $339.99; ArmPi FPV 6-DOF arm w/ Pi 5 8GB $539.99 (Amazon, Apr 2026) — [SpecPicks aggregator](https://specpicks.com/product/B0FHHPZFVZ); ArmPi Ultra ~$666.99 — [OZRobotics](https://ozrobotics.com/product-tag/ros2-robot-arm/).
- Yahboom Pi 5 8GB ROS 2 robot with dual LiDAR $969.90; with 2D SLAM + AI vision $1,079.90; ROSMASTER A1 + Raspbot V2 bundle $664.89; Raspbot V2 4WD without Pi 5 $158.64 (list $226.63) — [SpecPicks](https://specpicks.com/product/B0G4QXVH4T), [Tufzen](https://tufzen.com/products/yahboom-4wd-raspbot-v2-ai-large-model-robot-kit-for-raspberry-pi-5-beginners-educational-project-ros2-humble-python-programming); Yahboom MicroROS Pi5 ROS 2 Humble car — [RobotShop](https://robotshop.com/products/yahboom-microros-pi5-ros2-robot-car-raspberry-pi-5-ros2-humblepython3-with-raspberry-pi5-2gb).
- Many listings exclude the Pi 5 board; ROS version (Humble vs unspecified) varies by bundle — same sources.

**Elegoo / Freenove Arduino & Raspberry Pi cars (China)**
- Elegoo Smart Robot Car Kit V4.0 with camera $75.99 (US store) / €69.99 (EU) — [Elegoo US](https://elegoo.com/collections/filaments/products/elegoo-smart-robot-car-kit-v-4-0), [Elegoo EU](https://eu.elegoo.com/en-it/products/elegoo-smart-robot-car-kit-v-4-0); UNO R3 V4 kit $79.95 — [reseller](https://reach.dog/shop/alpha-3d-lab/products/elegoo-uno-r3-project-smart-robot-car-kit-v4-with-uno-r3); Conqueror Tank $99.99 deal — [Slickdeals](https://slickdeals.net/f/17226169-elegoo-conqueror-tank-stem-programming-robot-kit-99-99).
- Freenove 4WD Arduino car ~$45 (out of stock listing) — [Desertcart](https://www.desertcart.us/products/735190192-freenove-4wd-car-kit-with-remote-control-arduino-ide-compatible.md); Freenove Pi-based kits don't include the Pi — same search.

**Pololu 3pi+ 2040 / Zumo 2040 (USA; RP2040, MicroPython/C++)**
- 3pi+ 2040 Hyper Edition assembled $161.95 — [Pololu #5000](https://www.pololu.com/product/5000/blog); Standard Edition kit (30:1) — [Pololu #5004 via Core Electronics](https://core-electronics.com.au/catalog/product/view/sku/POLOLU-5004); Turtle Edition kit — [Pololu #5005](https://www.pololu.com/product/5005).
- Zumo 2040 assembled 75:1 $194.95 — [Pololu #5012](https://www.pololu.com/product/5012/specs); motorless kit — [Pololu #5011](https://www.pololu.com/product/5011).

**JetBot / DonkeyCar / JetRacer (NVIDIA Jetson Nano based)**
- NVIDIA JetBot project page still up — [NVIDIA JetBot](https://developer.nvidia.com/embedded/learn/jet-diy-robotics-kit); DonkeyCar on Jetson Nano community page — [NVIDIA DonkeyCar](https://developer.nvidia.com/embedded/community/jetson-projects/donkey_car).
- Jetson Nano Developer Kit EOL: NVIDIA forum states the 4GB dev kit will be discontinued as inventory declines — [NVIDIA forum EOL thread](https://forums.developer.nvidia.com/t/jetson-nano-developer-kit-eol/276729); a vendor states Nano EOL from January 2026 — [ThinkRobotics JetRacer Pro listing](https://thinkrobotics.com/products/jetracer-pro-high-speed-ai-racing-robot-kit-online). SparkFun JetBot kit (without Nano) marked discontinued by a reseller — [Little Bird](https://littlebirdelectronics.com.au/products/sparkfun-jetbot-ai-kit-without-jetson-nano).
- NVIDIA phasing out older Jetson modules as LPDDR4 supply tightens; final POs by July 1, 2026, last shipments July 15, 2027 — [Digital Citizen](https://www.digitalcitizen.life/nvidia-is-phasing-out-older-jetson-modules-as-lpddr4-supply-gets-tighter/), [pulse.bot](https://www.pulse.bot/hardware/news/nvidia-phases-out-several-jetson-modules-due-to-high-lpddr4-ram-prices-and-tight-supplies-8627a664-bde2-4fc8-a267-c58a12393bd6/).
- Waveshare JetRacer AI kit lists DonkeyCar among supported libraries (Nano not included) — [Waveshare JetRacer](https://www.waveshare.com/jetracer-ai-kit.htm), [RobotShop CA](https://ca.robotshop.com/products/waveshare-jetracer-ai-kit-ai-racing-robot-powered-by-jetson-nano-not-included).

### Inferences
- Best teaching materials, ranked: (1) Duckietown — a complete, free, university-grade curriculum with simulation fallback; (2) ROBOTIS TurtleBot3 e-Manual — the de-facto ROS 2 tutorial robot and the only one from a Korean vendor with domestic support; (3) TurtleBot 4 docs (good but the Create 3 base is retired, making long-term supply a risk for a new curriculum); (4) Husarion (good tutorials, but €2.7k); (5) Yahboom/Hiwonder (lots of video/Gitee docs but uneven English, pre-configured images rather than teaching ROS 2 from scratch).
- For a Korean software-developer audience, TurtleBot3 Burger is the pragmatic ROS 2 flagship: domestic vendor, Korean-language community, CPU-only RPi4 (not hit by Jetson Nano EOL), and the Burger's parts are individually replaceable via the ROBOTIS mall.
- Jetson-Nano-based kits (JetBot, Duckiebot DB21-J, JetRacer) should be labelled "buy only with hardware already in hand / expect migration to Orin Nano" in a 2026 curriculum.
- KRW estimates (inference, ~1,400 KRW/USD, verify): TB3 Burger ≈ 1.0–1.25M원 (based on €895), TB4 Lite ≈ 2.05M원, Duckiebot DB21 ≈ 42만원 (+Jetson), Elegoo V4 ≈ 10–11만원, Pololu 3pi+ ≈ 23만원.

### Gaps
- Could not retrieve robotis.us (HTTP 429 twice) or the Korean ROBOTIS mall TurtleBot3 category page, so no confirmed 2026 USD or KRW list price for TB3 Burger/Waffle Pi; EU €895 is the best dated primary figure.
- No Korean retailer (디바이스마트, 엘레파츠, 11번가) listing for TurtleBot3, Duckiebot, Yahboom/Hiwonder ROS 2 kits, or Pololu was found in search; 11번가 results were unrelated products.
- No confirmed statement on whether Clearpath will continue TurtleBot 4 production after Create 3 retirement.
- DonkeyCar project maintenance status in 2026 unverified (no GitHub release info retrieved).

## Key Question 2 — Manipulators: prices, docs, ROS 2 support

### Takeaway
The Hugging Face LeRobot SO-101 is the price/learning sweet spot: official BOM $121.94 (follower only) / $229.88 (leader+follower) DIY, $300–$500 as assembled kits, with a Python-first imitation-learning curriculum and a Korean complete-kit vendor (RoboSEasy) listed in the BOM. Mid-tier options are myCobot 280 ($499–$759, ROS 2 Humble), Dobot Magician Lite (~$995), OpenMANIPULATOR-X (~$1,629), while research arms (WidowX AI ~$3–6k, uFactory Lite 6 €3k+, Niryo Ned2 ~$3.7–8k, Ned2 reported no longer available at one distributor) exceed a learner budget.

### Cited Findings

**LeRobot SO-100 / SO-101 (Hugging Face + The Robot Studio) — https://github.com/huggingface/lerobot ; docs https://huggingface.co/docs/lerobot/so101 ; hardware https://github.com/TheRobotStudio/SO-ARM100**
- Official BOM totals: leader+follower $229.88 / €226.30 / ¥44,530; follower only $121.94 / €124.30 — [SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100).
- Motors: Feetech STS3215 7.4V; follower uses 6× 1/345; leader uses mixed 1/147, 1/191, 1/345 gearing; 12V variant gives 30 kg·cm vs 16.5 kg·cm — [SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100), [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101).
- Sellers listed by region: US/EU via Alibaba + Amazon; China Alibaba/TaoBao; Japan Akizuki Denshi; **RoboSEasy (South Korea) listed for complete kits** — [SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100).
- 3D printing: PLA+, 15% infill, 0.4 mm nozzle/0.2 mm layer; Ender (220×220) or Prusa/UP bed single-file sets; printing-service options in 3DPRINT.md — same README.
- Required skills: basic 3D printer operation, mechanical assembly with #0/#1 Phillips, USB/serial motor setup via `lerobot-find-port`, `lerobot-setup-motors`, `lerobot-calibrate` CLI; Python install `pip install 'lerobot[feetech]'`; Discord support — [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101).
- Launch: base price $100, assembled/tariffed units $100–~$500 — [TechCrunch](https://techcrunch.com/?p=2999850); [Hackster launch article](https://www.hackster.io/news/hugging-face-launches-the-so-101-an-upgraded-low-cost-3d-printable-autonomous-robot-arm-532360f441eb).
- Kit prices 2026: Seeed SO-ARM101 Pro assembled $432.84 — [OpenELAB](https://openelab.com/products/seeed-studio-so-arm101-pro-assembled-kit-lerobot-6dof-robotic-arm); Seeed servo kit (no printed parts) $312 (sold out) — [rcdrone](https://rcdrone.top/products/so-arm101-low-cost-ai-arm-servo-motor-kit-pro-for-lerobot-without-3d-printed-parts); printed skeleton only $59.65 — [rcdrone](https://rcdrone.top/products/so-arm101-low-cost-ai-arm-3d-printed-skeleton); Hiwonder assembled starter $396.89 — [OZRobotics](https://ozrobotics.com/?p=214221); "Complete kit $499 / DIY ~$300" — [roboticscenter.ai](https://roboticscenter.ai/hardware/so-101); India ₹27,999 DIY (one arm) — [ThinkRobotics review](https://thinkrobotics.com/blogs/product-reviews-buying-guides/thinkrobotics-lerobot-so-101-6-axis-robotic-arm-review-ai-ready-open-source-and-built-for-learning).
- A Korean-language wikidocs guide exists for the SO-ARM101 BOM and assembly — [wikidocs BOM](https://wikidocs.net/307112), [wikidocs assembly](https://wikidocs.net/328746); roboticscenter.ai has a Korean SO-101 buying guide — [roboticscenter.ai ko](https://www.roboticscenter.ai/ko/guides/robot-arms/so-101-buying-guide).
- A 2026 beginner guide budgets "SO-100 arm on a laptop with no GPU ≈ $110" to learn fundamentals — [YouWare roadmap](https://www.youware.com/guide/getting-started-robotics-beginner-guide).

**Koch arm / ALOHA / Mobile ALOHA low-cost derivatives**
- Mobile ALOHA costs ~$32,000; TidyBot++ $5,000–6,000; XLeRobot $660; AhaRobot $1,000–2,000; Nori Bot (May 2026) 17-DoF dual-arm mobile manipulator parts cost $947 — [Nori Bot arXiv 2605.16537](https://arxiv.org/html/2605.16537). YOR (Feb 2026) open-source bimanual mobile manipulator BOM < $10k — [arXiv 2602.11150](https://arxiv.org/pdf/2602.11150).
- Trossen Solo AI (commercial ALOHA-derived single-arm kit) $11,385.95 — [Trossen store](https://store.trossenrobotics.com/products/solo-ai). Hobbyists on HomeBrew Robotics Club (Jun 2026) are building "AlohaMini" variants with SO-ARM-200 — [hbrobotics thread](https://groups.google.com/g/hbrobotics/c/XRpjKicK6qQ).

**Elephant Robotics myCobot 280 — https://www.elephantrobotics.com/en/mycobot-en/**
- M5 version $649, Arduino $499, Raspberry Pi $759 (Jul 2026 guide) — [GrabARobot Elephant price guide](https://grabarobot.com/blog/elephant-robotics-price-guide-2026/); myCobot 280 RDK X5 ¥150,920 (Japan, released 2025-10-02) — [Switch Science](https://www.switch-science.com/collections/mycobot/products/10623).
- Supports Linux/Windows/macOS, ROS 1 Noetic, ROS 2 Humble — [Robozaps listing](https://robozaps.com/products/mycobot-280); RDK X5 variant ROS 2 via TogetheROS.Bot — [D-Robotics blog](https://en.d-robotics.cc/blog/mycobot-280-rdk-x5-a-6-dof-robotic-arm-with-rdk-x5-power-ai-vision-llms-high-performance-for-budget-focused-developers).

**ROBOTIS OpenMANIPULATOR-X — https://emanual.robotis.com/docs/en/platform/openmanipulator_x/overview/**
- $1,629.09 (Jul 2026 guide); 4-DOF + gripper, 500 g payload, 380 mm reach — [GrabARobot ROBOTIS guide](https://grabarobot.com/blog/robotis-turtlebot-dynamixel-price-guide-2026/) (weak source; see note above). Korean mall category ca_id=4030 exists — [ROBOTIS shop](https://www.robotis.com/shop/list.php?ca_id=20).

**Trossen / Interbotix WidowX AI — https://store.trossenrobotics.com/products/widowx-ai**
- Conflicting prices: $3,795 base / $3,825 leader on one Trossen snapshot; $5,935.45 on another; a 2026 guide says $2,995 base / $3,135 leader / $3,445 follower, build-to-order — [Trossen store](https://store.trossenrobotics.com/products/widowx-ai), [GrabARobot Trossen guide](https://grabarobot.com/blog/trossen-robotics-price-guide-2026/); €5,880 — [Generation Robots](https://www.generationrobots.com/en/404333-widowx-ai.html). Legacy WidowX-250S still listed — [Trossen](https://store.trossenrobotics.com/products/widowx250s).

**uFactory Lite 6** — "From €3,000 ex-VAT" — [Generation Robots blog](https://www.generationrobots.com/blog/?p=21535); US listings $7,101–$8,539 — [Qviro](https://qviro.com/product/ufactory/lite-6) (wide spread; unreliable).

**Dobot Magician / Magician Lite** — Magician Lite from $995 — [RobotLAB](https://www.robotlab.com/?p=5762); education arms typically $995–$1,995 street — [GrabARobot Dobot guide](https://grabarobot.com/blog/dobot-robot-price-guide-2026/). (Magician classic price not found; Magician E6 cobot $15,993 is a different product.)

**Niryo Ned2** — RS Australia A$7,144.62 ex-GST; RS UK £3,719.69 — [RS UK](https://uk.rs-online.com/web/p/educational-robots/2356719); RobotLAB says "Ned 2 is no longer available" — [RobotLAB](https://www.robotlab.com/store/niryo-ned-2-robotic-arm/).

### Inferences
- SO-101 is the only arm where the full learning stack (hardware BOM, assembly video, calibration CLI, teleop, dataset recording, ACT/Diffusion policy training) is free and Python-native; it's the obvious manipulation module for a developer-oriented curriculum. ROS 2 is not the native stack (LeRobot is pure Python), so pair it with TurtleBot3/OpenMANIPULATOR-X or a ROS 2 wrapper if ROS 2 manipulation (MoveIt 2) is a learning goal.
- RoboSEasy appearing in the official BOM means a Korean learner can buy a complete kit domestically; KRW price unverified (likely ~40–70만원 given $300–$500 global kit range — inference).
- Niryo Ned2 appears end-of-life at distributors; mark "verify before recommending".
- KRW estimates (inference): SO-101 DIY pair ≈ 32만원 + 3D printing; myCobot 280 M5 ≈ 90만원; OpenMANIPULATOR-X ≈ 2.3M원.

### Gaps
- No KRW list price found for SO-101 kits at RoboSEasy or any Korean shop; no Korean listing for myCobot/OpenMANIPULATOR-X.
- OpenMANIPULATOR-X official ROBOTIS price not retrieved (robotis.us 429).
- Koch v1.1 arm specific pricing/status and Dobot Magician (classic) 2026 price not found.
- Whether Trossen's WidowX AI ships with ROS 2 drivers vs LeRobot-only was not verified.

## Key Question 3 — Legged / humanoid / drones for learning

### Takeaway
Unitree Go2 is now $1,600 (Air, often not stocked) / ~$3,690–3,790 (Pro) / ~$11,090–15,600 (EDU, the only tier with an SDK for development) — far above a learner budget; the learner-tier quadrupeds are Petoi Bittle X ($255–$399, Python/C++/ROS) and the open-source Stanford Pupper v3 (~$2,000 DIY) with the full CS123 course online. For drones, Crazyflie 2.1+/2.1 Brushless ($480 bare, $570–$675 STEM bundles) has an MIT-licensed ROS 2 stack (Crazyswarm2), and PX4 + Gazebo SITL is free.

### Cited Findings

**Unitree Go2 — https://unitree.com/go2**
- Launch: Air $1,600, Pro $2,800 — [Hackster](https://www.hackster.io/news/unitree-launches-next-generation-go2-quadrupedal-robot-platforms-starting-at-1-600-17fa0d4304c8).
- Oct 2026 US store guide: Go2 Air $1,600 (not stocked), Go2 Pro $3,690, Go2 EDU $11,090; AGIBOT D1 Pro/EDU from $4,599 — [roboticscenter.ai robot dog price guide (updated 2026-10-17)](https://www.roboticscenter.ai/blog/robot-dog-price-guide). Go2 Pro $3,790 (Aug 2026) — [Global Drone HQ](https://globaldronehq.com/blogs/guides/unitree-robot-price-guide-2026); retailer Go2 EDU $14,599 — [Airpuria](https://airpuria.com/products/unitree-go2-edu-ai-quadruped-robot-dog), $15,637.50 — [Stemfinity](https://stemfinity.com/products/unitree-go2-edu-ai-quadruped-robot-dog). Earlier 2026 guides listed EDU at $3,790 (conflicting/outdated) — [roboticscenter.ai best under $5000](https://www.roboticscenter.ai/learn/best-quadruped-robots-under-5000).

**Petoi Bittle X — https://www.petoi.com/products/petoi-robot-dog-bittle-x-voice-controlled**
- From $319 (construction kit, lite servos); $339 assembled lite; $379 kit / $399 assembled alloy — [Mitrade "Best Robot Dogs 2026"](https://www.mitrade.com/insights/news/live-news/article-3-2019735-20260821), [Petoi](https://petoi.com/products/petoi-robot-dog-bittle-x-voice-controlled); NRW 2026 sale $254.99 — [Petoi NRW page](https://www.petoi.com/pages/nrw-2026); V2 alloy kit $379 — [RobotShop](https://www.robotshop.com/products/petoi-bittle-x-v2-construction-kit-w-alloy-servos).
- Supports block coding, Python, C++, ROS — [RobotShop CA](https://ca.robotshop.com/products/bittle-x-open-source-voice-controlled-robot-dog-assembled); optional robotic arm — [Petoi](https://petoi.com/products/petoi-robot-dog-bittle-x-with-optional-robotics-arm).

**Stanford Pupper v3 + CS123 — https://pupper-v3-documentation.readthedocs.io/ ; course https://cs123-stanford.readthedocs.io/**
- Open source; "build Pupper yourself for about $2000"; RL locomotion trained in sim ("one hour = 3 months of training"); uses OpenAI Realtime API + VLMs; Foxglove for visualisation; course link `/course/course.html`; Discord discord.gg/qbmaU8NmP2 — [Pupper v3 docs](https://pupper-v3-documentation.readthedocs.io/en/latest/).
- CS 123 "A Hands-On Introduction to Building AI-Enabled Robots": motor control, FK/IK, system ID, simulation, RL; weekly labs assembling and programming Pupper; final project (Fall 2026 schedule: presentations 11/30, final code 12/7); lottery admits 24 of first 100 applicants — [CS123 current](https://cs123-stanford.readthedocs.io/en/latest/), [Fall 2025 ref](https://cs123-stanford.readthedocs.io/en/latest/_sources/reference/fall_2025.rst.txt), [Lab 3 IK](https://cs123-stanford.readthedocs.io/en/latest/schedule/labs/spring-25/lab-3.html), [2024 edition](https://cs123-stanford-2024.readthedocs.io/en/latest/), [2023 edition](https://cs-123-stanford-2023.readthedocs.io/en/latest/).
- Course in its third year in 2025; lineage from Stanford Doggo (2019) — [Stanford News, Jul 2025](https://news.stanford.edu/stories/2025/07/ai-powered-robot-dogs-pupper-cs-123-robotics-students). Independent-study docs — [pupper-independent-study](https://pupper-independent-study.readthedocs.io/en/latest/).

**Crazyflie (Bitcraze, Sweden) — https://www.bitcraze.io/products/crazyflie-2-1-brushless/ ; https://bitcraze.io/products/crazyflie-2-1-plus/**
- Crazyflie 2.1 Brushless $480 (RobotShop US, tariffs incl.) — [RobotShop](https://www.robotshop.com/products/bitcraze-crazyflie-21-brushless); STEM Ranging Bundle $673; Happy Hacker Bundle $571.50 — [RobotShop STEM ranging](https://www.robotshop.com/products/bitcraze-stem-ranging-bundle-crazyflie-21-brushless), [Happy Hacker](https://www.robotshop.com/products/bitcraze-happy-hacker-bundle-crazyflie-21-brushless); €600 incl. VAT — [Generation Robots](https://www.generationrobots.com/en/404391-crazyflie-21-brushless.html); UK £397.57 (sold out) — [Unmanned Tech](https://www.unmannedtechshop.co.uk/products/crazyflie-2-1-brushless-hacker-drone).
- Crazyswarm2: open-source (MIT) ROS 2 stack for Crazyflie 2.1(+), 2.1 Brushless, Flapper Nimble+, Bolt-based builds — [Crazyswarm2 docs](https://imrclab.github.io/crazyswarm2/). (Supported ROS 2 distro not stated on landing page.)

**PX4 + Gazebo SITL** — free simulator path; docs at [PX4 Gazebo simulation](https://docs.px4.io/main/en/sim_gazebo_gz/) (not fetched; URL from training knowledge — verify).

**Open-source quadrupeds (SpotMicro, ODRI Solo 12), MIT Mini Cheetah** — no 2026 sources surfaced in searches (see Gaps).

### Inferences
- A learner-tier legged module should be Bittle X (cheap, Python, fits a $300 tier) with Pupper v3 as the "capstone" build (~$2k) and CS123's free labs as the curriculum; Go2 EDU is an institutional purchase only.
- Crazyflie is the only sub-$700 drone with a maintained ROS 2 stack and strong Python API; good fit for a "ROS 2 + control" module; PX4 SITL covers the zero-hardware tier.
- KRW estimates (inference): Bittle X ≈ 45–56만원; Crazyflie 2.1 Brushless ≈ 67만원; Pupper v3 ≈ 2.8M원; Go2 Pro ≈ 5.2M원.

### Gaps
- No official unitree.com price confirmed; no Korean distributor (e.g., 유니트리 한국 총판) pricing found.
- ODRI Solo 12, SpotMicro, MIT Mini Cheetah: no 2026 availability/cost sources found in searches.
- Crazyswarm2 supported ROS 2 distributions and Bitcraze's own 2026 store price not retrieved.
- Korean availability for Petoi/Crazyflie not found.

## Key Question 4 — Microcontroller/embedded foundations: boards, sensors, tutorials, micro-ROS

### Takeaway
2026 compute prices are inflated by the DRAM shortage: Raspberry Pi 5 2GB is $77.50 and 16GB $385 (Nov 2026), Jetson Orin Nano Super rose from $249 to $399 (Jul 2026), and Jetson Nano is EOL. Cheap sensing remains viable (LD19 ~$69–$100-class, RPLIDAR A1 ~$99) but OAK-D Lite jumped to $269 and RealSense D435 pricing is "on request". micro-ROS has solid free tutorials for Pico (Canonical) and ESP32 (Hackster/Articulated Robotics).

### Cited Findings
- Raspberry Pi 5 16GB rose $80 to $385 in Nov 2026 (launched at $120 in 2025, previously $305) — [OMG! Ubuntu](https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up), [Phoronix](https://phoronix.com/news/Raspberry-Pi-5-16GB-385); 2GB rose to $77.50 on Oct 1, 2026 — [Phoronix](https://www.phoronix.com/news/Raspberry-Pi-5-2GB-Price-77.50); LPDDR4 up sevenfold YoY as of Apr 2026 — [BGR](https://bgr.com/2150106/raspberry-pi-cost-ram-crisis/); supply expected tight until 2028–2030 — [TechRadar](https://www.techradar.com/pro/raspberry-pi-5-price-hike-means-the-16gb-model-now-costs-three-times-what-it-did-at-launch-and-of-course-the-global-ram-shortage-is-to-blame); earlier rounds — [Tom's Hardware](https://www.tomshardware.com/raspberry-pi/component-shortages-drive-raspberry-pi-prices-up-by-up-to-23-percent-escalating-lpddr4-lpddr5-costs-trigger-the-third-price-hike-of-the-year), [The Register](https://www.theregister.com/2026/02/02/raspberry_pi_ram_shortage_price_hike/).
- NVIDIA Jetson Orin Nano Super Developer Kit launched at $249 (Dec 2024) and was raised to $399 (+60%) in Jul 2026; AGX Thor kit $3,499→$5,499 — [CNX Software](https://cnx-software.com/2026/07/22/nvidia-increases-the-price-of-jetson-modules-and-devkits-by-up-to-101), [Notebookcheck](https://www.notebookcheck.net/Nvidia-quietly-increases-Jetson-prices-by-up-to-101.1348323.0.html). Some retailers still show $245–249 (likely stale) — [DFRobot](https://www.dfrobot.com/product-2900.html).
- Jetson Nano dev kit EOL / older modules phased out (see §1) — [NVIDIA forum](https://forums.developer.nvidia.com/t/jetson-nano-developer-kit-eol/276729).
- LDROBOT LD19 (D300 kit): Waveshare says the LD19-based D300 kit is discontinued and recommends the D500 — [Waveshare](https://waveshare.com/dtof-lidar-ld19.htm); LD19 with connector $69 — [SensorLidar](https://sensorlidar.com/products/ldrobot-ld06-ld19-d300-of-laser-radar-lidar-scanner-360-scanning-d500-lidar-kit-support-ros1-and-ros2-for-indoor-and-outdoor); A$209.95 — [Core Electronics](https://core-electronics.com.au/dtof-ld19-laser-lidar-sensor-kit-12m.html.md). Community list of 2D LiDARs with ROS support — [awesome-2d-lidars](https://github.imc.re/kaiaai/awesome-2d-lidars).
- RPLIDAR A1 ~$99 — [Industrial Monitor Direct guide](https://industrialmonitordirect.com/blogs/knowledgebase/affordable-lidar-options-for-student-robotics-projects), [awesome-2d-lidars](https://github.imc.re/kaiaai/awesome-2d-lidars).
- OAK-D Lite Auto Focus price rose $169→$269 effective Jul 9, 2026 — [Luxonis pricing change](https://shop.luxonis.com/pages/pricing-change-oak-lite-oak-1), [Luxonis OAK-D Lite](https://shop.luxonis.com/products/oak-d-lite-1).
- RealSense D435: "In stock, price upon request" at one retailer; no reliable 2026 price — [Generation Robots sensors](https://generationrobots.com/en/225-sensors); depth camera comparison — [roboticscenter.ai](https://roboticscenter.ai/learn/robot-camera-depth-sensor-comparison).
- micro-ROS on Raspberry Pi Pico: Canonical getting-started (VS Code project, node visible to ROS 2 host) — [Ubuntu blog](https://ubuntu.com/blog/getting-started-with-micro-ros-on-raspberry-pi-pico); follow-up HC-SR04 sonar publishing — [Ubuntu blog](https://ubuntu.com/blog/hc-sr04-with-the-raspberry-pi-pico-and-micro-ros); ROS Discourse thread — [Pico and ROS 2](https://discourse.openrobotics.org/t/raspberry-pi-pico-and-ros-2/18733.md); Hackaday.io project — [Running micro-ROS on Pico](https://hackaday.io/project/180426).
- micro-ROS on ESP32 with Arduino IDE — [Hackster tutorial](https://hackster.io/514301/micro-ros-on-esp32-using-arduino-ide-1360ca); ESP32 porting discussion — [ROS Discourse](https://discourse.openrobotics.org/t/micro-ros-porting-to-esp32/16101?page=2); Articulated Robotics beginner micro-ROS video (button → robot) — [Class Central listing](https://classcentral.com/course/youtube-could-this-button-control-your-robot-beginner-micro-ros-tutorial-272127).
- Yahboom sells a "MicroROS Pi5" car (ESP32 micro-ROS + Pi 5 ROS 2 Humble) — [RobotShop](https://robotshop.com/products/yahboom-microros-pi5-ros2-robot-car-raspberry-pi-5-ros2-humblepython3-with-raspberry-pi5-2gb).
- Korean electronics retailer 디바이스마트 carries education robot kits (e.g., AVR Super Sumo Robot, "터틀 로봇 + USB 동글") and offers free shipping over 66,000원 — [디바이스마트 item](https://www.devicemart.co.kr/goods/view?no=12520954), [AVR sumo kit](https://www.devicemart.co.kr/goods/view?no=1077361).

### Inferences
- Budget planning must assume Pi 5 4GB/8GB ≈ $100–150+ and Orin Nano Super $399 (≈ 56만원); Pi 4 / Pi Zero 2 W / ESP32 / Pico are the cost-stable entry boards. For a Korean learner, ESP32/Pico boards and sensors are readily available at 디바이스마트/엘레파츠 (domestic availability of specific items not verified here).
- Recommended free fundamentals channels Paul McWhorter (Arduino/Pi/Jetson lessons), DroneBot Workshop, and Elegoo's bundled tutorials were not surfaced by searches (queries targeted micro-ROS); their existence is training knowledge, not cited here — treat as unverified recommendations.
- LD19/LD06 family (and successor D500) remains the cheapest ROS 2-compatible 2D LiDAR and is what TurtleBot3 LDS-02 is based on; RPLIDAR A1 is the better-documented alternative at ~$99.

### Gaps
- No 2026 prices for RealSense D435/D435i, ESP32 dev boards, or Pico in KRW/USD were retrieved.
- Paul McWhorter / DroneBot Workshop / Elegoo tutorial URLs and current-ness were not verified.
- Korean retailer listings for LD19, RPLIDAR A1, OAK-D not found.

## Key Question 5 — Project-based curricula and competitions: which offer open curricula?

### Takeaway
Fully open curricula: Duckietown (edX MOOC + instructor manual + LX modules), Stanford CS123/Pupper v3 (all labs/lectures on readthedocs), F1TENTH/RoboRacer (open build docs; car ≈ $2,100–$3,000 on Jetson Orin Nano), and the ROBOTIS TurtleBot3 e-Manual. Competitions active in Korea in 2026: RoboCup 2026 Incheon (Jun 30–Jul 6; first time in Korea), RoboCup Korea Open (Feb 6–8, PyeongChang), VEX Korea nationals (Jan–Mar), FIRST Global Challenge 2026 Incheon (Oct 7–10), 국제로봇콘테스트 21회 (operator tender Jun 2026; rules not retrieved), 전국학생로봇경진대회 (구로구), 2026 로보틱스 작품공모전 (과기정통부), WRO 2026 season.

### Cited Findings
- **F1TENTH / RoboRacer**: official build docs (chassis Traxxas Slash 4x4 Premium, compute Jetson Xavier NX; TX2 deprecated; Master BOM in Google Sheet; last updated Jul 1, 2026) — [F1TENTH BOM](https://f1tenth.readthedocs.io/en/main/getting_started/build_car/bom.html), [build index](https://f1tenth-doc.readthedocs.io/en/latest/getting_started/build_car/index.html); UCSB course manuals estimate ~$2,100 total with Orin Nano dev kit $500, LiDAR $200–600 — [UCSB 2025-26](https://courses.ece.ucsb.edu/ECE188/188_F25Ilan/Projects%20Offered/F1TENTH_2025-26.pdf); UCSB capstone sheet (May 15, 2026) totals $3,022.29 with Orin Nano Super at $249 (pre-hike) — [UCSB capstone](https://capstone.engineering.ucsb.edu/sites/default/files/2026-06/F1tenth1centauri.pdf); course repo — [mlab-upenn/f1tenthpublic](https://www.github.com/mlab-upenn/f1tenthpublic); TU Wien F1TENTH course — [tuwien](https://tuwien.at/inf/f1tenth/?p=195).
- **Duckietown**: free edX MOOC + instructor manual sample curricula (see §1) — [MOOC](https://duckietown.com/mooc/), [instructor manual](https://docs.duckietown.com/ente/instructor-manual/curricula/mooc/index.html).
- **Stanford CS123 / Pupper v3**: open labs and lectures (see §3) — [CS123](https://cs123-stanford.readthedocs.io/en/latest/), [Pupper v3 course](https://pupper-v3-documentation.readthedocs.io/en/latest/course/course.html).
- **RoboCup 2026 Incheon**: Jun 30–Jul 6, 2026, Songdo Convensia; first RoboCup hosted in Korea — [RoboCup event](https://robocup.org/events/80), [RoboCup news](https://robocup.org/news/190), [2026.robocup.org](https://2026.robocup.org/); Korea Herald coverage — [Korea Herald](https://www.koreaherald.com/article/10797456); WEROB educational robotics workshop at RoboCup 2026 — [WEROB](https://2026.robocup.org/werob/). RoboCupJunior 2026 info — [junior.robocup.org](https://junior.robocup.org/?p=7309). RoboCup South Korea Open 2026: Feb 6–8, Alpensia, PyeongChang — [RoboCup event 78](https://www.robocup.org/events/78).
- **VEX Korea**: V5RC HS Korea National Tournament Feb 20–21, 2026 — [RobotEvents](https://events.vex.com/robot-competitions/vex-robotics-competition/RE-V5RC-25-0420.html); VEX IQ MS nationals Jan 31–Feb 1, 2026 at KIS Jeju — [RobotEvents](https://events.vex.com/RE-VIQRC-25-0677.html).
- **FIRST Global Challenge 2026** hosted in Incheon, Oct 7–10, 2026, 190+ national teams — [FIRST Global press release](https://first.global/press-releases/south-korea-to-host-190-national-teams-at-the-2026-first-global-challenge-robotics-premier-global-competition/), [Herald](https://biz.heraldcorp.com/article/10894691); LG sponsors Korean FGC team — [inews24](https://inews24.com/view/2013080).
- **WRO 2026 season** rules — [WRO Association](https://wro-association.org/competition/2026-season/).
- **국제로봇콘테스트 (IRC) 제21회**: 나라장터 tender for venue/operation posted 2026-06-11 (bid close 07-02), estimated 424,427,273원 — [Sankun bid listing](https://www.sankun.com/bid-info/dsuNRittU8wt5DABkLJF2oHp3H6IUdWT5hmHjrI44Ig). Competition rules/categories NOT retrieved.
- **전국학생로봇경진대회 제21회 (구로구)**: 초·중·고 대상, 로봇 창작/코딩/조종 3개 부문 — [서울신문 2026-07-09](https://m.go.seoul.co.kr/news/2026/07/09/20260709500092).
- **2026 로보틱스 작품공모전** (과기정통부 주최, 한국과학창의재단 주관): 접수 2026-10-08 ~ 11-02 — [eopla](https://eopla.net/magazines/48000).
- **부산 로봇 대회 / Robofest 국내예선** Nov 28, 2026 at BPEX — [Herald](https://biz.heraldcorp.com/article/10858475), [Asiae](https://view.asiae.co.kr/en/article/2026080710523494705).
- **한국우주항공산업협회 대학생 무인항공기 경연대회** (총상금 6,400만원, 개발비 지원; VTOL 조난자 구조 임무) — [Asiae 2026-03-25](https://view.asiae.co.kr/article/2026032509590361856).
- Korean HS robot team / industry collaboration feature (KRSA) — [HelloT](https://hellot.net/news/article.html?no=113430).

### Inferences
- Competitions with *open* curricula a self-learner can reuse: F1TENTH (course slides/labs public on GitHub/readthedocs), RoboCupJunior (public rules; Rescue/Soccer kits), Duckietown's AI Driving Olympics lineage. FIRST/VEX/WRO are closed-ecosystem (VEX V5/IQ, LEGO Spike) and K-12 team-based, less relevant for adult software developers.
- For a Korea-based adult learner the most accessible structured targets are RoboCup Korea Open (Feb), the 로보틱스 작품공모전 (Oct–Nov, project submission), and F1TENTH-style autonomous racing if a university lab is accessible.

### Gaps
- 국제로봇콘테스트 2026 official rules, categories, and schedule not found; 로봇항공기경연대회 2026 (KARI-affiliated) not found in search results.
- WRO Korea and FIRST (FRC/FTC) Korea 2026 regional schedules not found.
- Whether MIT Mini Cheetah course materials (e.g., MIT 6.1120 or similar) are public was not verified; no sources surfaced.

## Key Question 6 — Where communities recommend starting, and a realistic hardware budget ladder

### Takeaway
Community guidance (r/robotics wiki FAQ/Resources, 2026 roadmap blogs) converges on: start in simulation (ROS 2 + Gazebo), then an Arduino/ESP32-class robot, then a Pi-class ROS 2 robot, with LeRobot SO-100/101 now the canonical ~$110–$230 entry into learning-based manipulation. A defensible 2026 ladder: $50–100 (Arduino car / ESP32 + sensors), $200–350 (Pololu 3pi+ or SO-101 follower DIY, Bittle X, Duckiebot), $600–1,000 (TurtleBot3 Burger, SO-101 leader+follower assembled kits, Hiwonder MentorPi), $2,000–3,000 (TurtleBot 4 Standard, Pupper v3, F1TENTH car, ROSbot 3).

### Cited Findings
- r/robotics directs beginners to the wiki's FAQ and Resources sections, then to r/AskRobotics for questions — [The Hive Index r/robotics summary](https://thehiveindex.com/communities/r-robotics/); example "how do I get into robotics" thread — [r/robotics mirror](https://lr.eu.psf.lt/r/robotics/comments/1ey031d/how_do_i_get_into_robotics); r/AskRobotics snapshots (2026) — [sentinel snapshot 2026-04-25](https://reddit.sentinel-team.org/subreddits/AskRobotics/snapshots/2026-04-25T00%3A31%3A18.610234Z).
- 2026 roadmap: ROS 2 Kilted Kaiju as the current free industry-standard framework; simulate in Gazebo before buying; SO-100 arm + no-GPU laptop ≈ $110 to learn fundamentals — [YouWare guide](https://www.youware.com/guide/getting-started-robotics-beginner-guide); practical developer guide — [Dupple](https://dupple.com/blog/how-to-create-robots); step-by-step roadmap — [Hashnode](https://hashnode.com/posts/how-to-start-robotics-for-beginners-a-practical-step-by-step-roadmap/68fd0c745f447dae2e29969f).
- Ask HN hobbyist thread summary — [mewayz mirror](https://mewayz.com/lt/blog/ask-hn-how-to-get-started-with-robotics-as-a-hobbyist); element14 "what hardware should I start with" — [element14](https://community.element14.com/technologies/robotics/f/forum/44819/what-hardware-should-i-start-with/45739).
- HomeBrew Robotics Club (hbrobotics) is an active 2026 hobbyist list discussing low-cost ALOHA-style builds — [hbrobotics](https://groups.google.com/g/hbrobotics/c/XRpjKicK6qQ).
- Discords: LeRobot Discord (discord.com/invite/s3KuuzsPFb) — [LeRobot docs](https://huggingface.co/docs/lerobot/so101); Hands-On Robotics (Pupper) Discord discord.gg/qbmaU8NmP2 — [Pupper v3 docs](https://pupper-v3-documentation.readthedocs.io/en/latest/).
- Vendor beginner-kit roundup (vendor bias) — [ThinkRobotics](https://thinkrobotics.com/es/blogs/diy-projects/best-robotics-kits-for-beginners).

### Inferences (budget ladder, USD → approx KRW at ~1,400)
- **Tier 0 ($0)**: ROS 2 + Gazebo, Duckietown virtual Duckiebot (edX), PX4 SITL, LeRobot sim datasets.
- **Tier 1 (~$50–100 / 7–14만원)**: Elegoo Smart Car V4 ($76) or Freenove 4WD (~$45) + ESP32/Pico; teaches motors, sensors, PID, serial; no ROS.
- **Tier 2 (~$200–350 / 28–50만원)**: Pololu 3pi+ 2040 ($162) / Zumo 2040 ($195); SO-101 follower DIY ($122 + printing) or Bittle X ($255–319); Duckiebot DB21 ($299, but Jetson Nano EOL risk); micro-ROS on Pico + LD19 (~$69).
- **Tier 3 (~$600–1,000 / 85–140만원)**: TurtleBot3 Burger (~€895); SO-101 leader+follower assembled kit (~$430–500) + a camera; Hiwonder MentorPi A1 ($640); Crazyflie STEM bundle ($570–675).
- **Tier 4 (~$2,000–3,000 / 2.8–4.2M원)**: TurtleBot 4 Standard ($2,575), Pupper v3 (~$2,000), F1TENTH car ($2,100–3,000), ROSbot 3 (€2,749), myCobot 280 + Pi.
- Institutional (> $10k): Unitree Go2 EDU ($11k+), Trossen Solo AI ($11.4k), Mobile ALOHA ($32k).

### Gaps
- The r/robotics wiki page itself could not be fetched (reddit blocked), so its exact hardware list is uncited.
- No Korean-language community (e.g., 로봇 네이버 카페, 모두의연구소 robotics) starting-guide was retrieved beyond the modulabs TurtleBot note.
- All KRW values are inferred conversions; no Korean retailer prices were verified for the ladder items.
