# 링크 생존 점검 (LINK_CHECK)

- 점검일: 2026-11-11 (2차: M9 포함 50개 레슨)
- 대상: `curriculum/robotics-expert/**` 레슨 frontmatter `resources[].url` (중복 제거)
- 방법: Python `urllib` 로 HEAD 요청, 실패하면 GET 으로 재시도. 타임아웃 10초, 기본 User-Agent.
- 결과: 110개 중 105개 200 OK, 5개 확인 필요

## 교체한 링크

| 레슨 | 옛 URL (상태) | 새 URL |
|---|---|---|
| m4-sensor-models | `github.imc.re` 미러 (403) | GitHub 원본 저장소 |
| m10-testing-ci-deployment | `awesome.ecosyste.ms` 목록 페이지 (402) | GitHub 원본 저장소 |
| m5-odometry-sensor-fusion | Nav2 옛 `setup_guides/` 경로 (404) | `docs.nav2.org/rolling/` 공식 후속 페이지 + robot_localization 공식 문서 추가 |
| m5-graph-slam-slam-toolbox | FH Aachen 여름학교 자습서 (403, 브라우저에서도 차단) | Nav2 공식 튜토리얼 "Navigating While Mapping" |
| m9-sim-to-real-domain-randomization | NVIDIA Isaac Lab 입문 단원 (404) | 후속 모듈 Robot Learning Fundamentals + Visual Domain Randomization 단원 |

Nav2 와 Isaac Lab 대체 URL 은 리서처 세션(robotics-learning-research)이 제안했고 `research_notes/로보틱스 학습 자료 조사/link_fixes.md` 에 근거가 있다.

## 확인 필요

| url | 상태 | 레슨 |
|---|---|---|
| <https://mathworks.com/videos/tech-talks/controls> | 403 (봇 차단 추정 — 브라우저 수동 확인 필요) | m3-pid-control, m4-filtering-basics |
| <https://www.packtpub.com/en-US/product/mastering-ros-2-for-robotics-programming-9781836209003> | 403 (봇 차단 추정 — 브라우저 수동 확인 필요) | m8-reference-robot-code |
| <https://www.packtpub.com/en-ro/product/ros-2-from-scratch-9781835881415> | 403 (봇 차단 추정 — 브라우저 수동 확인 필요) | m8-nodes-topics-launch |
| <https://www.udemy.com/course/ros2-for-beginners/> | 403 (봇 차단 추정 — 브라우저 수동 확인 필요) | m8-nodes-topics-launch |
| <https://www.udemy.com/course/ros2-moveit2/> | 403 (봇 차단 추정 — 브라우저 수동 확인 필요) | m7-moveit2-reading |

유료 강의·도서 판매 페이지(Udemy, Packt)와 MathWorks 는 자동 요청을 거부하는 것으로 보인다. 브라우저로 열어 살아 있는지 사람이 확인해야 한다.

## 전체 목록

