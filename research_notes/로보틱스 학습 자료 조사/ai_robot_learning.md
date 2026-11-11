# AI-Driven Robotics (Robot Learning / RL / Imitation Learning / VLA / "Physical AI") — Learning Materials Inventory, as of November 2026

Scope note: this covers the *advanced capstone tier* on-ramp for software developers (some ML background) who have finished beginner→intermediate classical robotics. Research date: 11 Nov 2026. Where a page did not state a date/version, that is flagged. Secondary/vendor sources are flagged as such; prefer the primary links.

---

## Key Question 1: Courses (HF/LeRobot course, Berkeley CS 285, Stanford CS 224R, MIT Underactuated / Manipulation, CMU 16-831, NVIDIA DLI, DeepMind x UCL, Spinning Up, Coursera/edX) — status in 2026, free/paid

### Takeaway
The best free, *current* on-ramps in late 2026 are (a) Hugging Face's free "Robotics Course" + the LeRobot-based "Robot Learning: A Tutorial", (b) NVIDIA's free Physical AI Learning paths (Isaac Lab, Newton, and the SO-101 sim-to-real path with GR00T), (c) the two free MIT Tedrake textbooks (Underactuated Robotics; Robotic Manipulation, Fall 2026 edition in progress), and (d) university Deep-RL courses with public materials (Berkeley CS 285 Spring 2026 with Fall 2023 YouTube lectures; Stanford CS 224R Spring 2026; CMU 16-831 Fall 2025). Spinning Up is officially in maintenance mode; Coursera/edX have only general RL courses, not robot-learning-specific ones.

### Cited Findings

