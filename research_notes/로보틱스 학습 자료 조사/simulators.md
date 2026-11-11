# Robotics Simulation Platforms and Their Learning Materials (state as of 2026-11-11)

Scope: Webots, Gazebo (gz-sim), NVIDIA Isaac Sim / Isaac Lab, MuJoCo, PyBullet, CoppeliaSim, Genesis, Unity/Unreal, MATLAB/Simulink — suitability for a beginner-to-intermediate curriculum aimed at software developers with modest laptops, best learning materials, and practical constraints. Special depth on Webots (user already has a Webots project) and Gazebo (ROS 2 default).

Method note: facts below were taken from official docs, GitHub release/changelog pages, official forums, and course pages fetched directly; secondary blog/aggregator claims are flagged as such. Several JS-rendered sites (cyberbotics.com, webots.cloud, coppeliarobotics.com/pricing, docs.ros.org behind Anubis bot-protection) could not be fetched directly; for Webots the equivalent Markdown source on GitHub was used instead.

---

## Key Question 1 — Webots: version, license, tutorials, ROS 2 status, courses, community, limitations

### Takeaway
Webots is still at stable release R2025a (Jan/Feb 2025) with an unreleased R2025b/R2026 line being built nightly; it is Apache-2.0, cross-platform (Ubuntu 22.04/24.04/26.04, Windows 10/11, macOS 12–14), runs on modest hardware (2 GB RAM minimum, any OpenGL 3.3 GPU), has an official 8-tutorial sequence (~4 hours), a first-class Python API (Python ≥ 3.8), an apt-installable `webots_ros2` package for Jazzy/Kilted, and a free Coursera specialization (CU Boulder) built on it — making it the most beginner-friendly option in this list, at the cost of a smaller community than Gazebo and less photorealism/GPU-RL capability than Isaac.

### Cited Findings