| url | 상태 | 레슨 |
|---|---|---|
| <http://hades.mech.northwestern.edu/index.php/Modern_Robotics> | 200 | m1-coordinate-transforms, m1-rotation-representations, m1-vectors-matrices, m2-dh-parameters, m2-forward-kinematics, m2-inverse-kinematics, m3-differential-drive, m3-path-following, m3-pid-control, m6-local-planning-dwa-mppi, m6-path-smoothing-trajectory, m6-sampling-based-planning, m7-grasping-impedance-control, m7-jacobian-singularity, m7-manipulator-dynamics-torque-control, m7-manipulator-motion-planning, m7-trajectory-generation |
| <https://arxiv.org/abs/2510.12403> | 200 | m9-robot-learning-overview |
| <https://arxiv.org/html/2405.14093v7> | 200 | m9-vla-foundation-models |
| <https://arxiv.org/html/2604.23001> | 200 | m9-datasets-benchmarks-evaluation |
| <https://atsushisakai.github.io/PythonRobotics/> | 200 | m6-configuration-space-graph-search, m6-costmap-global-planning, m6-local-planning-dwa-mppi |
| <https://automaticaddison.com/sensor-fusion-and-robot-localization-using-ros-2-jazzy/> | 200 | m5-odometry-sensor-fusion |
| <https://automaticaddison.com/tutorials> | 200 | m10-testing-ci-deployment |
| <https://autorob.org/> | 200 | m6-sampling-based-planning, m7-manipulator-motion-planning |
| <https://control.ros.org/rolling/doc/getting_started/getting_started.html> | 200 | m10-realtime-safety-reliability, m7-moveit2-reading, m8-stacks-dev-environment |
| <https://discourse.openrobotics.org/c/local/korea/33> | 200 | m10-career-community-portfolio |
| <https://discourse.openrobotics.org/t/what-is-the-hardest-part-of-learning-ros-2-as-a-beginner/57917> | 200 | m8-stacks-dev-environment |
| <https://discuss.ai.google.dev/t/deepminds-reinforcement-learning-lecture-series-2021/29496> | 200 | m9-reinforcement-learning-basics |
| <https://docs.docker.com/guides/ros2/> | 200 | m10-testing-ci-deployment, m8-stacks-dev-environment |
| <https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2> | 200 | m10-testing-ci-deployment, m8-tf2-urdf-visualization |
| <https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/odom/setup_robot_localization/> | 200 | m5-odometry-sensor-fusion |
| <https://docs.nav2.org/rolling/index.html> | 200 | m10-system-architecture-requirements, m6-costmap-global-planning, m6-local-planning-dwa-mppi, m6-nav2-architecture-behavior-trees, m6-path-smoothing-trajectory |
| <https://docs.nav2.org/rolling/tutorials/general_tutorials/navigation2_with_slam/navigation2_with_slam/> | 200 | m5-graph-slam-slam-toolbox |
| <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/robot-learning-fundamentals/index.html> | 200 | m9-sim-to-real-domain-randomization |
| <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transfer-policies-from-simulation-to-reality/03-bridging-the-gap-simulation-enhancement/01-visual-domain-randomization.html> | 200 | m9-sim-to-real-domain-randomization |
| <https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html> | 200 | m9-datasets-benchmarks-evaluation, m9-sim-to-real-domain-randomization |
| <https://docs.ros.org/en/jazzy/Tutorials.html> | 200 | m8-nodes-topics-launch, m8-ros2-concepts-distros, m8-tf2-urdf-visualization |
| <https://docs.ros.org/en/jazzy/p/pinocchio/doc/d-practical-exercises/4-dyn.html> | 200 | m7-manipulator-dynamics-torque-control |
| <https://docs.ros.org/en/lyrical/Related-Projects/Visualizing-ROS-2-Data-With-Foxglove.html> | 200 | m8-tf2-urdf-visualization |
| <https://docs.ros.org/en/rolling/p/robot_localization/> | 200 | m5-odometry-sensor-fusion |
| <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html> | 200 | m1-rotation-representations |
| <https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/> | 200 | m8-reference-robot-code |
| <https://eopla.net/magazines/48000> | 200 | m10-career-community-portfolio |
| <https://fastcampus.co.kr/data_online_mp> | 200 | m7-moveit2-reading |
| <https://fastcampus.co.kr/data_online_physicalai> | 200 | m4-object-detection-intro |
| <https://fastcampus.co.kr/data_online_selfdriving> | 200 | m6-nav2-architecture-behavior-trees |
| <https://fpcv.cs.columbia.edu/> | 200 | m4-camera-model-features, m4-object-detection-intro |
| <https://github.com/2b-t/docker-for-robotics> | 200 | m10-testing-ci-deployment |
| <https://github.com/Ekumen-OS/andino> | 200 | m10-capstone-project-guide, m10-system-architecture-requirements, m6-nav2-architecture-behavior-trees, m8-reference-robot-code |
| <https://github.com/NVIDIA/Isaac-GR00T> | 200 | m9-vla-foundation-models |
| <https://github.com/NxRLab/ModernRobotics> | 200 | m2-forward-kinematics, m2-inverse-kinematics |
| <https://github.com/Physical-Intelligence/openpi> | 200 | m9-vla-foundation-models |
| <https://github.com/TheRobotStudio/SO-ARM100> | 200 | m10-hardware-selection-integration |
| <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public> | 200 | m5-graph-slam-slam-toolbox, m5-kalman-filter-ekf, m5-occupancy-grid-scan-matching, m5-particle-filter-mcl |
| <https://github.com/huggingface/lerobot> | 200 | m9-datasets-benchmarks-evaluation, m9-imitation-learning-bc-dagger |
| <https://github.com/kaiaai/awesome-2d-lidars> | 200 | m4-sensor-models |
| <https://github.com/micro-ROS/micro_ros_setup> | 200 | m10-hardware-selection-integration, m8-stacks-dev-environment |
| <https://github.com/petercorke/robotics-toolbox-python> | 200 | m7-jacobian-singularity, m7-trajectory-generation |
| <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python> | 200 | m4-filtering-basics, m4-sensor-models, m5-bayes-filter, m5-kalman-filter-ekf, m5-odometry-sensor-fusion, m5-particle-filter-mcl |
| <https://github.com/unitreerobotics/unitree_rl_mjlab> | 200 | m9-sim-to-real-domain-randomization |
| <https://github.com/vwxyzjn/cleanrl> | 200 | m9-reinforcement-learning-basics |
| <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos> | 200 | m1-rotation-representations, m2-forward-kinematics, m2-inverse-kinematics, m3-differential-drive, m6-path-smoothing-trajectory, m7-jacobian-singularity, m7-trajectory-generation |
| <https://huggingface.co/blog/smolvla> | 200 | m9-vla-foundation-models |
| <https://huggingface.co/docs/lerobot/so101> | 200 | m10-capstone-project-guide |
| <https://huggingface.co/learn/robotics-course> | 200 | m9-robot-learning-overview |
| <https://introduction-to-autonomous-robots.github.io/> | 200 | m4-filtering-basics |
| <https://lavalle.pl/planning/> | 200 | m6-configuration-space-graph-search, m6-costmap-global-planning, m6-path-smoothing-trajectory, m6-sampling-based-planning, m7-manipulator-motion-planning, m9-mdp-decision-making |
| <https://link.springer.com/10.1007/978-3-031-06469-2> | 200 | m1-rotation-representations, m3-path-following |
| <https://manipulation.mit.edu/> | 200 | m4-object-detection-intro, m7-grasping-impedance-control, m7-manipulator-motion-planning |
| <https://mathworks.com/videos/tech-talks/controls> | 403 | m3-pid-control, m4-filtering-basics |
| <https://moveit.ai/install-moveit2/binary/> | 200 | m7-moveit2-reading |
| <https://moveit.picknik.ai/main/doc/tutorials/tutorials.html> | 200 | m7-moveit2-reading |
| <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010> | 200 | m6-configuration-space-graph-search, m9-mdp-decision-making |
| <https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/> | 200 | m1-vectors-matrices |
| <https://ocw.mit.edu/courses/6-4210-robotic-manipulation-fall-2022/> | 200 | m7-grasping-impedance-control |
| <https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up> | 200 | m10-hardware-selection-integration |
| <https://playground.mujoco.org/> | 200 | m9-sim-to-real-domain-randomization |
| <https://rail.eecs.berkeley.edu/deeprlcourse/> | 200 | m9-imitation-learning-bc-dagger, m9-reinforcement-learning-basics |
| <https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst> | 200 | m8-ros2-concepts-distros |
| <https://robotacademy.net.au/> | 200 | m1-rotation-representations, m3-pid-control, m4-camera-model-features |
| <https://robotics-transformer-x.github.io/> | 200 | m10-capstone-project-guide, m9-datasets-benchmarks-evaluation |
| <https://roboticsbackend.com/courses/> | 200 | m8-tf2-urdf-visualization |
| <https://robots.stanford.edu/probabilistic-robotics/> | 200 | m3-differential-drive, m4-filtering-basics, m5-bayes-filter, m5-occupancy-grid-scan-matching, m5-particle-filter-mcl, m9-mdp-decision-making |
| <https://see.stanford.edu/Course/CS223A> | 200 | m2-dh-parameters |
| <https://trelis.substack.com/p/train-an-act-policy-for-an-so-101> | 200 | m10-capstone-project-guide |
| <https://turtlebot.github.io/turtlebot4-user-manual/tutorials/> | 200 | m10-capstone-project-guide, m8-reference-robot-code |
| <https://ubuntu.com/blog/getting-started-with-micro-ros-on-raspberry-pi-pico> | 200 | m10-realtime-safety-reliability |
| <https://underactuated.mit.edu/> | 200 | m9-imitation-learning-bc-dagger, m9-reinforcement-learning-basics |
| <https://wikidocs.net/book/16208> | 200 | m8-ros2-concepts-distros |
| <https://wikidocs.net/book/18464> | 200 | m5-graph-slam-slam-toolbox, m5-odometry-sensor-fusion |
| <https://www.coursera.org/resources/robotics-learning-roadmap> | 200 | m10-system-architecture-requirements |
| <https://www.coursera.org/specializations/modernrobotics> | 200 | m7-manipulator-dynamics-torque-control, m7-trajectory-generation |
| <https://www.generationrobots.com/en/402707-turtlebot3-burger-mobile-robot.html> | 200 | m10-hardware-selection-integration |
| <https://www.github.com/mlab-upenn/f1tenthpublic> | 200 | m10-career-community-portfolio |
| <https://www.inflearn.com/course/a-complete-breakdown> | 200 | m10-hardware-selection-integration, m10-realtime-safety-reliability, m4-sensor-models |
| <https://www.inflearn.com/course/robot-development-pr> | 200 | m10-system-architecture-requirements |
| <https://www.interconnects.ai/p/robotic-foundation-models> | 200 | m9-robot-learning-overview |
| <https://www.ipb.uni-bonn.de/online-training-robotics/> | 200 | m5-bayes-filter |
| <https://www.koreatimes.co.kr/amp/southkorea/20260129/kwangwoon-university-hosts-robot-developer-conference> | 200 | m10-career-community-portfolio |
| <https://www.open3d.org/docs/release/getting_started.html> | 200 | m4-point-clouds-icp-ransac |
| <https://www.packtpub.com/en-US/product/mastering-ros-2-for-robotics-programming-9781836209003> | 403 | m8-reference-robot-code |
| <https://www.packtpub.com/en-ro/product/ros-2-from-scratch-9781835881415> | 403 | m8-nodes-topics-launch |
| <https://www.plushcap.com/content/huggingface/blog/huggingface-how-i-trained-action-chunking-transformer-act-on-so-101-my-journey-gotchas-and-lessons> | 200 | m9-imitation-learning-bc-dagger |
| <https://www.robocup.org/events/78> | 200 | m10-career-community-portfolio |
| <https://www.routledge.com/A-Concise-Introduction-to-Robot-Programming-with-ROS-2/MartinRico/p/book/9781032851488> | 200 | m6-nav2-architecture-behavior-trees |
| <https://www.udemy.com/course/ros2-for-beginners/> | 403 | m8-nodes-topics-launch |
| <https://www.udemy.com/course/ros2-moveit2/> | 403 | m7-moveit2-reading |
| <https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab> | 200 | m1-vectors-matrices |
| <https://www.youtube.com/playlist?list=PLggLP4f-rq00TQamz2pXjzPWpuxhVN_Vy> | 200 | m7-manipulator-dynamics-torque-control |
| <https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG> | 200 | m6-sampling-based-planning, m7-manipulator-motion-planning |
| <https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp> | 200 | m7-grasping-impedance-control, m7-manipulator-dynamics-torque-control |
| <https://www.youtube.com/watch?v=0I30M6yTklo> | 200 | m5-graph-slam-slam-toolbox |
| <https://www.youtube.com/watch?v=0lKHFJpaZvE> | 200 | m5-bayes-filter |
| <https://www.youtube.com/watch?v=72QwRnSNY88> | 200 | m9-mdp-decision-making |
| <https://www.youtube.com/watch?v=Cu1f6vpEilg> | 200 | m4-point-clouds-icp-ransac |
| <https://www.youtube.com/watch?v=E-6paM_Iwfc> | 200 | m5-kalman-filter-ekf |
| <https://www.youtube.com/watch?v=HR1TNa8Lp7w> | 200 | m6-configuration-space-graph-search, m6-costmap-global-planning |
| <https://www.youtube.com/watch?v=JS5ndD8ans4> | 200 | m4-sensor-models |
| <https://www.youtube.com/watch?v=MQdm0Z_gNcw> | 200 | m1-coordinate-transforms, m4-camera-model-features |
| <https://www.youtube.com/watch?v=MsYlueVDLI0> | 200 | m5-particle-filter-mcl |
| <https://www.youtube.com/watch?v=PiCC-SxWlH8> | 200 | m5-kalman-filter-ekf |
| <https://www.youtube.com/watch?v=SfwxLpdFB-o> | 200 | m4-sensor-models |
| <https://www.youtube.com/watch?v=djnd502836w> | 200 | m4-point-clouds-icp-ransac, m5-occupancy-grid-scan-matching |
| <https://www.youtube.com/watch?v=r2cyMQ5NB1o> | 200 | m4-point-clouds-icp-ransac |
| <https://www.youtube.com/watch?v=uHbRKvD8TWg> | 200 | m5-graph-slam-slam-toolbox |
| <https://www.youtube.com/watch?v=v-Rm9TUG9LA> | 200 | m5-occupancy-grid-scan-matching |