**Hugging Face "Robotics Course" (free, self-paced, LeRobot-based)**
- URL: https://huggingface.co/learn/robotics-course. Syllabus table: Unit 0 "Welcome to the Robotics Course" (Released), Unit 1 "Course Introduction — Introduction to robot learning and the LeRobot ecosystem" (Released), Unit 2 "Classical Robotics — Traditional approaches and their limitations" (Released), Unit 5 "Reinforcement Learning" (Coming Soon), Unit 6 "Imitation Learning — Learning from demonstrations and behavioral cloning" (Coming Soon), Unit 7 "Foundation Models — Large-scale models for general robotics" (Coming Soon). Units 3 and 4 are not listed on the page. — [HF Robotics Course](https://huggingface.co/learn/robotics-course)
- Each unit takes "approximately 30-45 minutes"; prerequisites: comfortable with basic Python ("variables, functions, loops"), elementary linear algebra/calculus help but not required, general ML familiarity is a bonus; described as a "free course"; "No formal certification required"; no robot required — "You can follow along with simulated environments and datasets"; the course "is based on the Robot Learning Tutorial". — [HF Robotics Course](https://huggingface.co/learn/robotics-course)
- The course was announced by Ben Burtenshaw (Community Education Lead, Hugging Face); it introduces RL, imitation learning, and foundation models. — [EdTech Innovation Hub](https://www.edtechinnovationhub.com/news/hugging-face-launches-free-robotics-course-exploring-ai-driven-learning-in-robotics) (secondary)
- Caveat: as of 11 Nov 2026 the official syllabus still shows Units 5–7 as "Coming Soon" — the RL/IL/foundation-model units have not shipped on the course page; learners should use the Tutorial (below) for those topics. — [HF Robotics Course](https://huggingface.co/learn/robotics-course)

**"Robot Learning: A Tutorial" (Hugging Face LeRobot team; free; arXiv + HF Space)**
- arXiv:2510.12403, submitted 14 Oct 2025, authors Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, Michel Aractingi. Abstract: covers the shift from model-based robotics to data-driven robot learning, starting with Reinforcement Learning and Behavioral Cloning and moving to generalist, language-conditioned models across tasks and embodiments; includes "ready-to-use examples implemented in lerobot". — [arXiv 2510.12403](https://arxiv.org/abs/2510.12403)
- Interactive version hosted as a Hugging Face Space "Robot Learning: A Tutorial" (lerobot/robot-learning-tutorial, 560 likes at time of fetch). — [HF Space](https://huggingface.co/spaces/lerobot/robot-learning-tutorial)
- The LeRobot README lists the "Robot Learning Tutorial, a free, hands-on course to learn robot learning using LeRobot". — [LeRobot GitHub](https://github.com/huggingface/lerobot)

**UC Berkeley CS 285 Deep Reinforcement Learning (Sergey Levine) — free materials**
- URL: https://rail.eecs.berkeley.edu/deeprlcourse/. Current offering: Spring 2026 (staff list cs285-staff-sp2026@…, Week 1 Jan 19–23, 2026); instructor Sergey Levine; Head GSI Seohong Park; GSIs include Kevin Black (co-author of π0). — [CS 285 site](https://rail.eecs.berkeley.edu/deeprlcourse/)
- Five homework PDFs posted: (1) Imitation Learning, (2) Policy Gradients, (3) Q-Learning and Actor Critic, (4) LLM RL, (5) Offline RL. Topics: imitation learning/behavioral cloning incl. distributional shift, policy gradients, actor-critic, Q-learning, control as inference, LLM RL, model-based RL, offline RL, exploration, RL theory, multi-task RL. — [CS 285 site](https://rail.eecs.berkeley.edu/deeprlcourse/)
- Public YouTube recordings are linked only for the Fall 2023 offering; the page does not say whether Spring 2026 lectures are public. — [CS 285 site](https://rail.eecs.berkeley.edu/deeprlcourse/)

**Stanford CS 224R Deep Reinforcement Learning — free slides**
- URL: https://cs224r.stanford.edu. Spring 2026 offering listed (Wed/Fri 9:30–11:00, NVIDIA Auditorium); 2026 intro slides at https://cs224r.stanford.edu/slides/01_cs224r_intro_2026.pdf. Topics (per student notes on the 2026 course): RL basics, Q-learning, offline RL, reward learning from preferences/RLHF, model-based RL, multi-task/goal-conditioned RL, meta-RL, hierarchical RL, sim-to-real robot learning. Prerequisites: familiarity with deep learning (incl. transformers) and basic RL; assignments in PyTorch; compared with CS234 it is more applied and emphasizes robotics and language modeling. — [CS 224R](https://cs224r.stanford.edu); [2026 notes (student, secondary)](https://web.stanford.edu/~srliu/homepage/notes/cs224r/)
- Chelsea Finn is confirmed as instructor for Spring 2025 (lecture 1 recording via Stanford Online); a third-party aggregator says she also taught Spring 2026, but I found no official 2026 page naming her. — [Recapio summary of Spring 2025 Lecture 1](https://recapio.com/digest/stanford-cs224r-deep-reinforcement-learning-spring-2025-lecture-1-class-intro-by-stanford-online); [beri.net (secondary)](https://www.beri.net/learning/stanford-cs224r-deep-rl-spring-2026)
- Stanford CS 237B (Principles of Robot Autonomy II) and "CS 336-ish robot learning": not researched in this pass (see Gaps).

**MIT 6.8210 Underactuated Robotics (Russ Tedrake) — free textbook + videos**
- URL: https://underactuated.mit.edu/. Textbook *Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation* by Russ Tedrake; the notes page says they are working notes for a course taught in Spring 2024 (no Spring 2026 edition stated on the landing page); lecture videos "available on YouTube"; software is Drake via Python bindings (pydrake); PDF from GitHub releases. — [underactuated.mit.edu](https://underactuated.mit.edu/)
- Chapters most relevant to the AI layer: Ch. 7 Dynamic Programming, Ch. 8 LQR, Ch. 10 Trajectory Optimization, Ch. 11 Policy Search, Ch. 15 Output Feedback ("Pixels-to-Torques"), Ch. 17 Planning and Control through Contact, Ch. 18 System Identification, Ch. 20 Model-Free Policy Search (the RL chapter), Ch. 21 Imitation Learning. — [underactuated.mit.edu](https://underactuated.mit.edu/)

**MIT 6.4210 Robotic Manipulation (Russ Tedrake) — free textbook, Drake**
- URL: https://manipulation.mit.edu/. Textbook *Robotic Manipulation: Perception, Planning, and Control*; the notes "will be updated throughout the Fall 2026 semester" (i.e., actively maintained as of Nov 2026); software Drake (pydrake, online Jupyter notebooks, Google Colab, Appendix B); HTML + PDF (GitHub). Chapters: 1 Intro, 2 Let's get you a robot, 3 Basic Pick and Place, 4 Geometric Pose Estimation, 5 Bin Picking, 6 Motion Planning, 7 Mobile Manipulation, 8 Manipulator Control, 9 Object Detection and Segmentation, 10 Deep Perception for Manipulation, 11 Reinforcement Learning (policy-gradient, value-based, model-based), 12 Soft Robots and Tactile Sensing; appendix on DrakeGym environments. Imitation learning does not appear as its own chapter in the TOC. — [manipulation.mit.edu](https://manipulation.mit.edu/)

**CMU 16-831 Introduction to Robot Learning — free slides**
- Official site https://16-831.github.io with per-semester pages; most recent found: Fall 2025 (https://16-831.github.io/fall25, schedule at /fall25/lectures; T/Th 12:30–1:50). Topics: imitation learning, model-free and model-based RL, bandits and exploration, offline RL, sim-to-real, safe robot learning. A third-party summary names Guanya Shi as instructor (not confirmed from the official page). — [16-831.github.io](https://16-831.github.io/); [Fall 2025](https://16-831.github.io/fall25); [third-party summary](https://gozhiyuan.github.io/robotics/2025/05/01/cmu-robotics-intro-01.html)

**NVIDIA Physical AI Learning / DLI (free, registration required)**
- Portal: https://docs.nvidia.com/learning/physical-ai/ — "all learning paths are free to access for self-paced learning". Courses include "An Introduction to Robot Learning and Isaac Lab" (https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/an-introduction-to-robot-learning-and-isaac-lab/index.html), "Train Your First Robot in Isaac Lab", "Transferring Robot Learning Policies From Simulation to Reality", and "Accelerating Robot Learning With Isaac Lab and Newton" (https://docs.nvidia.com/learning/physical-ai/getting-started-with-newton/latest/index.html; requires comfort with Python). — [NVIDIA Physical AI Learning](https://docs.nvidia.com/learning/physical-ai/); [NVIDIA Robotics learning path](https://nvidia.com/en-us/learn/learning-path/robotics)
- "Sim-to-Real with SO-101" learning path (https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html): modules Overview (sim-to-real background, LeRobot background), Build Your Robot Lab (SO-101 setup, calibration), Collect Data/Train/Evaluate (domain randomization with teleoperation, GR00T VLA models, sim and real evaluation), Augment Datasets (co-training with real data, Cosmos augmentation), Measure the Actuation Gap (SAGE + GapONet); task is "unstructured pick-and-place of centrifuge vials"; "Train vision-language-action (VLA) models using GR00T for robot manipulation"; © 2026 NVIDIA; no cost or GPU stated. — [NVIDIA SO-101 path](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html)
- A third-party DLI guide claims some NVIDIA DLI courses cost $30–$90; this conflicts with NVIDIA's own "free" labeling of the Physical AI paths — verify per-course. — [pasqualepillitteri.it (secondary)](https://pasqualepillitteri.it/en/news/25084/nvidia-ai-courses-certifications-dli-guide)

**DeepMind x UCL Reinforcement Learning Lecture Series (2021) — free YouTube**
- 13 videos (~45 min to just under 2 h each), taught by DeepMind researchers; Lecture 1 "Introduction to Reinforcement Learning" by Hado van Hasselt; topics: exploration/control, MDPs and dynamic programming, model-free prediction and control, function approximation, planning, policy gradients, deep RL. Playlist short link dpmd.ai/DeepMindxUCL21. David Silver's older "RL Course" is a separate (2015) series. — [Google AI dev forum post](https://discuss.ai.google.dev/t/deepminds-reinforcement-learning-lecture-series-2021/29496); [Class Central listing](https://classcentral.com/classroom/youtube-deepmind-x-ucl-deep-learning-lecture-series-2020-45714)

**OpenAI Spinning Up in Deep RL — maintenance mode**
- URL: https://spinningup.openai.com. Official docs state the project "is currently in maintenance mode, with bug fixes only and no major updates currently planned". A 2025 community post describes a volunteer effort to modernize it because implementations were tied to older dependencies. CleanRL (single-file implementations, JMLR 2022; https://github.com/vwxyzjn/cleanrl) is the commonly cited modern alternative for readable algorithm references. — [Spinning Up intro](https://spinningup.openai.com/en/latest/user/introduction.html); [OpenAI community post](https://community.openai.com/t/modernizing-spinning-up-for-today-s-reinforcement-learning-researchers/1358002); [CleanRL JMLR](https://jmlr.org/papers/v23/21-1342.html)

**Coursera / edX / other MOOCs**
- No 2026 Coursera or edX course specifically on robot RL was found. Closest: Coursera "Foundations of Reinforcement Learning" Specialization (University of Colorado Boulder; first course "Mastering Classic Reinforcement Learning Algorithms", 14 hours, tabular methods) and edX "Reinforcement Learning" (RWTH Aachen; 8 weeks × 2 h/week, free to audit, intermediate, basic probability required) — both general RL. Robotics-specific paid/free alternatives: Columbia Plus "Introduction to Deep RL from a Robotics Perspective" ($99, Columbia's own platform); KI-Campus "Robot Learning" (free, German platform); The Construct "Reinforcement Learning for Robotics" (Python). — [Coursera CU Boulder](https://www.coursera.org/learn/mastering-classic-reinforcement-learning-algorithms); [Columbia Plus](https://plus.columbia.edu/content/introduction-deep-rl-robotics-perspective); [KI-Campus](https://ki-campus.org/en/learning-opportunities/courses/robot-learning); [The Construct](https://app.theconstruct.ai/courses/68)
- ETH Zurich "Robot Learning: From Fundamentals to Foundation Models" (Spring 2026) reportedly released slides, lecture recordings and coding assignments openly, covering imitation learning through foundation models — from a secondary post; official page not verified. — [bittide.aicompass.dev (secondary)](https://bittide.aicompass.dev/article/69793b83-33b9-4b2d-a450-33b33c427b0c)

### Inferences
- For this curriculum's capstone tier, the lowest-friction sequence is: HF Robotics Course Units 0–2 → "Robot Learning: A Tutorial" (RL + BC + generalist policies with runnable LeRobot code) → NVIDIA "Introduction to Robot Learning and Isaac Lab" → selected CS 285 lectures (Fall 2023 YouTube) for RL depth. Tedrake's two books are the bridge from classical control to learning (Ch. 20–21 of Underactuated; Ch. 9–11 of Manipulation).
- University courses (CS 285, CS 224R, 16-831) are graduate-level and assume deep-learning fluency; for a developer with "some ML", they are reference material rather than the first stop.
- Spinning Up remains useful as *reading* (its "Key Papers" and algorithm explanations) but its code should not be the learner's implementation base in 2026; CleanRL or the RL libraries bundled with Isaac Lab/mjlab (RSL-RL, SKRL) are more current.

### Gaps
- HF Robotics Course Units 3–4 are absent from the syllabus table and Units 5–7 are "Coming Soon" with no dates; release schedule unknown.
- Whether CS 285 Spring 2026 and CS 224R Spring 2026 lecture videos are public was not confirmed.
- Stanford CS 237B and any "CS 336-style" robot learning course were not researched; 16-831 current instructor not confirmed from an official page; ETH Zurich 2026 course not verified on an official site.
- No per-course pricing confirmed for individual NVIDIA DLI courses beyond the "free" Physical AI Learning portal label.

---

## Key Question 2: Frameworks and tools (LeRobot, Isaac Lab, MuJoCo Playground/MJX, mjlab, Gymnasium-Robotics, robosuite, ManiSkill3, Genesis, RLBench, OXE, DROID) — what they offer and which are approachable

### Takeaway
LeRobot (v0.7.0, Nov 2026) is the de-facto learner entry point for imitation learning and VLA fine-tuning with a cheap real arm (SO-101); Isaac Lab 3.0 is now installable without Isaac Sim via the Newton backend (uv-based, Python 3.12), lowering its barrier substantially; MuJoCo Playground 1.0 (PyTorch, MuJoCo Warp, SO-101 sim-to-real) and mjlab (Isaac Lab API on MuJoCo Warp) are the lightest GPU-RL paths. Gymnasium-Robotics/robosuite remain the simplest CPU-only sandboxes; ManiSkill3 and Genesis are GPU-parallel manipulation/sim options with heavier setup.

### Cited Findings

**LeRobot (Hugging Face) — Apache-2.0, PyTorch**
- README (fetched Nov 2026): "28.8k stars", 6.1k forks; install `pip install lerobot` then `lerobot-info`; extras e.g. `'lerobot[dataset]'`, `'lerobot[core_scripts,feetech]'` "to record with an SO-101 arm". Policies: imitation learning — ACT, Diffusion, VQ-BeT, Multitask DiT; RL — HIL-SERL, TDMPC, QC-FQL (coming soon); VLA — Pi0, Pi0Fast, Pi0.5, GR00T N1.7, SmolVLA, XVLA and ~10 others; world models — VLA-JEPA, LingBot-VA, FastWAM; reward models — SARM, TOPReward, Robometer. Robots/devices: "SO101, OpenARM, LeKiwi, Unitree G1, reBot B601, Koch, HopeJR, OMX, EarthRover, Reachy2, Gamepads, Keyboards, Phones and more." Sim benchmarks: LIBERO, MetaWorld (custom envs via EnvHub). Dataset: "Synchronized MP4 videos (or images) for vision and Parquet files for state/action data" hosted on the Hub (docs link "lerobot-dataset-v3"). Cite as ICLR 2026 paper, arXiv 2602.22818. — [LeRobot GitHub](https://github.com/huggingface/lerobot)
- Release history (GitHub releases page shows day/month only; years inferred from ordering and today's date): v0.7.0 (05 Nov, latest) — W&B replaced by Trackio, FSDP2/HSDP distributed training, LanceDB datasets, interactive rollout sessions, policy EMA, pi0.5 RTC and MEM, MolmoAct2, reBot B601, breaking changes to install/training/hardware layer; v0.6.1 (03 Aug); v0.6.0 (06 Jul) — slimmer base install, GR00T N1.7 replaces N1.5, min PyTorch 2.7, RL stack rebuilt, `lerobot-rollout` CLI, benchmarks RoboTwin 2.0 / RoboCasa365 / RoboMME / LIBERO-plus / VLABench, EO-1 policy; v0.5.1 (07 Apr) — relative actions for pi0/pi0.5/pi0-fast, DAgger-style collection, Multitask DiT; v0.5.0 (09 Mar) — Transformers v5, Python 3.12+, Unitree G1 whole-body control, dataset v2.1→v3.0 conversion; v0.4.4 (27 Feb) — OpenArm, Damiao/RobStride CAN motors, G1 teleop, streaming video encoding. — [LeRobot releases](https://github.com/huggingface/lerobot/releases); v0.6.0 on 7 Jul 2026 also reported by [letsdatascience (secondary)](https://letsdatascience.com/news/hugging-face-releases-lerobot-06-robotics-toolkit-908e3ba5)
- SO-101 (flagship arm): docs at https://huggingface.co/docs/lerobot/so101; parts via TheRobotStudio SO-ARM100 README (BOM, 3D-print files, advice if no printer); follower uses 6× Feetech STS3215 motors (1/345 gearing), leader uses mixed gear ratios; CLI flow `lerobot-find-port` → `lerobot-setup-motors` → `lerobot-calibrate` → "Getting started with real-world robots" (il_robots) tutorial; Discord support link. No price stated on the docs page. — [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101); [SO-ARM100 repo](https://github.com/TheRobotStudio/SO-ARM100)
- Official compute guide (indicative): Light BC (`act`, `vqbet`, `tdmpc`) ~2–6 GB VRAM at BS 8, "Laptop GPU (RTX 3060), L4, A10G"; Diffusion ~8–14 GB (RTX 4070+); SmolVLA ~10–16 GB (RTX 4080+); Large VLA (`pi0`, `pi0_fast`, `pi05`, `xvla`, `wall_x`) ~24–40 GB (A100 40 GB+, "24 GB tight at BS 1"); Multimodal (`groot`, `eo1`) ~24–40 GB. Wall-clock for 5 epochs on ~50 episodes (~45k frames): ACT on RTX 4090/3090 ~30–60 min; Diffusion ~2–4 h; SmolVLA on L4/A10G ~3–6 h or on A100 40 GB ~1–2 h; pi0/pi05 on A100 40 GB ~4–8 h; ACT on Apple Silicon (MPS) ~6–14 h; "CPU only — Don't train. Use Colab or rent a GPU." Imitation learning "typically converges in 5–10 epochs over the dataset". Managed training via Hugging Face Jobs (`--job.target=a10g-large`, billed by the second; flavors t4-small/medium (ACT only), l4x1/x4, a10g-*, a100-large). — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide)
- Community write-ups on first SO-101 ACT runs: HF blog "How I trained Action Chunking Transformer (ACT) on SO-101" (Sherry Chen); Trelis "Train an ACT Policy for an SO-101 Robot"; Classmethod ACT eval; HIL-SERL on SO-101 deployment learnings (2026); Jetson AGX Orin SO-101 kit guide (Hackster). — [HF blog mirror](https://www.plushcap.com/content/huggingface/blog/huggingface-how-i-trained-action-chunking-transformer-act-on-so-101-my-journey-gotchas-and-lessons); [Trelis](https://trelis.substack.com/p/train-an-act-policy-for-an-so-101); [Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/); [HIL-SERL blog 2026](https://indraneelpatil.github.io/blog/2026/hil-serl); [Hackster Jetson](https://www.hackster.io/shahizat/running-lerobot-so-101-arm-kit-using-nvidia-jetson-agx-orin-19b8a4)
- Seeed Studio runs an SO-ARM "Physical AI course" wiki (chapter 15 example uses `--steps=300000`). — [Seeed wiki](https://wiki.seeedstudio.com/robotics/soarm_physical_ai_course_chapter_15/)

**NVIDIA Isaac Lab — BSD-3 (parts Apache-2.0)**
- Docs: https://isaac-sim.github.io/IsaacLab/. "a unified and modular framework for robot learning" supporting RL, learning from demonstrations, and motion planning; Isaac Lab 3.0 is the current major release (Isaac Sim 6.2.0 badge; version dropdown includes v3.0.0-beta2.patch1); "can also run standalone with the Newton physics backend for fast and efficient simulation" without a full Isaac Sim install; Newton supports soft bodies, cloth, experimental cables (VBD solver). — [Isaac Lab docs](https://isaac-sim.github.io/IsaacLab/main/index.html)
- Installation (3.0): default install is Newton, "The standard installation runs without Isaac Sim"; Python 3.12 with automatic `uv` setup; OS Ubuntu 22.04+ x86_64, Linux aarch64 (incl. DGX Spark), Windows 11; GPU: CUDA-capable NVIDIA, "The default CUDA 13 stack requires Turing or newer (compute capability 7.5+)"; "Headless Newton simulation does not require RTX hardware"; "RAM and VRAM needs depend on the task, number of parallel environments, and camera workload"; drivers Linux x86_64 595.58.03 / Windows 595.97; published package `uv pip install isaaclab==3.0.0` from pypi.nvidia.com. Optional Isaac Sim 6.2 (5.1 and older unsupported): "plan for at least 32 GB RAM, 16 GB VRAM, and a supported RTX GPU". — [Isaac Lab installation](https://isaac-sim.github.io/IsaacLab/main/source/isaaclab/installation.html)
- Isaac Lab paper: "Isaac Lab: A GPU-Accelerated Simulation Framework for Multi-Modal Robot Learning" (arXiv 2511.04831). Isaac Lab 2.3 added whole-body control, enhanced imitation learning and locomotion; Newton 1.0 GA announced at GTC 2026. — [arXiv 2511.04831](https://arxiv.org/html/2511.04831v1); [NVIDIA blog Isaac Lab 2.3](https://developer.nvidia.com/blog/streamline-robot-learning-with-whole-body-control-and-enhanced-teleoperation-in-nvidia-isaac-lab-2-3/); [NVIDIA Newton blog](https://developer.nvidia.com/blog/newton-adds-contact-rich-manipulation-and-locomotion-capabilities-for-industrial-robotics)
- Third-party Isaac Lab VRAM guidance conflicts: one tutorial says ≥8 GB VRAM, 12 GB+ recommended for parallel RL; a roboticscenter.ai guide lists RTX 3090 24 GB as "minimum for small experiments" and claims a 4090 handles ~1,024 envs for a 6-DOF arm vs 512 on a 3090 (unverified against NVIDIA data). — [roboticscenter.ai (vendor)](https://www.roboticscenter.ai/ja/blog/nvidia-isaac-lab-getting-started); [Isaac Lab performance benchmarks](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta/_sources/source/overview/reinforcement-learning/performance_benchmarks.rst)

**MuJoCo Playground 1.0 (Google DeepMind) — Apache-2.0**
- "An open-source library for sim and real robot demos on top of MuJoCo"; v1.0 is PyTorch-based on MuJoCo / MuJoCo Warp / reaf-sim, successor to the RSS 2025 JAX/MJX research preview (kept under `rss2025`); workflows: whole-body motion tracking (Unitree G1, 29-DoF, large-batch GPU RL with RSL-RL), system identification (`mujoco.sysid`), sim and real teleoperation (SO-101, MCAP logging), zero-shot sim-to-real SO-101 pick-cube (`--mode=sim`/`--mode=real`), agentic VLM tabletop manipulation. Robots: SO-101, i2rt YAM Pro, Trossen WidowX AI (sim), Unitree G1 (sim). Install: `uv venv --python 3.13` + `uv pip install "playground>=1.0"`; Python 3.12–3.13; CPU and CUDA 12/13; "8,192 parallel envs on GPU"; "~1 min on CPU" for CartpoleBalance with 64 worlds; TensorBoard monitoring. Citation year 2026; the page does not list the old DM Control / Go1 / Spot / Berkeley Humanoid suites. — [playground.mujoco.org](https://playground.mujoco.org/); [GitHub](https://github.com/google-deepmind/mujoco_playground)

**mjlab (MuJoCo Lab) — Apache-2.0**
- "mjlab combines Isaac Lab's manager-based API with MuJoCo Warp, a GPU-accelerated version of MuJoCo", with minimal dependencies; tasks `Mjlab-Velocity-Flat-Unitree-G1` and `Mjlab-Tracking-Flat-Unitree-G1`; "requires an NVIDIA GPU for training. macOS is supported for evaluation only"; try without install: `uvx --from mjlab --refresh demo`; Google Colab notebook available; multi-GPU via `--gpu-ids`; ~3.4k stars; arXiv 2601.22074 (2026); MuJoCo Warp 3.16.0 badge. — [mjlab GitHub](https://github.com/mujocolab/mjlab)
- Unitree's official `unitree_rl_mjlab` builds on mjlab (see Key Question 5).

**ManiSkill3 — GPU-parallel manipulation**
- Paper: "ManiSkill3: GPU Parallelized Robotics Simulation and Rendering for Generalizable Embodied AI" (arXiv 2410.00425); claims simulation with rendering "10-1000x faster with 2-3x less GPU memory usage than other platforms"; built on PhysX (like Isaac Lab); Gymnasium-style API, e.g. `gym.make("PickCube-v1")` with configurable parallel envs; PyPI `mani-skill`; docs maniskill.readthedocs.io. — [arXiv 2410.00425](https://arxiv.org/abs/2410.00425); [PyPI](https://pypi.org/project/mani-skill)

**robosuite and Gymnasium-Robotics — CPU-friendly starters**
- Community overview: robosuite = MuJoCo manipulation tasks, "recommended for rich tasks + stable MuJoCo development"; Gymnasium-Robotics = "standard Gymnasium API, seamless integration with Stable-Baselines3", recommended as a standard RL benchmark. Sites: https://robosuite.ai, https://robotics.farama.org. — [jeffliulab overview (community)](https://jeffliulab.github.io/ai-notes/en/Embodied_Intelligence/06_Software/%E5%BC%80%E6%BA%90%E6%A1%86%E6%9E%B6/)

**Genesis — two things with the same name**
- Original open-source Genesis simulator (Dec 2024, Apache-2.0, github.com/Genesis-Embodied-AI/Genesis): developer speed claims up to ~430,000× real time; a Go2 locomotion policy "took about 26 seconds on a single RTX 4090" (developer claim); a mid-2026 wiki says the repo reached v1.2.1 in July 2026 with ~29.5k stars and that third-party benchmarks produced "a more nuanced picture" of its speed. — [The Decoder](https://the-decoder.com/genesis-speeds-up-ai-robot-training-with-simulations-430000x-faster-than-reality/); [aiwiki (secondary)](https://www.aiwiki.ai/wiki/genesis_simulator/raw)
- Genesis AI (company) open-sourced "Genesis World 1.0" (blog 27 May 2026; github.com/Genesis-Embodied-AI/genesis-world), three components including a GPU compute layer "Quadrants"; company claims ~89% sim-to-real correlation (not independently verified). — [Genesis AI blog](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward); [Robotics & Automation News](https://roboticsandautomationnews.com/2026/06/04/genesis-ai-launches-simulation-platform-to-accelerate-robotics-development/102243/)
- Genesis docs include a Go2 locomotion RL tutorial: minimal pipeline using PPO from rsl-rl at 50 Hz, models ~20 ms action latency, trained policy is a joint-position controller deployable to a physical Go2. — [Genesis locomotion tutorial](https://genesis-world.readthedocs.io/en/latest/user_guide/policy_training/examples/locomotion.html)

**Datasets: Open X-Embodiment and DROID**
- OXE (robotics-transformer-x.github.io; code github.com/google-deepmind/open_x_embodiment; arXiv 2310.08864): "1M+ real robot trajectories", 22 robot embodiments, 60 source datasets, 527 skills, 160,266 tasks; models RT-1-X and RT-2-X (incl. a 55B version); per-dataset licensing via a Google Sheet; native RLDS (TFDS) format. — [OXE site](https://robotics-transformer-x.github.io/)
- LeRobot-format mirrors exist: `IPEC-COMMUNITY/OpenX-LeRobot` with 31 subsets on the Hub; DROID also began in RLDS; licenses "run the gamut from commercially usable CC-BY 4.0 to non-commercial-only" per subset. DROID size reported variously as 76k vs 60k trajectories by secondary sources (unresolved). — [Pebblous datasets report (secondary)](https://blog.pebblous.ai/report/robot-physical-ai-datasets-landscape/en/); [roboticscenter.ai (vendor)](https://www.roboticscenter.ai/datasets/compare/open-x-vs-droid/)
- openpi provides DROID fine-tuning instructions and checkpoints (see KQ3). — [openpi](https://github.com/Physical-Intelligence/openpi)

### Inferences
- Approachability ranking for a developer-learner (my synthesis of the above): (1) LeRobot — pip install, CLI-driven, rich tutorials, real-arm path under hobby budget; (2) Gymnasium-Robotics / robosuite — CPU-only, SB3-compatible, good for first PPO/SAC runs; (3) MuJoCo Playground 1.0 and mjlab — `uv`-based, Colab/CPU demos, NVIDIA GPU for serious training; (4) Isaac Lab 3.0 with Newton — now far easier than 2.x (no Isaac Sim), but NVIDIA-only and Turing+ GPU; (5) ManiSkill3 / Genesis — powerful but heavier setup and more churn.
- RLBench was not surfaced by any search in this pass; given the field's move to LIBERO/MetaWorld/RoboCasa benchmarks inside LeRobot, treat RLBench as legacy for learners (unverified).
- The LeRobot v0.5→v0.7 cadence (four minor releases in ~9 months with breaking changes in v0.7.0) means tutorials written against v0.4.x may not run unmodified; pin the version a tutorial names.

### Gaps
- No official SO-101 kit price found on HF docs (hobbyist guides cite various vendor kits; not verified here).
- Isaac Lab 3.0 stable vs beta status on 11 Nov 2026 is ambiguous (docs show "3.0" and "v3.0.0-beta2.patch1"; pypi package `isaaclab==3.0.0` exists).
- RLBench status, Gymnasium-Robotics/robosuite current versions, and Genesis v1.2.1 release notes were not verified from primary pages.
- DROID official site (droid-dataset.github.io) was not fetched; trajectory counts conflict across secondary sources.

---

## Key Question 3: Foundation models for robotics (π0/π0.5, OpenVLA, Octo, RT-2, GR00T N1.x/N2, Gemini Robotics, Figure Helix, SmolVLA, MolmoAct2) — open weights, consumer-hardware runnability, tutorials

### Takeaway
As of Nov 2026, the open-weight models a learner can actually run are SmolVLA (450M, Apache-2.0, consumer GPU), π0/π0.5 via openpi or LeRobot (Apache-2.0 code; inference >8 GB, LoRA fine-tune >22.5 GB i.e. an RTX 4090, full fine-tune >70 GB), NVIDIA GR00T N1.7 (Apache-2.0 code, NVIDIA Open Model License weights; inference 16 GB+, fine-tune 40 GB+ recommended), OpenVLA/OpenVLA-OFT (MIT), Octo, and Ai2's MolmoAct2 (fully open incl. data, May 2026). Gemini Robotics On-Device 2 (July 2026) is trusted-tester only; Figure Helix is closed; RT-2 was never released as weights.

### Cited Findings

**SmolVLA (Hugging Face)**
- Blog "SmolVLA: Efficient Vision-Language-Action Model trained on LeRobot Community Data" — https://huggingface.co/blog/smolvla. Community/vendor pages list it at 450M params, Apache-2.0, runnable "on a consumer GPU or CPU", "the most plug-and-play VLA route on LeRobot"; one community report: ~20,000 steps in ~4 h on a single A100 at batch 64. — [HF blog](https://huggingface.co/blog/smolvla); [roboticscenter.ai (vendor)](https://www.roboticscenter.ai/tools/vla-models-comparison/); [particula.tech (secondary)](https://particula.tech/blog/openvla-vs-pi0-vs-smolvla-vs-groot-n1)
- LeRobot official sizing: SmolVLA ~10–16 GB VRAM at BS 8 (RTX 4080+ / L4 / A10G); ~3–6 h for 5 epochs/50 episodes on an L4; tip `freeze_vision_encoder=True` if memory-bound. — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide)
- Tutorials: "How to Fine-Tune SmolVLA on SO-101 with LeRobot" (OpenELAB); example community fine-tunes on the Hub (Project-IRA TPSoSe2026 SmolVLA SO101). — [OpenELAB](https://openelab.io/fr/blogs/learn/how-to-fine-tune-smolvla-on-so-101-with-lerobot); [HF model](https://huggingface.co/Project-IRA/TPSoSe2026_SmolVLA_LeRobot_SO101_Finetuning_V2_Lego)

**π0 / π0-FAST / π0.5 (Physical Intelligence, openpi) — Apache-2.0**
- openpi (https://github.com/Physical-Intelligence/openpi): models π₀ (flow-based VLA), π₀-FAST (autoregressive, FAST tokenizer), π₀.₅ (flow-matching head only in this repo); π₀.6 not mentioned. Single-GPU memory: inference >8 GB (RTX 4090 example); LoRA fine-tuning >22.5 GB (RTX 4090); full fine-tuning >70 GB (A100 80 GB / H100); tested only on Ubuntu 22.04. Examples: DROID (fine-tune instructions + checkpoints), ALOHA (real + sim), LIBERO (π₀.₅-LIBERO checkpoint), UR5; SO-101 not mentioned. JAX original; PyTorch π₀/π₀.₅ added Sept 2025 (no π₀-FAST, no LoRA/FSDP/EMA in PyTorch; requires patching transformers 4.53.2). Updates: Jun 2025 full-DROID training; Sept 2025 PyTorch + π₀.₅. — [openpi](https://github.com/Physical-Intelligence/openpi)
- LeRobot ships π0/π0.5/π0-FAST with PaliGemma-3B backbone and checkpoints like `lerobot/pi05_base`; LeRobot guide: ~24–40 GB VRAM, A100 40 GB+, "24 GB tight at BS 1"; pi05 fine-tune on 4×H100 for 5k steps ≈ 3h41m. — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide); [sebastiandavidlee ecosystem notes (community)](https://sebastiandavidlee.github.io/seb-lab/lerobot-study/ecosystem.html)
- π0.5 first released April 2025 at ~3B params (vendor table). — [roboticscenter.ai (vendor)](https://www.roboticscenter.ai/tools/vla-models-comparison/)

**NVIDIA GR00T N1.7 (Isaac-GR00T)**
- Repo https://github.com/NVIDIA/Isaac-GR00T: N1.7 is current GA (previous N1.6, N1.5; no N2 mentioned on the page). Code Apache-2.0; weights under NVIDIA Open Model License. Inference: 1 GPU with 16 GB+ VRAM (RTX 4090, L40, H100, Jetson AGX Thor/Orin, DGX Spark). Fine-tuning: 1+ GPUs with 40 GB+ VRAM recommended (H100 or L40; A6000 works but slower). Benchmarks: H100 ~115.5 ms/step, L40 190.5 ms, RTX Pro 6000 Blackwell 119.3 ms (batch 1, two cameras); ~40 Hz on RTX PRO 6000 Blackwell and ~28 Hz on Jetson AGX Thor with TensorRT. Embodiments: SO-100 via `NEW_EMBODIMENT` (`examples/SO100`, demo `cube_to_bowl_5`), LIBERO_PANDA, OXE_DROID, SIMPLER_ENV, UNITREE_G1, UNITREE_G1_SONIC (whole-body via GEAR-SONIC). Tutorials: `finetune_new_embodiment.md`, `GR00T_inference.ipynb`, `data_preparation.md`, `hardware_recommendation.md`, deployment README (TensorRT/Spark/Thor/Orin), Docker. — [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)
- LeRobot v0.6.0 switched its GR00T integration from N1.5 to N1.7. — [LeRobot releases](https://github.com/huggingface/lerobot/releases)
- Secondary sources conflict on N1.7 licensing ("commercial licensing" vs "Apache 2.0") and mention "N2 previewed at GTC 2026" — not confirmed on the repo page. — [marktechpost (secondary)](https://www.marktechpost.com/2026/04/28/top-10-physical-ai-models-powering-real-world-robots-in-2026/)

**OpenVLA / OpenVLA-OFT, Octo**
- OpenVLA and OpenVLA-OFT are MIT-licensed; SmolVLA, X-VLA, and openpi are Apache-2.0 (vendor/secondary). OpenVLA size given as 7B or 7.5B depending on source. No 2026 maintenance/status updates for OpenVLA or Octo were found. — [presenc.ai (secondary)](https://presenc.ai/research/best-open-weight-robotics-vla-models-2026); [roboticscenter.ai (vendor)](https://www.roboticscenter.ai/vla-models/best-2026/)

**MolmoAct2 (Ai2, May 2026) — fully open**
- Paper "MolmoAct2: Action Reasoning Models for Real-world Deployment" (arXiv 2605.02881): model weights, training code, and complete training data released; "deployable out-of-the-box on multiple embodiments"; results reported against OpenVLA-OFT on bimanual YAM tasks. Added to LeRobot in v0.7.0. — [arXiv 2605.02881](https://arxiv.org/html/2605.02881v1); [Ai2 page](https://allenai.org/papers/molmoact2); [LeRobot releases](https://github.com/huggingface/lerobot/releases)

**Gemini Robotics (Google DeepMind)**
- Gemini Robotics On-Device announced 24 June 2025 (runs locally on robot hardware); "Gemini Robotics On-Device 2" model card published 30 July 2026, distributed only to Trusted Testers (not openly available). — [DeepMind blog June 2025](https://deepmind.google/blog/gemini-robotics-on-device-brings-ai-to-local-robotic-devices/); [On-Device 2 model card](https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/)

**Figure Helix / RT-2**
- No open weights found for Figure Helix in this research (no search hit; see Gaps). RT-2 weights were never released; RT-2-X and RT-1-X are described on the OXE site as models trained on the OXE mixture (no download link stated). — [OXE site](https://robotics-transformer-x.github.io/)

**Consumer-GPU runnability landscape (Oct 2026, vendor comparisons)**
- A vendor comparison names π0.5, GR00T N1.7, and MolmoAct2 as "the leading open-weight VLAs in October 2026" and says π0.5 runs on an 8 GB GPU for inference. A Yotta Labs benchmark says π0.5 gives "deployable latency everywhere — even on a consumer GPU" but Lingbot-VLA on an RTX 4090 takes 10.2 s/action — viability is model-specific. TurboVLA (0.2B) claims 0.9 GB VRAM / 32 Hz on an RTX 4090 (authors' claim). — [roboticscenter.ai best-2026 (vendor)](https://www.roboticscenter.ai/vla-models/best-2026/); [Yotta Labs benchmark (vendor)](https://www.yottalabs.ai/post/vla-inference-gpu-benchmarks.md); [TurboVLA summary (secondary)](https://ai-tldr.dev/releases/h-embodvis-turbovla/index.md)

### Inferences
- For a learner with one 24 GB consumer GPU (RTX 3090/4090): train ACT/Diffusion from scratch, fine-tune SmolVLA, run π0.5 and GR00T N1.7 *inference*, and do π0 LoRA fine-tuning at the edge of memory. Full π0/GR00T fine-tuning requires rented 40–80 GB GPUs (HF Jobs, RunPod, etc.).
- With 12–16 GB (RTX 3060/4070/4080): ACT, VQ-BeT, TDMPC comfortably; Diffusion at small batch; SmolVLA with frozen vision encoder. With no GPU: Colab/HF Jobs; LeRobot explicitly says do not train on CPU.
- The three "has-a-tutorial" models for learners are SmolVLA (LeRobot docs + OpenELAB), GR00T N1.7 (Isaac-GR00T getting_started + NVIDIA SO-101 path), and π0.x (openpi examples; LeRobot checkpoints).

### Gaps
- No primary-source confirmation of Figure Helix openness (assumed closed; not searched directly) or of a GR00T "N2".
- π0.6 or later Physical Intelligence releases: openpi page does not mention them; one secondary source says later PI models have no open weights.
- OpenVLA/Octo 2026 maintenance status unverified; exact SmolVLA param count conflicts (450M vs 500M) across secondary sources.

---

## Key Question 4: Reading lists / surveys / blog explainers

### Takeaway
The strongest curated entry points are the HF "Robot Learning: A Tutorial" (arXiv 2510.12403) and three actively revised arXiv surveys (VLA survey 2405.14093 v7 Feb 2026; Efficient VLA survey 2510.24795 v2 Feb 2026; VLA datasets/benchmarks survey 2604.23001 Apr 2026), plus GitHub awesome lists (awesome-vla-study for a recommended reading order; yueen-ma/Awesome-VLA as the survey companion; wadeKeith/Awesome-Embodied-AI for breadth). For explainers, Sergey Levine's long-form interviews (Dwarkesh Sept 2025; TWIML Feb 2025) and Interconnects' "A realistic path to robotic foundation models" are more accessible than papers; no robotics post by Lilian Weng and no standalone Chris Paxton blog explainer were found.

### Cited Findings

**Surveys (2024–2026)**
- "A Survey on Vision-Language-Action Models for Embodied AI" (arXiv 2405.14093): first posted May 2024, revised to v7 in Feb 2026; taxonomy of VLAs into three lines of research; companion repo https://github.com/yueen-ma/Awesome-VLA. — [arXiv 2405.14093 v7](https://arxiv.org/html/2405.14093v7)
- "A Survey on Efficient Vision-Language-Action Models" (arXiv 2510.24795, v2 Feb 2026): "first comprehensive review of Efficient VLAs across the entire model-training-data pipeline". — [arXiv 2510.24795](https://arxiv.org/abs/2510.24795v2)
- "Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines" (arXiv 2604.23001, Apr 2026): argues future advances depend on "co-designing high-fidelity data engines and structured evaluation protocols". — [arXiv 2604.23001](https://arxiv.org/html/2604.23001)
- Preprints.org (non-arXiv) 2026 surveys: an evaluation-focused VLA survey covering 582 papers (2023–May 2026); a VLA/VLM manipulation review (4 June 2026). — [Preprints 202606.0425](https://www.preprints.org/manuscript/202606.0425)
- "Survey of Vision-Language-Action Models for Embodied Manipulation" (literature review summary). — [themoonlight.io](https://www.themoonlight.io/en/review/survey-of-vision-language-action-models-for-embodied-manipulation)

**GitHub awesome lists**
- MilkClouds/awesome-vla-study — "structured reading list that guides users from foundational generative concepts to state-of-the-art robot foundation models, data scaling, RL fine-tuning, and world models", papers in recommended reading order (closest thing to a curriculum). — [awesome-vla-study](https://relatedrepos.com/gh/MilkClouds/awesome-vla-study)
- yueen-ma/Awesome-VLA — companion to the 2405.14093 survey. — [Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA)
- jiaaqiliu/Awesome-VLA-Robotics — papers, models, datasets, resources on VLA in robotics. — [awesome-vla-robotics](https://www.context-awesome.com/list/jiaaqiliu/awesome-vla-robotics)
- jonyzhang2023/awesome-embodied-vla-va-vln — VLA, World-Action-Model, VLN, VA, MLLM-based embodied learning. — [GitHub](https://github.com/jonyzhang2023/awesome-embodied-vla-va-vln)
- wadeKeith/Awesome-Embodied-AI — surveys, VLA models, datasets, simulators, humanoids, robot learning, safety. — [ecosyste.ms listing](https://awesome.ecosyste.ms/lists/wadekeith%2Fawesome-embodied-ai)
- Psi-Robot/Awesome-VLA-Papers; KwanWaiPang/Awesome-VLA; DravenALG/awesome-vla-wam (VLA + World Action Models); OpenHelix-Team/Awesome-VLA-RL and Denghaoyuan123/Awesome-RL-VLA (RL fine-tuning of VLAs). — [Psi-Robot](https://github.com/Psi-Robot/Awesome-VLA-Papers); [KwanWaiPang](https://github.com/KwanWaiPang/Awesome-VLA); [awesome-vla-wam](https://github.com/DravenALG/awesome-vla-wam); [Awesome-RL-VLA](https://github.com/Denghaoyuan123/Awesome-RL-VLA)
- No repository named exactly "awesome-robot-learning" surfaced in search.

**Blog / podcast explainers**
- Sergey Levine on Dwarkesh Patel (12 Sept 2025): how VLA models work, self-improvement from deployment. — [dwarkesh.com](https://www.dwarkesh.com/p/sergey-levine)
- TWIML "π0: A Foundation Model for Robotics with Sergey Levine" (Feb 2025). — [TWIML](https://twimlai.com/go/719)
- Levine + Liyiming Ke, "Robotic Foundation Models" talk at Actuate (Foxglove). — [Actuate recording](https://actuate.foxglove.dev/recordings/robotic-foundation-models)
- Interconnects (Nathan Lambert), "A realistic path to robotic foundation models". — [interconnects.ai](https://www.interconnects.ai/p/robotic-foundation-models)
- RoboPapers podcast (Chris Paxton co-host), e.g. Ep. 52 on "Probe, Learn, Distill" residual actors on top of a frozen VLA. — [RoboPapers](https://robopapers.substack.com/p/ep52-probe-learn-distill-self-improving)
- DataCamp "Vision Language Action Models Explained" (a VLA "takes the same kind of input as a VLM and produces an action instead"); Markaicode VLA explainer comparing RT-2 / OpenVLA / π0 action outputs and noting OXE's ~1M trajectories from 20+ robot types. — [DataCamp](https://www.datacamp.com/tutorial/vision-language-action-models-explained); [markaicode](https://www.markaicode.com/vla-models-explained/)
- Practitioner field report: ML6 "AI Robotics: a field report on imitation learning with LeRobot" — "if the policy cannot explore environments independently, it will need data, and lots of it". — [ML6 blog](https://www.ml6.eu/en/blog/ai-robotics-a-field-report-on-imitation-learning-with-lerobot)

### Inferences
- A reasonable reading order for the capstone tier: HF Tutorial (2510.12403) → Interconnects/Levine interviews for the "why" → 2405.14093 survey sections on architectures → awesome-vla-study's ordered list for depth → 2604.23001 for data/benchmark literacy before attempting fine-tuning.

### Gaps
- Lilian Weng (Lil'Log) has no robotics post in 2025–26 found; her older posts (e.g., on diffusion models) were not fetched and are not cited here.
- Chris Paxton's personal blog was not located; only the RoboPapers podcast he co-hosts.
- Physical Intelligence blog posts and BAIR blog posts were not fetched directly.

---

## Key Question 5: Sim-to-real and RL for locomotion (legged_gym / Isaac Lab locomotion, Unitree Go2/G1 examples, RMA / "walk these ways" lineage) — learner-friendly tutorials?

### Takeaway
Learner-friendly locomotion on-ramps now exist at three levels: NVIDIA's free Isaac Lab/Newton courses and the ANYmal-D quadruped Newton tutorial; Unitree's official RL repos (unitree_rl_gym on legged_gym/Isaac Gym, unitree_rl_lab on Isaac Lab, unitree_rl_mjlab on MuJoCo/mjlab) with a sim2sim-in-MuJoCo step before hardware; and Genesis's minimal Go2 PPO walking tutorial. All train velocity-tracking policies with RSL-RL PPO and export ONNX for deployment. Direct learner tutorials for the RMA / "walk these ways" papers were not found in this pass.

### Cited Findings
- NVIDIA blog: "complete train, validate, and deploy workflow that trains an ANYmal-D quadruped locomotion policy with Newton in Isaac Lab"; companion post "Train a Quadruped Locomotion Policy and Simulate Cloth Manipulation with NVIDIA Isaac Lab and Newton". — [NVIDIA blog Newton](https://developer.nvidia.com/blog/newton-adds-contact-rich-manipulation-and-locomotion-capabilities-for-industrial-robotics); [NVIDIA quadruped tutorial](https://developer.nvidia.com/blog/train-a-quadruped-locomotion-policy-and-simulate-cloth-manipulation-with-nvidia-isaac-lab-and-newton)
- NVIDIA Physical AI Learning: "Transferring Robot Learning Policies From Simulation to Reality" and "Accelerating Robot Learning With Isaac Lab and Newton" courses (free). — [NVIDIA Physical AI Learning](https://docs.nvidia.com/learning/physical-ai/)
- Community tutorial "A Tutorial on Developing Reinforcement Learning Environments for Legged Robots in Isaac Lab — From Quadrupedal Locomotion to Humanoid Challenges" (Notion). — [Notion tutorial](https://marble-resistance-175.notion.site/A-Tutorial-on-Developing-Reinforcement-Learning-Environments-for-Legged-Robots-in-Isaac-Lab-25e59724dbdf80b5b6c6c2dbd9ea6b66)
- Unitree RL GYM (legged_gym-based): "complete pipeline from training in Isaac Gym to Sim2Sim (Mujoco) and Sim2Real physical deployment"; tasks go2, g1, h1, h1_2. — [unitree_rl_gym docs index](https://docsearch.algolia.com/mcp/docs/repo/unitreerobotics/unitree_rl_gym)
- Unitree RL Lab (Isaac Lab-based): supports Go2, H1, G1-29dof; workflow includes a sim2sim step in MuJoCo before real deployment. — [unitree_rl_lab mirror](https://gitee.com/hilbertw/unitree_rl_lab)
- Unitree RL Mjlab: "built upon the mjlab, using MuJoCo as its physics simulation backend, currently supporting Unitree Go2, A2, As2, G1, R1, H1_2 and H2"; velocity tasks `Unitree-Go2-Flat`, `Unitree-G1-Flat`; training exports `policy.onnx`; recommends testing in `unitree_mujoco` before hardware. — [unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab)
- Genesis Go2 tutorial: PPO from rsl-rl, 50 Hz control, ~20 ms modeled action latency, deployable joint-position policy. — [Genesis locomotion tutorial](https://genesis-world.readthedocs.io/en/latest/user_guide/policy_training/examples/locomotion.html)
- MuJoCo Playground 1.0: Unitree G1 whole-body motion tracking with RSL-RL; SO-101 zero-shot sim-to-real pick-cube. — [GitHub](https://github.com/google-deepmind/mujoco_playground)
- mjlab: G1 velocity and motion-tracking tasks, Colab notebook, `uvx` demo. — [mjlab](https://github.com/mujocolab/mjlab)
- Vendor guides for other platforms: LimX Dynamics TRON1 "RL Training and Deployment Guide (Isaac Lab)" (Jan 2026, Isaac Lab 2.x-era); UBTech Walker/Tien Kung "gait training and deployment". — [LimX](https://www.limxdynamics.com/en/documents/800015958042349568); [UBTech](https://docs.ubtrobot.com/walker-tienkung/en/docs/gait-training-and-deployment)
- Recent sim-to-real evidence: GS-Playground (arXiv 2604.25459) reports Go2 velocity tracking and G1 23-DoF balancing/walking transfer. — [arXiv 2604.25459](https://arxiv.org/pdf/2604.25459)
- RoboVerse wiki has a "Unitree RL" RL section. — [roboverse.wiki](https://roboverse.wiki/roboverse_learn/reinforcement_learning/unitree_rl)

### Inferences
- The locomotion "lineage" (legged_gym → Isaac Gym → Isaac Lab → MuJoCo Warp/mjlab) is now reflected in Unitree's three parallel repos; a learner without a quadruped can still complete the full train→sim2sim(MuJoCo)→ONNX export loop, which is the learner-appropriate stopping point.
- Isaac Lab 3.0's Newton-only install and mjlab's `uvx` demo make GPU locomotion RL feasible on a single Turing+ NVIDIA GPU without Isaac Sim; the 32 GB RAM / 16 GB VRAM guidance applies only when Isaac Sim rendering is needed.

### Gaps
- No learner tutorial specifically covering RMA (Rapid Motor Adaptation) or "Walk These Ways" was surfaced; those remain paper-plus-code repos (not verified here).
- Isaac Lab official locomotion tutorial page (docs "Tutorials" index) was not fetched; only NVIDIA blog tutorials confirmed.
- Hardware costs for Go2/G1 and whether a learner can realistically own one were out of scope.

---

## Key Question 6: Community sentiment — recommended learning path (ML background vs classical background) and realistic GPU needs

### Takeaway
Evidence is thin and mostly secondary (Reddit mirrors, blogs, job postings), but it converges: classical-robotics commenters insist that ROS is not robotics and that kinematics/dynamics/control come first; ML-background advice points to starting with behavioral cloning on a cheap arm or in sim and treating data collection as the core skill; employers in 2026 ask for hands-on imitation learning (ACT/diffusion/VLA) deployed on real hardware. On compute, the authoritative LeRobot guide puts a 24 GB consumer GPU (RTX 3090/4090) as the sweet spot, a 12 GB laptop GPU as sufficient for ACT, and rented A100-class GPUs for VLA fine-tuning.

### Cited Findings
- r/AskRobotics threads (Feb–May 2026, via mirror): commenters argue "learning ROS is not learning robotics, since it is mostly system programming and orchestration" and recommend kinematics, dynamics, control theory, and motion planning before ros2_control/Nav2; for learning-based robotics, threads suggested starting to "teach robots new skills with VLAs" and focusing on PyTorch for behavioral cloning. — [Reddit mirror (AskRobotics, 2026)](https://reddit.sentinel-team.org/subreddits/AskRobotics/snapshots/2026-04-03T16%3A02%3A43.268571Z)
- r/AskRobotics GPU thread (Apr 2025): debate between cheaper 12 GB cards (RTX 3060) and a ~5070 Ti budget for robotics RL. — [redlib mirror](https://redlib.hbubli.cc/r/AskRobotics/comments/1jsmh3d/gpu_recommendation_for_robotics_and_reinforcement)
- NVIDIA developer forum: user on RTX 3060 asking how much a 3090/4090 upgrade speeds IsaacGym training (no verified speed ratio found). — [NVIDIA forums](https://forums.developer.nvidia.com/t/gpu-upgrade-impact-on-isaacgym-training-speed-rtx-3060-to-3090-4090/299424)
- Hacker News (mirror) thread on choosing an xArm over an SO-101 for a first arm (no training-time data). — [HN mirror item 48586329](https://pr-879-hackernews.vinext.workers.dev/item/48586329)
- A student report (LinkedIn, secondary) estimates a small policy consuming ~20 GB VRAM and ~12 hours; LeRobot's official guide instead anchors ACT at ~2–6 GB and ~30–60 min on a 4090 for 5 epochs/50 episodes — the discrepancy illustrates how step count and resolution dominate. — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide)
- 2026 job postings for robot-learning engineers commonly require "hands-on imitation learning or behavior cloning experience on physical systems", "practical depth in imitation learning and at least one modern policy family, such as vision-language-action models, diffusion policies, or action-chunking transformers", experience with "behavior cloning, PPO, SAC, DAgger", policies "deployed on real robot hardware — not just in simulation", and ROS familiarity. — [Built In posting](https://builtin.com/job/machine-learning-engineer-robotics-embodied-ai/9325208); [Bedrock Robotics posting](https://job-boards.greenhouse.io/bedrockrobotics/jobs/4802452008); [Applied Intuition posting](https://jobs.generalcatalyst.com/companies/applied-intuition/jobs/94283530-robot-learning-engineer-manipulation)
- ML6 field report: data is the bottleneck for imitation learning with LeRobot. — [ML6](https://www.ml6.eu/en/blog/ai-robotics-a-field-report-on-imitation-learning-with-lerobot)
- Hugging Face Discord is the official LeRobot support channel (invite in docs). — [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)
- "VLA fine-tunes on a single 24 GB consumer GPU in hours" (vendor guide, model unnamed). — [roboticscenter.ai (vendor)](https://br.roboticscenter.ai/blog/scaling-vla-training-on-a-budget)

### Inferences
- Path for an ML-background developer: skip straight to LeRobot (dataset → ACT → SmolVLA fine-tune) in sim/LIBERO or on an SO-101, then backfill Tedrake's Underactuated chapters and a classical control module when sim-to-real gaps bite (calibration, latency, dynamics). Path for a classical-robotics developer: start with Isaac Lab/mjlab PPO locomotion (familiar control framing), then CS 285 lectures 1–6 and the HF Tutorial for BC/VLA.
- Compute tiers (synthesis of the LeRobot guide + openpi + GR00T): no GPU → Colab/HF Jobs; 12 GB → ACT/VQ-BeT/TDMPC and small-batch diffusion; 24 GB → everything except full VLA fine-tuning; 40–80 GB (rented) → π0/GR00T fine-tuning. For Isaac Lab 3.0 with Newton, any Turing+ NVIDIA GPU works headless; 16 GB VRAM + 32 GB RAM if Isaac Sim rendering is required.

### Gaps
- No primary r/reinforcementlearning or X/Twitter researcher threads were retrievable (search returned mirrors/aggregators); sentiment claims above rest on a small number of threads.
- No Hugging Face Discord content is indexed; recommendations there could not be cited.
- No verified 3060-vs-4090 throughput ratio for Isaac Lab/IsaacGym.

---

## Key Question 7 (synthesis): How this layer fits on top of classical fundamentals — prerequisites, hardware/compute, and a beginner-to-intermediate on-ramp

### Takeaway
The AI layer assumes (i) Python + PyTorch fluency, (ii) basic probability/linear algebra, (iii) classical robotics concepts the earlier tiers already cover (kinematics, joint-space control, calibration, simulation), and (iv) a clear mental model of RL vs. imitation learning. The on-ramp that the sources support is: HF Robotics Course → HF Tutorial with LeRobot in sim → one CPU-level RL run (Gymnasium-Robotics/robosuite or MuJoCo Playground CPU) → SO-101 ACT on real hardware → SmolVLA fine-tune → optional GPU locomotion RL in Isaac Lab 3.0/mjlab. Tedrake's books and CS 285 supply the theory on demand.

### Cited Findings
- HF course prerequisites: basic Python; linear algebra/calculus helpful; ML familiarity "a bonus"; no robot required. — [HF Robotics Course](https://huggingface.co/learn/robotics-course)
- CS 224R expects deep-learning familiarity (incl. transformers) and basic RL, PyTorch assignments. — [CS 224R notes (secondary)](https://web.stanford.edu/~srliu/homepage/notes/cs224r/)
- NVIDIA Newton course requires comfort with Python. — [NVIDIA Newton course](https://docs.nvidia.com/learning/physical-ai/getting-started-with-newton/latest/index.html)
- LeRobot SO-101 docs stress calibration "because it allows a neural network trained on one robot to work on another" — a classical-skills dependency. — [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)
- Tedrake's Manipulation book places RL (Ch. 11) after pick-and-place, pose estimation, motion planning, and manipulator control (Ch. 3–8); Underactuated places Model-Free Policy Search (Ch. 20) and Imitation Learning (Ch. 21) after DP/LQR/trajectory optimization. — [manipulation.mit.edu](https://manipulation.mit.edu/); [underactuated.mit.edu](https://underactuated.mit.edu/)
- LeRobot: imitation learning converges in 5–10 epochs; ACT on a 24 GB GPU in under an hour; CPU-only "Don't train". — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide)
- Isaac Lab 3.0 runs without Isaac Sim (Newton default; Turing+ GPU; headless needs no RTX). — [Isaac Lab installation](https://isaac-sim.github.io/IsaacLab/main/source/isaaclab/installation.html)

### Inferences
- Suggested capstone module sequence (each item maps to cited resources above): (1) Concepts: HF Course U0–U2 + Tutorial §RL/§BC (free, ~3–5 h). (2) First RL: Gymnasium-Robotics Fetch/Hand or MuJoCo Playground CartpoleBalance on CPU with SB3/RSL-RL (free). (3) First imitation learning: LeRobot ACT on a Hub dataset (LIBERO/MetaWorld) — Colab or 12 GB GPU. (4) Real robot: SO-101 build + teleop + 50-episode dataset + ACT (24 GB GPU or HF Jobs). (5) Foundation model: SmolVLA fine-tune on the same dataset; GR00T/π0.5 inference only. (6) Optional locomotion: Isaac Lab 3.0 or mjlab Unitree G1/Go2 velocity task → ONNX → MuJoCo sim2sim. (7) Theory backfill: Tedrake Ch. 20–21 (Underactuated), Ch. 9–11 (Manipulation); CS 285 lectures on BC/policy gradient/offline RL.
- Hardware budget tiers implied: $0 (sim + Colab/HF Jobs), low (SO-101 pair + used RTX 3060 12 GB), mid (SO-101 pair + RTX 3090/4090 24 GB), rented cloud for VLA fine-tuning.

### Gaps
- No single source prescribes this exact sequence; it is a synthesis. SO-101 kit pricing and Colab free-tier adequacy for LeRobot ACT were not verified in this pass.