**Version and release history**
- The GitHub releases page lists, newest first: nightly pre-release builds dated 10-11-2026, 9-11-2026, 6-11-2026; then R2025a (marked "Latest", 04 Feb); R2023b (28 Jun); R2023a (28 Nov); R2022b; R2022a; R2021b; R2021a. There is no official R2026 or R2025b release; nightly builds are from `master`, "might be unstable", and their notes reference a `changelog-r2026.md` — [GitHub releases](https://github.com/cyberbotics/webots/releases); [nightly 10-11-2026 tag](https://github.com/cyberbotics/webots/releases/tag/nightly_10_11_2026)
- The changelog in `master` dates R2025a as released January 31, 2025 and contains an undated, in-progress "R2025b" section (Ubuntu 26.04 support, Blender-style mouse navigation, `home://` paths in EXTERNPROTO, Franka Panda `baseSlot`, Windows toolchain move from MINGW64 to UCRT64, several Python API bug fixes, PBR light-intensity scaling change). Note the conflict: the nightly release note cites a "changelog-r2026.md", but `raw.githubusercontent.com/.../docs/reference/changelog-r2026.md` returned 404 and the directory listing only shows `changelog-r2025.md`; the next release's final name (R2025b vs R2026a) is therefore unconfirmed — [changelog-r2025.md (raw)](https://raw.githubusercontent.com/cyberbotics/webots/master/docs/reference/changelog-r2025.md); [docs/reference directory](https://github.com/cyberbotics/webots/tree/master/docs/reference)
- Wikipedia lists the stable release as R2025a / January 31, 2025 — [Wikipedia: Webots](https://en.wikipedia.org/wiki/Webots)
- R2025a headline: "Some new robot model, new demos, improved ROS 2 support, and many other improvements"; the R2025a changelog adds a Clearpath Heron USV model, renames the web scene format X3D→W3D, removes Lua as a PROTO scripting language, removes ROS 1 support, drops Ubuntu 20.04 and macOS 11, adds Ubuntu 24.04 and macOS 14 — [GitHub releases](https://github.com/cyberbotics/webots/releases); [changelog-r2025.md](https://raw.githubusercontent.com/cyberbotics/webots/master/docs/reference/changelog-r2025.md)
- Secondary coverage: "Cyberbotics Ships Webots R2025a With Marine Robots and Drops ROS 1" — [AlphaSignal](https://alphasignal.ai/news/cyberbotics-ships-webots-r2025a-with-marine-robots-and-drops-ros-1)

**License, repo, community size**
- License Apache-2.0; ~4.8k stars, ~2.1k forks on GitHub; README links Discord (https://discordapp.com/invite/nTWbN9m), User Guide/Reference Manual, Tutorials and Wiki — [cyberbotics/webots](https://github.com/cyberbotics/webots)
- Gazebo has been open source since 2002 whereas Webots was open-sourced in 2018 (gbiggs, OSRF, March 2025) — [Discourse thread](https://discourse.openrobotics.org/t/why-is-gazebo-very-famous-in-the-ros-community-what-about-webots/42459)
- Community channels: Cyberbotics says the community is mainly active on Discord for quick answers, GitHub for issues, and Stack Overflow (`webots` tag) for general questions; there is a `community-projects` repo of user-contributed PROTOs/controllers/worlds and an `awesome-webots` list — [cyberbotics/community-projects (via ecosyste.ms)](https://awesome.ecosyste.ms/projects/github.com%2Fcyberbotics%2Fcommunity-projects); [cyberbotics/awesome-webots](https://github.com/cyberbotics/awesome-webots)

**System requirements and OS support**
- Minimum 2 GHz dual-core CPU (quad-core recommended), minimum 2 GB RAM, NVIDIA or AMD GPU with OpenGL 3.3+ and ≥ 512 MB graphics memory. Intel integrated graphics "not recommended" because they often lack good OpenGL support (may cause rendering problems and crashes); on Linux only NVIDIA cards are recommended; recent Apple computers' graphics reported to work well. OS: Linux x86-64 only, Ubuntu 22.04/24.04/26.04 guaranteed ("doesn't run on Ubuntu earlier than 22.04"), Windows 10/11 64-bit, macOS 12/13/14. No mention of WSL, VMs or Apple Silicon — [system-requirements.md (raw)](https://raw.githubusercontent.com/cyberbotics/webots/master/docs/guide/system-requirements.md) (rendered at https://cyberbotics.com/doc/guide/system-requirements)

**Official tutorials (User Guide)**
- Tutorials 1–8 with stated times: (1) Your First Simulation in Webots, 30 min; (2) Modification of the Environment, 30 min; (3) Appearance, 20 min; (4) More about Controllers, 30 min; (5) Compound Solid and Physics Attributes, 15 min; (6) 4-Wheels Robot, 60 min; (7) Your First PROTO, 20 min; (8) The Supervisor, 30 min; plus "Going Further". Total ≈ 235 min. The tutorial page's examples are written in C (a language tab switches to Python/C++/Java/MATLAB on the website); prerequisites: programming background; solutions ship in `WEBOTS_HOME/projects/samples/tutorials` — [tutorials.md (raw)](https://raw.githubusercontent.com/cyberbotics/webots/master/docs/guide/tutorials.md) (rendered at https://cyberbotics.com/doc/guide/tutorials)
- Python API: supports Python ≥ 3.8; API in the `controller` module (~25 classes, ~200 functions, names mirror the C++ API); interpreter chosen via PATH, Preferences, per-controller `runtime.ini`, or shebang (Linux/macOS only); pip only needed for third-party libs like OpenCV — [using-python.md (raw)](https://raw.githubusercontent.com/cyberbotics/webots/master/docs/guide/using-python.md) (rendered at https://cyberbotics.com/doc/guide/using-python)
- MathWorks lists Webots as a connected product (Webots can run MATLAB controllers) — [MathWorks product connection page](https://au.mathworks.com/products/connections/product_detail/webots.html)

**webots_ros2 (ROS 2 integration)**
- `webots_ros2` is released as a ROS 2 Jazzy binary package, version 2025.0.1; install is `sudo apt-get install ros-jazzy-webots-ros2` — [docs.ros.org webots_ros2 (Jazzy)](https://docs.ros.org/en/jazzy/p/webots_ros2/); [ROS 2 Jazzy Webots install tutorial](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Simulators/Webots/Installation-Ubuntu.html)
- The `webots_ros2_driver` 2025.0.1 changelog (2025-07-14) "Adds ROS Kilted Kaiju support" — [webots_ros2_driver changelog](https://docs.ros.org/en/jazzy/p/webots_ros2_driver/__CHANGELOG.html)
- The ROS 2 documentation carries an official "Simulation Webots" tutorial section even for the newest distro (Lyrical) — [ROS 2 docs (Lyrical) Webots tutorials](https://docs.ros.org/en/lyrical/Tutorials/Advanced/Simulators/Webots/Simulation-Webots.html)
- Repo: ~549 stars, 194 forks, Apache-2.0; packages `webots_ros2_driver`, `webots_ros2_control`, `webots_ros2_msgs`, `webots_ros2_importer` plus robot packages (e-puck, Mavic, Tesla, TIAGo, TurtleBot, Universal Robots, Husarion, Crazyflie) — [cyberbotics/webots_ros2](https://github.com/cyberbotics/webots_ros2)
- Wiki "Getting Started": ROS docs cover Linux, Windows and macOS; automatic Webots download is available only on Linux and Windows; source build via `git clone --recurse-submodules` + `rosdep` + `colcon`. Tutorials: Ros2Supervisor node, URDF/Xacro import, custom plugins (C++/Python), custom packages/robots, simulation reset. Examples: E-puck "for ROS 2 beginners", TIAGo, TurtleBot3 Burger (Nav2 and SLAM guides), Universal Robots arm, Tesla Model 3, DJI Mavic 2 Pro — [webots_ros2 wiki Getting Started](https://github.com/cyberbotics/webots_ros2/wiki/Getting-Started)
- "webots_ros2 package downloads Webots automatically on first run, so no separate PPA setup is needed" (lukicdarkoo, Cyberbotics contributor, March 2025); counter-point from peci1: Gazebo ships in the ROS repository while Webots needs another source — [Discourse thread](https://discourse.openrobotics.org/t/why-is-gazebo-very-famous-in-the-ros-community-what-about-webots/42459)

**Courses, MOOCs and textbooks built on Webots**
- CU Boulder CSCI 3302 "Introduction to Robotics" (Correll lab) uses Webots; content, quizzes, peer-reviewed assignments and final projects are run via Coursera as the "Introduction to Robotics in Webots" specialization; three 5-week parts (page dated 2024-08-17) — [CU Boulder course page](https://www.colorado.edu/lab/correll/node/127)
- Coursera specialization "Introduction to Robotics with Webots" (University of Colorado Boulder, instructor Nikolaus Correll), three courses, first = "Basic Robotic Behaviors and Odometry", last = "Robotic Path Planning and Task Execution"; learners program in Python in Webots with peer-graded work; can count toward CU's online MS-CS/MS-AI; enrollment figures across pages range ≈4.5k–9.4k — [Coursera specialization](https://www.coursera.org/specializations/introduction-robotics-webots); [CU Boulder ALI page](https://www.colorado.edu/ali/introduction-robotics-webots-specialization); [Course 1](https://www.coursera.org/learn/basic-robotic-behaviors-and-odometry)
- Companion open textbook: "Introduction to Autonomous Robots: Mechanisms, Sensors, Actuators, and Algorithms" (Correll, Hayes, Heckman, Roncone; MIT Press 1st ed. 2022; source CC-BY-NC-ND) — the site does not itself mention Webots — [introduction-to-autonomous-robots.github.io](https://introduction-to-autonomous-robots.github.io/)
- Ruhr-University Bochum "Autonomous Robotics" (WT 2020) required students to run Webots on their own computers — [RUB course page](https://www.ini.rub.de/teaching/courses/autonomous_robotics_winter_term_2020/)
- ASEE paper comparing platform configurations "within ROS2, Raspberry Pi and Webots" for a robotics course — [ASEE PEER](https://peer.asee.org/a-comparison-of-platform-configurations-for-robotics-development-within-ros2-raspberry-pi-and-webots.pdf)
- "Cyberbotics' Robot Curriculum" is a Wikibook targeting Webots and the e-puck robot (older material) — [Wikipedia: Webots](https://en.wikipedia.org/wiki/Webots); [robotcurriculum on SourceForge](https://sourceforge.net/projects/robotcurriculum/)
- EPFL MICRO-452 "Basics of Mobile Robotics" (Mondada, 4 credits, 14 weeks, Thymio-based project) — student repos show Thymio + Python/Aseba; no confirmation that the course uses Webots (a Webots Thymio II model exists) — [EPFL coursebook](https://edu.epfl.ch/studyplan/en/master/microengineering/coursebook/basics-of-mobile-robotics-MICRO-452); [student project repo](https://github.com/mbiselx/MobRob)
- A 2017 RoboCup Symposium paper describes a MOOC on Autonomous Mobile Robots delivered through The Construct's ROS Development Studio, which supported both Gazebo and Webots in the cloud — [RoboCup 2017 paper](https://2017.robocup.org/file/symposium/RoboCup_Symposium_2017_paper_7.pdf)

**webots.cloud and robotbenchmark**
- webots.cloud (repo `cyberbotics/webots-cloud`, Apache-2.0, ~3,573 commits) hosts Scenes (static 3D), Animations (recordings), Demos (interactive simulations run in the cloud) and Competitions (scored challenges). Demos/competitions live in GitHub repos created from `webots-demo-template` with a `webots.yaml`; the Dockerfile base image sets the Webots version; no pricing is mentioned — [cyberbotics/webots-cloud](https://github.com/cyberbotics/webots-cloud)
- The webots-cloud wiki says a developer can register a GitHub repo so the simulation runs from a browser, and that webots.cloud "will automatically detect the markdown files for the course content and display them to browse the course and run the corresponding simulations" — [webots-cloud wiki Use Cases](https://github.com/cyberbotics/webots-cloud/wiki/Use-Cases)
- Competitions (e.g., Humanoid Robot Wrestling) are evaluated on Cyberbotics servers when competitors push to GitHub; organizer tooling `competition-template` (last push Sept 2023) and `competition-record-action` — [arXiv survey of AI competition platforms](https://arxiv.org/pdf/2312.05185); [competition-template (ecosyste.ms)](https://awesome.ecosyste.ms/projects/github.com%2Fcyberbotics%2Fcompetition-template)
- robotbenchmark.net was launched by Cyberbotics in 2017 as free browser-based robotics challenges "from middle school to PhD" — [Robohub 2017](https://robohub.org/robotbenchmark-lets-you-program-simulated-robots-from-your-browser/). WARNING: on 2026-11-11 a fetch of https://robotbenchmark.net/ returned a page of Indonesian gambling spam ("togel", "slot") unrelated to robotics, strongly suggesting the domain has lapsed or been hijacked; do not link learners to it — [robotbenchmark.net as fetched](https://robotbenchmark.net/)

**Known limitations vs Gazebo / Isaac (community views, March 2025 thread)**
- Pro-Webots: "a lot more beginner-friendly", more polished UI, more systematic documentation (rxduty); Gazebo's XML-like definition language was off-putting and Webots' live view made prototyping easier (thinkalicious); Isaac Sim's hardware requirements too steep (Anupam_Das) — [Discourse thread](https://discourse.openrobotics.org/t/why-is-gazebo-very-famous-in-the-ros-community-what-about-webots/42459)
- Against Webots: extra package source step (peci1); dated docs in one university course (thinkalicious); Gazebo has the most ROS-related tutorials (Anupam_Das); Gazebo lets you swap physics engines or write physics plugins (Katherine_Scott, Gazebo team) — same thread
- Comparison blogs (secondary/opinion): Webots "best for education and mobile-robot prototyping"; it ships 200+ pre-built robot models publishing ROS 2 interfaces; one source says Webots' physics is "not as advanced as Gazebo's" — [DEV Community](https://dev.to/godrift_ai/which-robot-simulator-should-you-actually-use-5gn4); [ThinkRobotics](https://thinkrobotics.com/es/blogs/learn/webots-vs-gazebo-choosing-a-robotics-simulator)
- Peer-reviewed: in a ROS 2 arm-manipulation comparison, Ignition (Gazebo) and Webots had higher stability than others, while PyBullet and CoppeliaSim used fewer resources — [arXiv 2204.06433](https://www.arxiv.org/pdf/2204.06433)

### Inferences
- For a developer with a modest laptop, Webots has the lowest hardware floor of any 3D simulator here (2 GB RAM, OpenGL 3.3); the main risk is Intel integrated graphics on Linux, so advise learners on Intel-only laptops to test early and fall back to Windows/macOS builds or software rendering.
- The official 8 tutorials (~4 h) plus the Python API page form a coherent "week 1" for a curriculum; the Coursera CU Boulder specialization is the most complete third-party Webots course and is a ready-made model for a Python-based beginner track.
- Since `webots_ros2` is an apt package for Jazzy and supports Kilted, Webots can also be used as the ROS 2 simulator in an intermediate track, although tutorial volume on the web is much larger for Gazebo.
- The stable release is now ~21 months old (R2025a); frequent nightlies mean a new release is imminent but curriculum should pin R2025a.

### Gaps
- Could not fetch cyberbotics.com pages directly (JS-rendered); facts come from the Markdown sources on GitHub, which are identical content.
- No official statement found on Apple Silicon/WSL support for Webots.
- The exact name/date of the next release (R2025b vs R2026a) is unconfirmed (conflicting references in the repo).
- No official statement on the current operational status of robotbenchmark.net beyond the suspicious page content.
- No numbers found for Discord membership.

---

## Key Question 2 — Gazebo (gz-sim): release lines, ROS 2 pairing, tutorials, migration from Classic

### Takeaway
Gazebo's current LTS lines are Harmonic (Sep 2023 → May 2029, pairs with ROS 2 Jazzy) and Jetty (Sep 2025 → May 2031, pairs with ROS 2 Lyrical/Rolling); Ionic (Sep 2024, pairs with Kilted) reaches EOL December 2026 and the next release "M" is slated for March 2027. Gazebo is the ROS 2 default with the largest tutorial ecosystem, but beginners face version-pairing confusion, an Ogre2 renderer that needs OpenGL 3.3 and real GPU drivers, and a web full of outdated Gazebo Classic material.

### Cited Findings

**Release table (official)**
- Rotary = rolling/nightly (experimental); "M" planned Mar 2027, EOL Dec 2028; Jetty Sep 2025 → May 2031 (LTS); Ionic Sep 2024 → Dec 2026 (not LTS); Harmonic Sep 2023 → May 2029 (LTS); Garden Sep 2022 → Nov 2024 (EOL); Fortress Sep 2021 → May 2027 (LTS); Citadel Dec 2019 → Dec 2024 (EOL) — [gazebosim.org Releases](https://gazebosim.org/docs/all/releases/)
- Jetty is the "10th major release", an LTS, support "Sep, 2025 to May, 2031"; release notes mention Zenoh interoperability with ROS 2 Jazzy and that ZeroMQ was used "up until Ionic" — [Jetty release notes](https://gazebosim.org/docs/all/release_notes/); [Jetty release announcement](https://discourse.openrobotics.org/t/gazebo-jetty-released/50349)
- "Gazebo Ionic reaching end-of-life in December, 2026" alongside ROS 2 Kilted; users should move to Jetty, which is paired with ROS 2 Lyrical — [Discourse EOL notice](https://discourse.openrobotics.org/t/gazebo-ionic-reaching-end-of-life-in-december-2026/57981)

**ROS 2 pairing (official matrix)**
- Lyrical (LTS) → Jetty (recommended), Harmonic/Ionic "possible with effort", Fortress incompatible; Kilted → Ionic; Jazzy (LTS) → Harmonic; Humble (LTS) → Fortress (Harmonic possible with effort via `ros-humble-ros-gzharmonic`, "not recommended for beginners"); Rolling → Rotary. Install: `sudo apt-get install ros-${ROS_DISTRO}-ros-gz`. Starting with Jazzy, Gazebo ships from the ROS repository as vendor packages — [Installing Gazebo with ROS](https://gazebosim.org/docs/all/ros_installation); [ROS 2 Gazebo vendor packages](https://gazebosim.org/docs/all/ros2_gz_vendor_pkgs/)
- Conflict: the `ros_gz` README table lists Lyrical with Harmonic (source-only), which disagrees with the official install page pairing Lyrical→Jetty; treat the gazebosim.org page as authoritative — [gazebosim/ros_gz](https://github.com/gazebosim/ros_gz)
- Jetty support-end conflict: release notes say May 2031 while the Discourse announcement said September 2030 — [release notes](https://gazebosim.org/docs/all/release_notes/); [announcement](https://discourse.openrobotics.org/t/gazebo-jetty-released/50349)

**Repo, license, platforms, Python**
- gz-sim: ~1.6k stars, 523 forks, Apache-2.0; CI badges for Ubuntu Noble, Homebrew (macOS) and Windows, with the note that `gz sim` does not yet work as one command on Windows (server and GUI must run in separate terminals) — [gazebosim/gz-sim](https://github.com/gazebosim/gz-sim)
- Python bindings (v10 = Jetty docs): "For now, we provide a `TestFixture` class" to load a world, step it, and register pre/update/post-update callbacks; Python systems can be loaded through `PythonSystemLoader`; `gz.math` and `gz.sim` `Model`/`Link` helpers; requires adding the install `lib/python` to `PYTHONPATH` — [Gazebo Python interfaces](https://gazebosim.org/api/sim/10/python_interfaces.html)
- Only "a handful of people make regular contributions to the core Gazebo source code" and there is "no turn-key reinforcement learning example" (Katherine Scott, Gazebo team, March 2025) — [Discourse thread](https://discourse.openrobotics.org/t/why-is-gazebo-very-famous-in-the-ros-community-what-about-webots/42459)

**Hardware / GPU constraints**
- Ogre2 render engine errors with "OpenGL 3.3 is not supported. Please update your graphics card drivers"; check `~/.ignition/rendering/ogre2.log` — [Gazebo Fortress troubleshooting](https://gazebosim.org/docs/fortress/troubleshooting)
- Harmonic runs on WSLg with GPU support and is reported "much faster (responsive)" than in VMware; another user on WSL2 got a black GUI with Ogre2, with a Gazebo developer noting the D3D12 driver may not support features needed to emulate OpenGL for ogre2 — [Discourse WSLg thread](https://discourse.openrobotics.org/t/wslg-with-gpu-support-available-on-latest-version-of-gazebo-garden-and-harmonic/48128)
- Headless rendering requires OGRE2 and `--headless-rendering` on Harmonic — [community headless guide](https://niklashargarter.github.io/gazebo-ros-setup/headless-rendering)
- A Harmonic user with a hybrid NVIDIA/AMD laptop on Ubuntu 24.04 reported freezes when running Gazebo and RViz together — [The Construct help thread](https://get-help.theconstruct.ai/t/gazebo-sim-harmonic-graphics/36993)
- No official minimum-hardware page for Harmonic/Jetty was found (see Gaps).

**Tutorials and courses**
- Official Jetty tutorials ("Simulation Tutorials"): Building your own robot, Moving the robot, SDF worlds, Sensors, Actors, Understanding the GUI, Manipulating Models, Model Insertion from Fuel, Keyboard Shortcuts, Spawn URDF; ROS 2 integration under How-to Guides: ROS 2 overview, Launch Gazebo from ROS 2, Use ROS 2 to interact with Gazebo — [Gazebo Jetty tutorials](https://gazebosim.org/docs/jetty/tutorials/); [Harmonic tutorials](https://gazebosim.org/docs/harmonic/tutorials/)
- The ROS 2 docs carry a "Setting up a robot simulation (Gazebo)" tutorial — [ROS 2 Jazzy Gazebo tutorial](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html) (site blocked automated fetch; title from search index)
- Articulated Robotics (Josh Newans): free site with series "Getting Ready to Build a ROS Robot", "Build a Mobile Robot with ROS" (Project Overview + Concept Design 2 items, Hardware 4 items, Applications 7 items), "Docker for Robotics", "Coordinate Transforms for Robotics", "Geometry Tips"; Discourse forum and YouTube channel; Patreon-supported. The site pages fetched did not state which ROS 2/Gazebo version the series targets — [articulatedrobotics.xyz tutorials](https://articulatedrobotics.xyz/tutorials); [Build a Mobile Robot series](https://articulatedrobotics.xyz/category/build-a-mobile-robot-with-ros); [YouTube](https://www.youtube.com/c/ArticulatedRobotics)
- A community port "articubot_one" rebuilds the Articulated Robotics diff-drive robot for ROS 2 Jazzy + Gazebo Harmonic using `ros_gz` (`sudo apt install ros-jazzy-ros-gz ...`) — [articubot_one (Jazzy/Harmonic)](https://github.com/samstromer1990-crypto/articubot_one)
- MOGI-ROS university course materials "Week 3-4 Gazebo basics: Introduction to URDF and Gazebo Harmonic with ROS2 Jazzy" (Ubuntu 24.04) — [MOGI-ROS repo](https://github.com/MOGI-ROS/Week-3-4-Gazebo-basics)
- The Construct offers "Introduction to Gazebo Sim with ROS2" and "Mastering Gazebo Simulator" on paid plans — [The Construct pricing](https://www.theconstruct.ai/pricing/)
- UMD ENPM605 (Spring 2026) course docs note "Gazebo Harmonic ... cannot coexist with Gazebo Classic" — [ENPM605 simulation page](https://enpm605-spring-2026-docs.readthedocs.io/en/latest/simulation/simulation.html)

**Migration from Gazebo Classic**
- Official position: "ROS 2 Jazzy will target Gazebo Harmonic, and there will be no official Gazebo Classic support"; recommended path is latest LTS of both — [Gazebo Classic EOL & Jazzy](https://discourse.openrobotics.org/t/gazebo-classic-end-of-life-ros-2-jazzy/36239); [Gazebo Classic End-of-Life](https://discourse.openrobotics.org/t/gazebo-classic-end-of-life/48748)
- Official migration guide walks through converting the TurtleBot3 simulation from `gazebo_ros_pkgs` to `ros_gz` (example targets Fortress; "concepts should work with newer versions") — [Migrating ROS 2 packages that use Gazebo Classic](https://gazebosim.org/docs/all/migrating_gazebo_classic_ros2_packages/); [Migration guide & office hours](https://discourse.openrobotics.org/t/gazebo-migration-guide-office-hours/48770)
- Community warning: "almost every guide you find on the internet will be for Gazebo Classic" — [UNL Lunabotics docs](https://unl-lunabotics.github.io/docs/Technical/ROS2/Jazzy/URDF/Gazebo-URDF.html)
- Nav2 published a "new modern Gazebo getting started guide" — [Discourse](https://discourse.openrobotics.org/t/nav2-new-modern-gazebo-getting-started-guide/41803)

### Inferences
- For a 2026–2027 curriculum, the safe pairing is ROS 2 Jazzy + Gazebo Harmonic (both LTS until 2029) on Ubuntu 24.04; Lyrical + Jetty is the newer LTS pair but has less third-party tutorial coverage yet. Avoid Kilted + Ionic (EOL Dec 2026).
- Gazebo should be positioned as the "intermediate / ROS 2 integration" simulator rather than the first contact, because of the install/pairing complexity and GPU driver sensitivity; a browser-based environment (The Construct) or a Docker/WSLg setup mitigates this for modest laptops.
- Any tutorial or video must be checked for "Classic vs new Gazebo" before being added to the curriculum.

### Gaps
- No official hardware-requirements page for Harmonic/Jetty found; GPU guidance is anecdotal.
- docs.ros.org pages could not be fetched (Anubis bot protection); tutorial titles come from search indexes.
- Articulated Robotics' current ROS 2/Gazebo target version could not be confirmed from its site.

---

## Key Question 3 — NVIDIA Isaac Sim / Isaac Lab: 2026 versions, hardware, free tiers, courses, beginner suitability

### Takeaway
In 2026 Isaac Sim moved to 6.x (6.0 GA June 8, 2026; 6.2 GA Oct 22, 2026) and Isaac Lab reached 3.0 GA (Oct 20–29, 2026) with the new Newton physics backend (built on MuJoCo-Warp) and a "kit-less" mode that can run without Isaac Sim; both are free (Isaac Sim Apache-2.0 + NVIDIA additional-materials license; Isaac Lab BSD-3), but Isaac Sim's minimum spec (RTX 4080 / 16 GB VRAM, 32 GB RAM, Ubuntu 22.04/24.04 or Windows 11) rules it out for modest laptops; it is an advanced/optional track with good free NVIDIA DLI intro courses and cloud (Brev/AWS) escape hatches.

### Cited Findings

**Versions and dates**
- Isaac Sim 5.0 + Isaac Lab 2.2 GA was announced at SIGGRAPH 2025 (Aug 2025) — [NVIDIA blog](https://developer.nvidia.com/blog/announcing-general-availability-for-nvidia-isaac-sim-5-0-and-nvidia-isaac-lab-2-2)
- Isaac Sim 6.0 "now generally available" posted June 8, 2026 (forum, rthaker): core Experimental API (motion generation, actuators, deformables across physics backends), Newton authoring (URDF/MJCF importers output backend-switchable assets; only Newton's MJWarp solver supported), Isaac Sim MCP server for Claude Code/Cursor, unified actuators shared with Isaac Lab, browser streaming client (Chromium), native Windows ROS 2 via Pixi; Isaac Sim 4.5 docs to be removed with 6.1 — [Isaac Sim 6.0 GA forum post](https://forums.developer.nvidia.com/t/isaac-sim-6-0-general-availability/372621); [6.0.0 release notes](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/overview/release_notes.html)
- Isaac Sim 6.2 GA posted Oct 22, 2026: "primarily a bug-fix release" supporting the Isaac Lab 3.0 GA launch; Kit SDK 110.4, Newton 1.6.1, MuJoCo/MuJoCo-Warp 3.12.0; Ubuntu 22.04 still supported but removal planned; Cortex removed — [Isaac Sim 6.2 GA forum post](https://forums.developer.nvidia.com/t/isaac-sim-6-2-general-availability/386512); [6.2.0 release notes](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/overview/release_notes.html)
- Isaac Lab GitHub releases: v3.0.0 (20 Oct, pairs with Isaac Sim 6.2), v3.0.0-EA (16 Sep, Isaac Sim 6.1), v3.0.0-beta2.patch1 (2 Jul, 6.0.1), beta2 (17 Jun, 6.0), beta (17 Mar, 6.0). v3.0.0 notes: multiple physics backends (Newton with MuJoCo-Warp/VBD/MPM; OVPhysX, OVRTX), "Isaac Sim is now optional", kit-less execution, Warp-native `ProxyArray` zero-copy to PyTorch, unified `isaaclab` CLI, 17 interactive Newton demos in the browser; stack Python 3.12, PyTorch 2.11 + CUDA 13.0, Warp 1.17, RSL-RL 5.5.1 — [IsaacLab releases](https://github.com/isaac-sim/IsaacLab/releases); [Isaac Lab 3.0 release notes](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/refs/release_notes.html)
- "NVIDIA Isaac Lab 3.0 Now Available" forum post dated Oct 29, 2026 — [forum post](https://forums.developer.nvidia.com/t/nvidia-isaac-lab-3-0-now-available/387360); a secondary site claims the GA was announced at GTC Berlin on 21 Oct 2026 (unverified) — [AI Tools Review](https://aitoolsreview.co.uk/insights/nvidia-isaac-lab-3-0)
- Isaac Lab v2.3.x supported Isaac Sim 4.5/5.0/5.1; Isaac Sim 5.x required Python 3.11 — [Isaac Lab 2.3 local installation](https://isaac-sim.github.io/IsaacLab/v2.3.0/source/setup/installation/index.html)
- The developer.nvidia.com product page still references 5.1.0 docs/download links (lagging the 6.x docs) — [NVIDIA Isaac Sim page](https://developer.nvidia.com/isaac/sim)

**Hardware requirements (Isaac Sim "latest" docs, i.e., 6.x)**
- x86_64: OS Ubuntu 22.04/24.04 or Windows 11; CPU min i7 7th-gen / Ryzen 5 (4 cores), RAM min 32 GB (good/ideal 64 GB), storage min 50 GB SSD; GPU min GeForce RTX 4080 (16 GB VRAM), good RTX 5080 (16 GB), ideal RTX PRO 6000 Blackwell (48 GB); driver Linux 595.58.03 / Windows 595.97. Windows 10 not supported; Ubuntu 22.04 deprecated; aarch64 only on DGX Spark; GPUs without RT cores (A100/H100) not supported; <16 GB VRAM "may struggle with complex scenes"; internet required for assets — [Isaac Sim requirements (latest)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html); [5.1.0 requirements](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html)

**Licensing / free tiers**
- Isaac Sim "is free to use, licensed as open source under Apache 2.0 and available on GitHub", used together with the "NVIDIA Isaac Sim Additional Software and Materials License"; redistributing Omniverse Kit inside your own product needs an Omniverse Enterprise subscription; download via GitHub, NGC container, or the docs download page; cloud via Brev (one-click GPU instances) and AWS Marketplace (pay EC2 fees) — [NVIDIA Isaac Sim page](https://developer.nvidia.com/isaac/sim)
- Isaac Lab is BSD-3-Clause — [Isaac Lab license page](https://isaac-sim.github.io/IsaacLab/v2.2.0/source/refs/license.html)
- Isaac Launchable lets you run Isaac Lab/Isaac Sim in the cloud with no local install (search snippet; NVIDIA) — [NVIDIA Isaac Sim page](https://developer.nvidia.com/isaac/sim)

**Official learning materials**
- Free DLI self-paced beginner course (2–3 h): build a simple robot, apply physics, integrate sensors, troubleshoot — [DLI course S-OV-27](https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-OV-27+V1); [forum announcement](https://forums.developer.nvidia.com/t/free-dli-mini-self-paced-course-assemble-a-simple-robot-in-nvidia-isaac-sim/230566)
- NVIDIA Robotics learning path (free intro courses: basic robot simulation, ROS 2 integration, synthetic data generation; Isaac Lab intermediate course ~3–4 h) — [NVIDIA robotics learning path](https://www.nvidia.com/en-us/learn/learning-path/robotics/); [Physical AI Learning hub](https://docs.nvidia.com/learning/physical-ai/); [Accelerating Robot Learning with Isaac Lab and Newton](https://docs.nvidia.com/learning/physical-ai/getting-started-with-newton/latest/index.html)
- Isaac Sim Office Hours livestreams and the Isaac Sim forum — [YouTube playlist](https://www.youtube.com/watch?v=ybtJxQbj2NE&list=PL3jK4xNnlCVewIu3MAcrP3HbvVUmKWNpS); [forum](https://forums.developer.nvidia.com/c/omniverse/simulation/69)
- A user reported that exercises in an older paid DLI "Introduction to Robotics Simulation" course "were not working anymore" — [forum thread](https://forums.developer.nvidia.com/t/introduction-to-robotics-simulation-course/269001)
- Opinion sources rate Isaac Lab "the current leader for GPU-parallelized robot RL" and Isaac Sim preferred for photorealism/perception — [roboticscenter.ai](https://www.roboticscenter.ai/rl-environments/best-2026/); [DEV Community](https://dev.to/godrift_ai/which-robot-simulator-should-you-actually-use-5gn4)

### Inferences
- Isaac is not viable as a mandatory beginner tool: the 16 GB-VRAM RTX floor and 32 GB RAM exclude most laptops; put it in an optional "advanced / RL at scale" module and point learners to Brev/AWS or Isaac Launchable if they want to try it.
- The rapid 2026 cadence (4.5 → 5.x → 6.0 → 6.2; Isaac Lab 2.x → 3.0 with breaking changes) means third-party tutorials go stale within months; curriculum should rely on NVIDIA's own DLI courses and docs.
- Isaac Lab 3.0's Newton backend (built on MuJoCo-Warp) and kit-less mode signal convergence with MuJoCo; a MuJoCo-first track is the better on-ramp to Isaac Lab than Isaac Sim itself.

### Gaps
- Exact Isaac Lab 3.0 GA date is ambiguous (GitHub tag 20 Oct; forum 29 Oct; third-party 21 Oct).
- Hardware requirements for kit-less Isaac Lab (Newton-only) were not stated on the pages fetched.
- Pricing/free credits for Brev or Isaac Launchable not found.

---

## Key Question 4 — MuJoCo: free since 2022, 3.x → 4.0, MJX/Warp, tutorials, Menagerie, course use

### Takeaway
MuJoCo (Google DeepMind, Apache-2.0) is in very active development — 3.x point releases roughly every 2–3 weeks through 2026, MuJoCo Warp officially released in 3.5.0 (Feb 2026), and MuJoCo 4.0.0 on Nov 6, 2026 (split `mujoco-core`/`mujoco-studio`/`mujoco` pip packages, Python 3.10 dropped, new Studio viewer with browser streaming). It runs on CPU with `pip install mujoco`, has first-class Colab tutorials and a zero-install browser viewer (live.mujoco.org), ~71 curated robot models in Menagerie, and underpins much academic robot-learning teaching — but it is a physics engine plus viewer, not a full robot/sensor/ROS environment.

### Cited Findings
- MuJoCo 3.0.0 was released Oct 2023; MuJoCo 3 described as "a result of unified efforts at Google" (free/open-source since DeepMind acquired it in 2021–2022) — [MuJoCo 3.0.0 release](https://github.com/google-deepmind/mujoco/releases/tag/3.0.0); [The Robot Report](https://www.therobotreport.com/mujoco-3-simulator-a-result-of-unified-efforts-at-google/)
- Latest releases: 4.0.0 (Nov 6, 2026), 3.17.0 (Oct 22, 2026), 3.16.0 (Oct 14, 2026), 3.15.0 (Oct 5, 2026), 3.14.0 (Sep 22, 2026) — [MuJoCo releases](https://github.com/google-deepmind/mujoco/releases)
- 4.0.0 changelog: Python distribution split into `mujoco-core` (bindings + C lib, numpy only), `mujoco-studio` (Studio + Filament renderer), `mujoco` (both); upgrading needs uninstall/force-reinstall; Python 3.10 support removed; Studio docs for web and native viewers; new model-tuning guide; bundled manual and "agent skills" in the Python package; new speculative contacts and elasto-plasticity; MuJoCo Warp still requires `solver="CG"` for flex-on-articulated models; unreleased: Studio web viewer on Windows via `mujoco-studio-wasm` — [MuJoCo changelog](https://mujoco.readthedocs.io/en/latest/changelog.html)
- 3.17.0 added a `mujoco.batch` module (thread-pool batched rollouts); 3.16.0 added Bazel builds and `savecompiled`/`savecanonical` XML options — same changelog
- 3.5.0 (Feb 12, 2026): "MuJoCo Warp is now officially released"; 3.6.0 (Mar 10, 2026) batch rendering for MJX-Warp; 3.7.0 (Apr 14, 2026) native flex collisions in Warp — [3.5.0 changelog](https://mujoco.readthedocs.io/en/3.5.0/_sources/changelog.rst.txt); [3.7.0 changelog](https://mujoco.readthedocs.io/en/3.7.0/changelog.html)
- MJX supports two implementations: pure JAX and Warp; MJX-Warp "resolves key performance bottlenecks exhibited in MJX-JAX around contacts and constraints" but does not support autodiff; Warp requires a CUDA device — [MJX docs](https://mujoco.readthedocs.io/en/3.9.0/mjx.html); [MJWarp docs](https://mujoco.readthedocs.io/en/latest/mjwarp/)
- Python install: `pip install mujoco` (core + Studio + OpenGL deps as of 4.0.0); `mujoco-core` for headless/RL; `mujoco-core[rendering]` adds glfw/pyopengl and `mujoco.viewer`; `mujoco[usd]` adds OpenUSD import/export; `mujoco[sysid]`; `mujoco-usd` supports Python 3.11–3.13 on Linux x86_64, Windows x86_64, macOS arm64; macOS passive viewer needs the `mjpython` launcher; no GPU requirement stated for core — [MuJoCo Python docs](https://mujoco.readthedocs.io/en/latest/python.html)
- Official Colab notebooks: Tutorial, Model editing (mjspec), Rollout, Least squares, System identification — [tutorial.ipynb](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/tutorial.ipynb); [mjspec.ipynb](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb); [rollout.ipynb](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/rollout.ipynb); [least_squares.ipynb](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/least_squares.ipynb); [sysid.ipynb](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mujoco/sysid/sysid.ipynb); an MJX tutorial notebook also exists per the repo README — [MuJoCo repo mirror listing](https://github.com/salhus/mujoco)
- MuJoCo Studio: successor to `simulate` and `mujoco.viewer`, Filament PBR + Dear ImGui; native window (`python -m mujoco.studio.viewer --model=humanoid.xml`) or web stream (`--gfx=web`, host needs "no GPU or display server"); MuJoCo Live (https://live.mujoco.org) runs entirely in the browser (drag-drop XML, or `?model=github:<org>/<repo>/<branch>/<path>`); standalone builds for macOS/Windows/Linux; Filament has software rasterizer fallbacks — [MuJoCo Studio docs](https://mujoco.readthedocs.io/en/latest/studio/index.html)
- MuJoCo Menagerie: "high-quality models ... curated by Google DeepMind"; ~71 models in 11 categories (25 arms, 11 humanoids, 11 end-effectors, 8 quadrupeds, 7 mobile manipulators, 2 drones, ...); per-model BSD/Apache/MIT licenses; `pip install mujoco-menagerie` then `mm.load('unitree_go2')`, or `uvx mujoco-menagerie view unitree_go2`, or browser viewer via live.mujoco.org; ~4.3k stars — [mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie)
- MuJoCo Playground (2025): open-source robot learning framework on MJX; full pipeline "from setup to policy training" runs in a single Colab notebook; uses Menagerie; authors include UC Berkeley researchers — [arXiv 2502.08844](https://arxiv.org/html/2502.08844v1)
- Course use: UT Austin CS391R default project uses robosuite "powered by the MuJoCo physics engine" (2022) — [CS391R project page](https://www.cs.utexas.edu/~robertom/cs391r_fall2022/project.html); UNC COMP 790-186 Robot Learning (2025) lists "simulators such as Isaac/MuJoCo/SAPIEN" as prerequisites — [COMP 790-186](https://dingmyu.github.io/course-robot_learning); CoppeliaSim integrated MuJoCo as a physics engine — [MuJoCo in CoppeliaSim](https://discourse.openrobotics.org/t/mujoco-in-coppeliasim/27568); Isaac Lab 3.0's Newton backend is built on MuJoCo-Warp — [Isaac Lab 3.0 notes](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/refs/release_notes.html)
- Opinion: MuJoCo "underlies a huge fraction of academic robot learning" — [roboticscenter.ai](https://www.roboticscenter.ai/learn/robot-simulation-software-comparison)

### Inferences
- MuJoCo is the best "no hardware barrier" option for teaching dynamics, control, and RL fundamentals: CPU-only pip install, Colab notebooks, and a browser viewer; it complements rather than replaces Webots/Gazebo because it lacks built-in robot sensor suites, world editors, and ROS 2 tooling.
- Because the 4.0.0 packaging split happened days ago (Nov 6, 2026), any curriculum material should pin `mujoco>=4.0` or explicitly `mujoco==3.17.0` and document the uninstall/reinstall step.
- MuJoCo → MJX/Warp → Isaac Lab (Newton) is a coherent progression from laptop to GPU-scale RL.

### Gaps
- Official list of supported Python versions/OS for the main `mujoco` wheel was not stated on the pages fetched (only 3.10 removal and the `mujoco-usd` range).
- No named 2025–2026 Stanford/Berkeley/CMU syllabus confirming MuJoCo assignments was found (only indirect links).

---

## Key Question 5 — PyBullet, CoppeliaSim, Genesis, ODE: status and teaching use

### Takeaway
PyBullet is effectively dormant (last PyPI release 3.2.7, Jan 30, 2025; "Inactive" per Snyk) and should be treated as legacy; CoppeliaSim (4.10, May 2025) remains a polished, cross-platform teaching simulator with a free Edu edition restricted to students/teachers (academic email required, not for companies/non-profits) and is the simulator used by Northwestern's Modern Robotics/Coursera; Genesis (now "Genesis World", Apache-2.0, 30k+ stars, v1.4.6 on Nov 8, 2026) is a fast-moving research-grade multi-physics engine with CPU and multi-GPU backends but no ROS tooling; ODE is relevant only as the physics engine inside Webots/Gazebo/CoppeliaSim, not as a standalone teaching tool.

### Cited Findings

**PyBullet / Bullet**
- Latest PyPI release 3.2.7, Jan 30, 2025; wheels for CPython 3.6–3.11 (classifiers stale: 2.7–3.8); license zlib; description "easy to use Python module for physics simulation, robotics and deep reinforcement learning" (URDF/SDF loading, FK/IK, collision, CPU renderer, OpenGL, VR) — [PyPI pybullet](https://pypi.org/project/pybullet/)
- bullet3 repo: ~14.8k stars, 9,408 commits, zlib license, recommends PyBullet (`pip3 install pybullet`), Quickstart Guide is a Google Doc — [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3); [PyBullet Quickstart Guide](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/edit)
- Snyk rates PyBullet maintenance "Inactive" (no PR activity in the past month); a community guide says it "has not been well maintained since 2023" and its RL examples rely on old Gym (opinion) — [Snyk advisor](https://dev.snyk.io/advisor/python/pybullet); [robot RL guide (opinion)](https://kushal-a.github.io/robot_RL_guide/news.html)
- Maintained community fork `pybullet-arm64` for macOS arm64 builds — [pybullet-arm64 releases feed](https://pypi.org/rss/project/pybullet-arm64/releases.xml)
- Still used downstream: panda-gym (PyBullet base class) — [panda-gym docs](https://panda-gym.readthedocs.io/en/stable/base_class/pybullet.html)

**CoppeliaSim**
- Stable release 4.10, May 14, 2025; dual-licensed (commercial or GPL); Windows/Linux/macOS; physics engines MuJoCo, Bullet, ODE, Vortex, Newton; controllers in Python or Lua scripts or C/C++ plug-ins; asynchronous controllers via ROS, remote API, ZeroMQ in C/C++, Python, Java, MATLAB; formerly V-REP (Toshiba R&D origins), now Coppelia Robotics AG, Zurich — [Wikipedia: CoppeliaSim](https://en.wikipedia.org/wiki/CoppeliaSim)
- Official blog's latest release posts are 4.9.0 (2025-01-10), 4.8.0 (2024-10-31), 4.7.0; latest post "Using gamepads with CoppeliaSim" (2025-02-28); no 2026 release post found — [CoppeliaSim blog](https://coppeliarobotics.com/blog); [4.9.0 release](https://coppeliarobotics.com/blog/article/4-9-0-released)
- Licensing: Edu edition "exclusively available for use by students, teachers and professors of schools and universities", "cannot be used commercially", not for companies/research institutions/non-profits; Pro and Lite are commercial (contact vendor); the geometric/kinematics plugin has an educational license whose "EDU" watermark must not be removed — [CoppeliaSim manual: licensing](https://manual.coppeliarobotics.com/en/licensing.htm); pricing page lists Edu as "Free for educational use only", "Academic email required" (search snippet) — [coppeliarobotics.com/pricing](https://coppeliarobotics.com/pricing)
- V4.6 brought "enhanced Python integration" — [Discourse 4.6 announcement](https://discourse.openrobotics.org/t/coppeliasim-v4-6-released-enhanced-python-integration/34559)
- Teaching: Northwestern's Modern Robotics (Lynch & Park; Coursera 6-course specialization "Modern Robotics: Mechanics, Planning, and Control") ships CoppeliaSim scenes (interactive UR5, CSV-animation UR5, interactive youBot, CSV-animation youBot; scenes dated Nov 2024); wiki recommends "the latest non-limited EDUCATIONAL version"; a student quote notes the specialization "does not teach how to use CoppeliaSim in detail" — [Northwestern CoppeliaSim intro](https://hades.mech.northwestern.edu/index.php/CoppeliaSim_Introduction); [Getting Started with CoppeliaSim](https://hades.mech.northwestern.edu/index.php/Getting_Started_with_the_CoppeliaSim_Simulator); [Coursera Modern Robotics course 1](https://www.coursera.org/learn/modernrobotics-course1); [ME 449 Robotic Manipulation](https://hades.mech.northwestern.edu/index.php/ME_449_Robotic_Manipulation)
- CTU Prague UIR course has a CoppeliaSim installation + Python API tutorial — [CTU tutorial](https://cw.fel.cvut.cz/b251/courses/uir/tutorials/vrep_tut); UC3M install guide — [UC3M](https://robots.uc3m.es/installation-guides/install-coppeliasim.html)
- Accuracy study: CoppeliaSim "ranks as the best performing simulator" for mobile-robot motion accuracy, Gazebo "not far behind" — [Glasgow eprint](https://eprints.gla.ac.uk/279056/2/279056.pdf)

**Genesis / Genesis World**
- GitHub `Genesis-Embodied-AI/genesis-world` (formerly "Genesis", began as an academic project Dec 2024): Apache-2.0, ~30.2k stars; multi-physics (rigid, FEM, MPM, PBD/SPH particles, coupling); renderers Nyx, Luisa, Pyrender; compiler "Quadrants" targets CUDA, ROCm, Apple Metal, Vulkan, x86, ARM64; assets URDF/MJCF/OBJ/GLB/USD; Python ≥ 3.12 < 3.15; blog "Genesis World 1.0" May 2026 — [Genesis GitHub](https://github.com/Genesis-Embodied-AI/Genesis); [Genesis World 1.0 blog](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward)
- PyPI `genesis-world` 1.4.6 released Nov 8, 2026; Python ≥ 3.12, < 3.15 — [PyPI genesis-world](https://pypi.org/project/genesis-world/)
- Install docs (older snapshot, Python 3.10–3.13): Linux/macOS/Windows; NVIDIA CUDA and AMD ROCm GPU on Linux/Windows; Apple Silicon Metal on macOS; Intel GPUs have no backend (use `gs.cpu`); CPU works everywhere; install PyTorch first then `pip install genesis-world`; Windows troubleshooting assumes WSL2 — [Genesis installation docs](https://genesis-world.readthedocs.io/en/latest/user_guide/overview/installation.html); [docs home](https://genesis-world.readthedocs.io/en/latest/)
- Earlier milestones: v0.2.1 (2025-01-08), v0.3.0 (2025-08-05) per repo mirrors; marketing claim of simulation "430,000x faster than reality" (press) — [mirror changelog](https://github.com/lszformal/Genesis); [The Decoder](https://the-decoder.com/genesis-speeds-up-ai-robot-training-with-simulations-430000x-faster-than-reality/)
- A critical take: "The new hyped Genesis simulator is..." (Substack commentary questioning benchmark claims) — [Substack](https://stoneztao.substack.com/p/the-new-hyped-genesis-simulator-is/comments)

**ODE**
- ODE appears only as one of CoppeliaSim's selectable engines (with MuJoCo, Bullet, Vortex, Newton) — [Wikipedia: CoppeliaSim](https://en.wikipedia.org/wiki/CoppeliaSim); Webots' physics is ODE-based (Wikipedia Webots page describes ODE as its physics engine) — [Wikipedia: Webots](https://en.wikipedia.org/wiki/Webots)

### Inferences
- PyBullet remains useful only for reading older RL papers/repos; do not build new curriculum on it (stale Python support, dormant maintenance).
- CoppeliaSim's Edu license is a problem for an audience of "software developers new to robotics" who are not enrolled students; GPL-licensed source is an alternative but the ready-made Edu binaries legally exclude hobbyist/corporate learners.
- Genesis is attractive for a "frontier" module (multi-physics, Apple Silicon GPU support, CPU fallback) but its Python ≥ 3.12 requirement, rapid releases and lack of ROS 2/robot-sensor tooling make it unsuitable as the primary beginner tool.

### Gaps
- Could not confirm whether CoppeliaSim released anything after 4.10 (May 2025); the vendor site is JS-rendered.
- Genesis documentation version/changelog dates could not be read from the docs landing page; version info is from PyPI/GitHub.
- No standalone ODE teaching material was sought or found.

---

## Key Question 6 — Unity / Unreal robotics and MATLAB/Simulink robotics

### Takeaway
Unity has refocused robotics on a commercial "Unity Simulation Pro" (Unity 6.3+, URDF drag-and-drop, ROS 2 support) while archiving its older open packages; Unreal Engine is pushed by Epic for photoreal robotics/synthetic data and has research plugins (Unreal Robotics Lab embeds MuJoCo; rclUE bridge) but no mainstream beginner curriculum; MATLAB/Simulink's Robotics System Toolbox (R2026b docs) still only co-simulates with Gazebo Classic 9–11 on Ubuntu 20.04 and uses Unreal Engine for its 3D scenes — all three are niche/paid paths for this audience.

### Cited Findings
- Unity-Robotics-Hub: ~2.6k stars, 472 forks, Apache-2.0, 150 commits; README now centers on "Simulation Pro" ("supported for production on Unity 6.3 and newer"), with "ROS-2 support" and a drag-and-drop URDF importer; course modules use Ubuntu 26.04 + ROS 2 Lyrical in a VM; older packages moved to ARCHIVE.md as "unsupported" — [Unity-Robotics-Hub](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
- Unity Simulation Pro launched in Early Access with a robotics focus (validation, training, digital twins) — [gamedev.net](https://gamedev.net/news/5929-from-simulation-to-real-world-deployment-unity-simulation-pro-early-access/)
- Epic spotlight (Apr 2026): "UE5 is becoming the platform of choice for robotics simulation", positioning Unreal as a synthetic-data factory and noting macOS native support — [Unreal Engine spotlight](https://www.unrealengine.com/spotlights/ue5-is-becoming-the-platform-of-choice-for-robotics-simulation)
- Unreal Robotics Lab (URLab): open-source UE5 plugin embedding MuJoCo, Apache-2.0, ZMQ interface for Python/ROS 2, requires UE 5.7+, Windows (Linux experimental), MuJoCo 3.7+; ICRA 2026 paper — [arXiv 2504.14135](https://arxiv.org/html/2504.14135v3); [URLab project page](https://jonathanembleyriches.github.io/projects/unrealroboticslab/)
- rclUE: only a 2025 "Hello World" tutorial (UE 5.3 Linux + ROS 2 Foxy) was found; no 2026 status — [dio.me tutorial](https://www.dio.me/en/articles/como-utilizar-unreal-engine-5-e-robotica-juntos-04c0c2dc677c)
- MATLAB Robotics System Toolbox Gazebo co-simulation (doc for R2026b): supports Gazebo 9, 10, 11 only; Ubuntu Xenial/Bionic/Focal; provided Linux VM runs Ubuntu 20.04 with Gazebo 11; no code generation; Simulink blocks Gazebo Publish/Subscribe/Select Entity/Pacer; UR10 example — [Gazebo simulation requirements](https://www.mathworks.com/help/robotics/ug/gazebo-simulation-requirements.html); [Gazebo co-simulation](https://www.mathworks.com/help/robotics/gazebo-cosimulation.html); [UR10 co-sim example](https://www.mathworks.com/help/robotics/ug/control-manipulator-robot-with-co-simulation.html); [ROS VM install](https://www.mathworks.com/ros_vm_install/v9)
- MATLAB "Simulation 3D" library uses Unreal Engine for prebuilt scenes, camera and lidar modeling — [Unreal Engine Simulation for Robots](https://ch.mathworks.com/help/robotics/ug/3d-simulation-for-robots.html)
- MathWorks lists Webots as a connected product (MATLAB controllers run inside Webots) — [MathWorks Webots connection](https://au.mathworks.com/products/connections/product_detail/webots.html)

### Inferences
- None of Unity/Unreal/MATLAB fits a free, beginner curriculum for software developers: Unity's robotics path is now a paid product, Unreal requires game-engine skills and a GPU, and MATLAB needs a license and is tied to deprecated Gazebo Classic.
- Mention them as "industry/visualization context" only; if MATLAB is already owned, Webots' MATLAB controller support is the cheapest bridge.

### Gaps
- No pricing or GA date found for Unity Simulation Pro.
- No evidence found of MathWorks supporting new Gazebo (Harmonic/Jetty) co-simulation.

---

## Key Question 7 — Which simulators do widely used courses/curricula pick, and why?

### Takeaway
Confirmed pairings: CU Boulder CSCI 3302 / Coursera "Introduction to Robotics with Webots" → Webots (Python, no GPU, cloud-gradeable); Northwestern Modern Robotics (Coursera) → CoppeliaSim Edu (visualizing kinematics from CSV trajectories, minimal simulator teaching); ROS 2-centric university courses (UMD ENPM605 2026, MOGI-ROS, The Construct's 100+ partner universities) → Gazebo Harmonic + ROS 2 Jazzy; robot-learning graduate courses (UT Austin CS391R via robosuite, UNC COMP 790-186) → MuJoCo/Isaac; Michigan ROB 550 is centered on the physical MBot rather than a simulator; ETH's legged-robotics work used Isaac Gym/legged_gym (research, not a confirmed course). The pattern: intro courses pick the simulator with the lowest setup friction (Webots/CoppeliaSim), ROS courses pick Gazebo because it ships in the ROS repos, and RL courses pick MuJoCo/Isaac for speed and GPU parallelism.

### Cited Findings
- CU Boulder CSCI 3302 uses Webots; Coursera specialization taught in Python with peer-graded assignments — [CU Boulder course](https://www.colorado.edu/lab/correll/node/127); [Coursera](https://www.coursera.org/specializations/introduction-robotics-webots)
- Northwestern Modern Robotics / ME 449 use CoppeliaSim scenes (UR5, youBot) tied to the textbook; EDU version recommended — [Northwestern CoppeliaSim intro](https://hades.mech.northwestern.edu/index.php/CoppeliaSim_Introduction); [ME 449](https://hades.mech.northwestern.edu/index.php/ME_449_Robotic_Manipulation)
- UMD ENPM605 (Spring 2026) teaches Gazebo Harmonic and warns it cannot coexist with Classic — [ENPM605](https://enpm605-spring-2026-docs.readthedocs.io/en/latest/simulation/simulation.html)
- MOGI-ROS course weeks 3–4: URDF + Gazebo Harmonic + ROS 2 Jazzy — [MOGI-ROS](https://github.com/MOGI-ROS/Week-3-4-Gazebo-basics)
- The Construct works "with over 100 universities and colleges worldwide" using its browser-based ROS/Gazebo environment — [The Construct for campus](https://theconstruct.ai/?p=22444)
- Michigan: MBot is a low-cost physical platform for ROB 550 (Robotic Systems Lab) and other courses; results describe hardware, not a simulator — [MBot courses](https://mbot.robotics.umich.edu/um-courses); [MBot paper](https://arxiv.org/abs/2312.00962v1)
- UT Austin CS391R: default project uses robosuite (MuJoCo) — [CS391R project](https://www.cs.utexas.edu/~robertom/cs391r_fall2022/project.html)
- UNC COMP 790-186 Robot Learning lists Isaac/MuJoCo/SAPIEN as prerequisites — [COMP 790-186](https://dingmyu.github.io/course-robot_learning)
- ETH RSL trained ANYmal in simulation with NVIDIA Isaac Gym; `legged_gym` is the lab's open codebase — [Notebookcheck on ETH ANYmal](https://www.notebookcheck.net/ETH-Zurich-researchers-unveil-four-legged-ANYmal-AI-robot-able-to-complete-obstacle-courses-like-K-9s-in-boot-camp.820494.0.html); [leggedrobotics GitHub (mirror)](https://gh.nn.ci/leggedrobotics)
- Stanford AA 174B / CS 237B (Winter 2025) covers RL/contact models but the fetched index did not name a simulator — [CS237B](https://web.stanford.edu/class/cs237b/)
- EPFL MICRO-452 uses the physical Thymio (Python/Aseba); Webots use not confirmed — [EPFL coursebook](https://edu.epfl.ch/studyplan/en/master/microengineering/coursebook/basics-of-mobile-robotics-MICRO-452)
- Reasons cited in the community: Gazebo "ships in the ROS PPA" and has "the most ROS-related tutorials"; Webots is "a lot more beginner-friendly" with "more systematic documentation" — [Discourse thread](https://discourse.openrobotics.org/t/why-is-gazebo-very-famous-in-the-ros-community-what-about-webots/42459)
- Comparison blogs converge on Webots for education, Gazebo for ROS 2, Isaac for GPU RL/photorealism, MuJoCo for research — [ThinkRobotics](https://thinkrobotics.com/es/blogs/learn/webots-vs-gazebo-choosing-a-robotics-simulator); [DEV Community](https://dev.to/godrift_ai/which-robot-simulator-should-you-actually-use-5gn4); [roboticscenter.ai](https://www.roboticscenter.ai/rl-environments/best-2026/)
- ROS wiki maintains a (dated) list of university courses using ROS — [ROS wiki Courses](https://whiteoak.umd.edu/roswiki/Courses.html)

### Inferences
- A beginner→intermediate curriculum mirroring these choices would be: Webots (weeks 1–N: sensors, actuators, odometry, planning in Python) → MuJoCo (dynamics/control/RL on CPU or Colab) → Gazebo Harmonic + ROS 2 Jazzy (ROS integration, Nav2, ros2_control) → optional Isaac Lab/Genesis for GPU-scale learning.
- CoppeliaSim's Edu license makes it hard to adopt for a public developer-oriented curriculum even though Modern Robotics relies on it.

### Gaps
- No 2025–2026 Stanford/Berkeley/CMU syllabus explicitly naming the simulator used for assignments was retrieved.
- Michigan ROB 320 (and whether it uses Gazebo) was not confirmed.

---

## Key Question 8 — Cloud / no-install options for learners without strong hardware

### Takeaway
Realistic no-install paths exist for three of the simulators: MuJoCo (Colab notebooks + live.mujoco.org browser viewer + Studio web streaming), Webots (webots.cloud demos/competitions run from a GitHub repo, no price listed), and Gazebo/ROS 2 (The Construct: free Basic tier with 2 GB storage and 3 free courses; Learner €39.97/month for all courses incl. Gazebo courses on 2 CPU/4 GB RAM; browser-based OLO platform). Isaac Sim is only cloud-viable via paid GPU instances (Brev/AWS) or Isaac Launchable, while Isaac Lab 3.0 now has browser-run Newton demos.

### Cited Findings
- webots.cloud: Demos "run interactively" in the cloud from a registered GitHub repo; Scenes/Animations hosted on webots.cloud; no pricing mentioned — [cyberbotics/webots-cloud](https://github.com/cyberbotics/webots-cloud); course Markdown can be auto-detected and displayed alongside runnable simulations — [webots-cloud wiki Use Cases](https://github.com/cyberbotics/webots-cloud/wiki/Use-Cases)
- robotbenchmark.net (free browser challenges, 2017) appears defunct/hijacked as of Nov 2026 (see KQ1) — [Robohub 2017](https://robohub.org/robotbenchmark-lets-you-program-simulated-robots-from-your-browser/)
- The Construct pricing: Basic free (basic settings, 2 GB project storage, public rosjects only, full access to Linux/Python3/C++ for Robotics courses, first unit of others); Learner €39.97/user/month or €439/year (2 CPUs + 4 GB RAM, all courses incl. "Introduction to Gazebo Sim with ROS2" and "Mastering Gazebo Simulator", learning paths, certificates, TurtleBot3 real-robot lab); Enterprise €2,399/user/year (8 CPUs + 15 GB RAM, all ROS/ROS 2 distros, remote robot labs); educational-institution discount available — [The Construct pricing](https://www.theconstruct.ai/pricing/); users "work from a web browser without having to install or prepare anything", 60+ courses — [The Construct](https://www.theconstruct.ai/?p=3178); 2026 "Robotics Developer Masterclass" (~240 h) — [brochure PDF](https://www.theconstruct.ai/wp-content/uploads/2026/04/Brochure-Robotics-Developer-Masterclass-2026-English.pdf)
- OLO: a browser-based ROS 2 platform for simulation, visualisation and robot programming (announced on ROS Discourse) — [OLO announcement](https://discourse.openrobotics.org/t/introducing-olo-a-browser-based-ros-2-platform-for-simulation-visualisation-and-robot-programming/54932); a browser URDF playground was also announced — [Discourse](https://discourse.openrobotics.org/t/built-a-browser-based-urdf-playground-for-ros-developers/55049.md)
- MuJoCo: official Colab notebooks (links in KQ4); MuJoCo Live runs "entirely in the browser" and can load models from GitHub URLs; Studio WebViewer streams a Python sim to the browser with "no GPU or display server required" on the host — [MuJoCo Studio docs](https://mujoco.readthedocs.io/en/latest/studio/index.html); Menagerie models have live browser viewers — [mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie); MuJoCo Playground trains policies end-to-end in one Colab — [arXiv 2502.08844](https://arxiv.org/html/2502.08844v1)
- Isaac: Brev one-click GPU instances, AWS Marketplace container (EC2 fees), NGC container — [NVIDIA Isaac Sim page](https://developer.nvidia.com/isaac/sim); Isaac Lab 3.0 links 17 interactive Newton demos that run in the browser — [IsaacLab releases](https://github.com/isaac-sim/IsaacLab/releases); Isaac Sim 6.0 added a Chromium browser streaming client — [6.0 GA post](https://forums.developer.nvidia.com/t/isaac-sim-6-0-general-availability/372621)
- Gazebo on Windows laptops: Harmonic works under WSLg with GPU support (user report) — [Discourse WSLg](https://discourse.openrobotics.org/t/wslg-with-gpu-support-available-on-latest-version-of-gazebo-garden-and-harmonic/48128); MathWorks distributes a ready Ubuntu 20.04 VM with ROS/Gazebo 11 (Classic) — [ROS VM](https://www.mathworks.com/ros_vm_install/v9)
- Research on cloud delivery of robotics-programming education (2022) — [arXiv 2210.10441](https://arxiv.org/abs/2210.10441v1); Unibotics browser platform usability study (RIE 2024) — [Unibotics paper](https://gsyc.urjc.es/jmplaza/papers/rie2024-unibotics-usability-draft.pdf)

### Inferences
- For learners on weak laptops: MuJoCo via Colab is the only fully free, zero-install path with real compute; Webots local install is the next cheapest (2 GB RAM, OpenGL 3.3); Gazebo should be offered via The Construct or WSLg/Docker; Isaac should be optional with a cloud fallback.
- GitHub Codespaces was not evaluated by any source found; it is an inference that a Codespace could run MuJoCo (CPU) and headless Gazebo but not a GUI without extra setup.

### Gaps
- Current The Construct catalog of ROS 2 distros/Gazebo versions in the free tier not confirmed.
- webots.cloud compute limits, quotas, and whether running demos requires a Cyberbotics account were not found.
- No source evaluated GitHub Codespaces for robot simulation.

---

## Key Question 9 — Cross-simulator practical-constraints matrix (for curriculum planning)

### Takeaway
On license, OS reach, hardware floor, Python API and ROS 2 integration, Webots and MuJoCo are the only two that are simultaneously free for everyone, cross-platform (Linux/Windows/macOS) and usable on laptops without a discrete GPU; Gazebo adds unmatched ROS 2 integration at the cost of Ubuntu-centric installs and a GPU-sensitive renderer; Isaac delivers GPU RL and photorealism but needs an RTX-class workstation; CoppeliaSim is capable but Edu-license-restricted; Genesis is fast-moving research tooling.

### Cited Findings (compact matrix; each cell cites the KQ where the source appears)
- Webots: latest R2025a (Jan 31, 2025; nightly R2025b/R2026 builds); Apache-2.0; Ubuntu 22.04/24.04/26.04, Win 10/11, macOS 12–14; min 2 GB RAM, OpenGL 3.3 GPU (Intel iGPU not recommended); Python ≥ 3.8 `controller` module; `ros-jazzy-webots-ros2` 2025.0.1 (Kilted support); ~4.8k GitHub stars; official 8 tutorials (~4 h) + Coursera specialization — sources in KQ1
- Gazebo: Harmonic LTS (Sep 2023–May 2029, ROS 2 Jazzy), Jetty LTS (Sep 2025–May 2031, Lyrical), Ionic EOL Dec 2026; Apache-2.0; Ubuntu first-class, macOS via Homebrew, Windows partial (`gz sim` needs two terminals); Ogre2 needs OpenGL 3.3; Python limited to `TestFixture`/Python systems; `ros_gz` in ROS repos (vendor packages since Jazzy); ~1.6k stars gz-sim — KQ2
- Isaac Sim 6.2 / Isaac Lab 3.0 (Oct 2026): Apache-2.0 + NVIDIA additional license / BSD-3; Ubuntu 22.04 (deprecated)/24.04 or Windows 11; min RTX 4080 16 GB VRAM, 32 GB RAM, 50 GB SSD; Python 3.12 (Lab 3.0), 3.11 (Sim 5.x); ROS 2 Humble/Jazzy bridges (Windows via Pixi); DLI courses free; cloud via Brev/AWS — KQ3
- MuJoCo 4.0.0 (Nov 6, 2026): Apache-2.0; Linux/Windows/macOS; CPU-only OK (`pip install mujoco`); Python 3.11+ (3.10 dropped); no official ROS 2 integration found; Colab notebooks; Menagerie ~71 models; live.mujoco.org — KQ4
- PyBullet 3.2.7 (Jan 30, 2025): zlib; wheels up to CPython 3.11; maintenance inactive — KQ5
- CoppeliaSim 4.10 (May 14, 2025): GPL/commercial, Edu free for students/teachers only (academic email); Win/Linux/macOS; Python/Lua scripting, ZeroMQ remote API; ROS support; MuJoCo/Bullet/ODE/Vortex/Newton engines — KQ5
- Genesis World 1.4.6 (Nov 8, 2026): Apache-2.0; Python 3.12–3.14; CUDA/ROCm/Metal/CPU backends; PyTorch required; ~30k stars; no ROS tooling found — KQ5
- Unity Simulation Pro (Unity 6.3+, commercial EA), Unreal (URLab plugin, UE 5.7+, Windows-first), MATLAB RST (Gazebo Classic 9–11 only, Ubuntu 20.04 VM) — KQ6

### Inferences
- Recommended spine for "software developers new to robotics, modest laptops": Webots R2025a (Python) as the primary beginner simulator; MuJoCo (pip/Colab) for dynamics, control and RL; Gazebo Harmonic + ROS 2 Jazzy for the intermediate ROS track (local Ubuntu 24.04/WSLg or The Construct); Isaac Lab 3.0 and Genesis flagged as optional GPU-dependent extensions.
- Pin versions in course material: Webots R2025a, `mujoco` 4.0.x (note the 3.x→4.0 pip split), ROS 2 Jazzy + Gazebo Harmonic, Isaac Sim 6.2 + Isaac Lab 3.0.

### Gaps
- Official hardware floors for Gazebo Harmonic/Jetty and for kit-less Isaac Lab were not found.
- Community-size metrics other than GitHub stars (Discord members, forum activity) were not obtainable.
