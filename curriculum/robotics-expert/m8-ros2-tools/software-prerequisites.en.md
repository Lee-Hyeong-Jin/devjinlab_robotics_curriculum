---
id: m8-software-prerequisites
lang: en
title: Software basics to check before ROS 2
summary: Where people get stuck in ROS 2 practice is more often the shell, Git, the C++ build, Python packaging or networking than robotics. Check with self-check questions how far you need to know each of the five areas, and follow the free resources for the ones you are short on.
objectives:
  - "Explain the difference between `source` and running a script, and check which environment variables and workspace the current shell sees."
  - Read the first line of a CMake configure error, a compile error and a link error, and tell whether a package, a header or a link setting is missing.
  - Say, in order, what to check on the network when the ROS 2 nodes of two containers or two computers do not see each other.
tags: [ros2, linux, shell, git, cmake, python-packaging, networking, prerequisites]
---

# Software basics to check before ROS 2

Most people who give up on the ROS 2 tutorials are not stuck on robotics. They are stuck on
`ros2: command not found`, on a CMake error they cannot read, or on a node on the next computer
that does not show up. ROS 2 sits on top of the Linux shell, a build system and a network, and its
tutorials assume the reader knows them. This lesson teaches nothing new. It fixes **what you need
to know and how far**, and points to where to learn what is missing. You do not need all five
areas: top up only the ones whose self-check question you could not answer, then come back.

## Where you will use this

From the next lesson on you create a workspace (`colcon build`), source environments and start
nodes in several terminals. On a real robot you log in to the on-board computer over SSH, fetch
someone else's package with Git and build it, and put robot and laptop on one network. Without
these five basics every ROS 2 error looks equally large and equally opaque. With them, errors sort
themselves into "a sourcing problem", "a dependency problem" and "a network problem".

## Concepts

### 1. The shell and environment variables

**How far:** moving around and handling files (`cd`, `ls`, `cp`, `mv`, `rm`, `cat`, `grep`),
reading environment variables (`echo $PATH`, `printenv`), when `~/.bashrc` runs, and what `source`
does.

`source setup.bash` runs the script **inside the current shell**, so the environment variables it
changes stay. `bash setup.bash` starts a new shell to run it, and the changes vanish with that
shell. "Sourcing" in ROS 2 means adding install paths to variables such as `PATH`,
`AMENT_PREFIX_PATH` and `PYTHONPATH`, which is why it has to be done in every terminal.

- Self-check: a new terminal says there is no `ros2` command. It worked yesterday. What do you check?
- Where to learn: The Missing Semester, "Course overview + the shell" and "Shell Tools and Scripting".

### 2. Git

**How far:** `clone`, `status`, `add`, `commit`, `log`, `diff`, creating and switching branches,
and fetching a given tag or branch (`git clone -b jazzy <url>`). ROS 2 repositories often keep one
branch per distribution, and the wrong branch breaks the build.

- Self-check: a package you fetched does not build. How do you check that the branch you have is
  the one for your distribution?
- Where to learn: Pro Git, chapters 1–3.

### 3. The C++ build and CMake

**How far:** you do not need to write C++ well. Know the order source → compile → link, and be
able to read what `find_package`, `add_executable`, `target_link_libraries` (in ROS 2,
`ament_target_dependencies`) and `install` do in a `CMakeLists.txt`. And read errors **from the
first one at the top**.

| Step that failed | Typical message | Meaning |
|---|---|---|
| Configure (CMake) | `Could not find a package configuration file provided by "foo"` | The package `foo` is not installed, or not sourced |
| Compile | `fatal error: foo/bar.hpp: No such file or directory` | A header is not found: a `find_package` or a dependency declaration is missing |
| Link | `undefined reference to 'foo::Bar::baz()'` | Declared, but the library that implements it is not linked |

- Self-check: for each of the three messages, can you say where in `package.xml` and
  `CMakeLists.txt` you would look?
- Where to learn: the CMake Tutorial, steps 1–2, then the ament_cmake documentation.

### 4. Python packaging

**How far:** where `pip install` puts a package, why virtual environments (`python3 -m venv`)
exist, and that `import` looks for modules along `sys.path`. In a ROS 2 Python package
(`ament_python`), a name written under `entry_points` in `setup.py` becomes the executable name of
`ros2 run <package> <name>`.

On Ubuntu 24.04, `pip install` into the system Python fails with `externally-managed-environment`.
That is deliberate, to protect system packages. Install ROS 2 dependencies with `rosdep` and
`apt`, and other packages you experiment with into a virtual environment.

- Self-check: you get `ModuleNotFoundError`. How do you tell "not installed" from "installed, but
  this Python cannot see it"?
- Where to learn: "Installing Packages" in the Python Packaging User Guide.

### 5. Networking

**How far:** IP addresses and subnets, network interfaces (`lo`, `eth0`, `wlan0`, `docker0` in
`ip -brief addr`), `ping`, and the difference between unicast and **multicast**. ROS 2 nodes find
each other without a central server, by announcing "I am here" over multicast. So two nodes must
be on the same subnet, and no router, firewall or virtual network in between may block multicast.

This is also why two containers cannot see each other. By default a container is inside a virtual
network (a bridge) that Docker created, which is a different network from the containers of
another Compose project, from the host, and from the computer next to you.

- Self-check: laptop and robot are on the same Wi-Fi, but `ros2 node list` does not show the
  robot's nodes. Name three things to check, in order.
- Where to learn: the About domain ID page and the Docker networking overview. The order of fixes
  is under "If this failed" in L8.5.

```hint
The nodes of the laptop and the robot do not see each other
1. Does `ping <the other IP>` work? If not, this is a network problem, not a ROS problem.
2. Is `ROS_DOMAIN_ID` the same on both (`echo $ROS_DOMAIN_ID`; empty means 0)?
3. Run `ros2 multicast receive` on one side and `ros2 multicast send` on the other to see whether
   multicast gets through. School and company Wi-Fi often block traffic between devices, or
   multicast. A travel router of your own is then the quickest way out.
```

## Example

The error CMake gives when it cannot find a package. It is long, but there are two places to read.

```text
CMake Error at CMakeLists.txt:3 (find_package):
  ...
  Could not find a package configuration file provided by
  "sensor_driver_that_is_not_installed" with any of the following names:

    sensor_driver_that_is_not_installedConfig.cmake
    sensor_driver_that_is_not_installed-config.cmake

  Add the installation prefix of "sensor_driver_that_is_not_installed" to
  CMAKE_PREFIX_PATH or set "sensor_driver_that_is_not_installed_DIR" ...
```

The first line says **where** (`find_package` on line 3 of `CMakeLists.txt`), the middle says
**what** was not found (a package of that name). In ROS 2 the cause is usually one of two: the
package is not installed (`rosdep install --from-paths src -y --ignore-src`), or it is installed
but the workspace it lives in is not sourced.

**Exercise:** In a Linux or macOS terminal (or the container of L8.5) run the lines below one at a
time, writing down your prediction of the output before each. Explain in one sentence why (1)–(3)
differ.

```bash
bash -c 'export RC_DEMO=1'; echo "${RC_DEMO:-unset}"     # (1)
echo 'export RC_DEMO=1' > demo.sh
bash demo.sh; echo "${RC_DEMO:-unset}"                   # (2)
source demo.sh; echo "${RC_DEMO:-unset}"                 # (3)
python3 -c "import sys; print(sys.prefix == sys.base_prefix)"   # (4)
ip -brief addr                                           # (5) on macOS: ifconfig
```

```expected
| Line | Output | Why |
| --- | --- | --- |
| (1) | `unset` | `bash -c` is a child shell; an `export` made there disappears with it |
| (2) | `unset` | `bash demo.sh` also runs in a child shell |
| (3) | `1` | `source` runs in the current shell, so the variable stays |
| (4) | `True` | You are outside a virtual environment; in a terminal with one activated it prints `False` |
| (5) | a list of interfaces | `lo` (127.0.0.1) and at least one wired or wireless interface; with Docker installed, `docker0` and `br-…` as well |

The difference between (1)–(3) is the reason for `source /opt/ros/jazzy/setup.bash` in every
terminal: running a setup script with `bash` looks as if nothing happened. If (5) shows `docker0`
or `br-…`, you have seen for yourself that containers are on a different network from the host.
```

## Self-check questions

1. Why do `source install/setup.bash` and `bash install/setup.bash` have different results?
2. At which step of the build does `undefined reference to` appear, and where in CMakeLists.txt
   do you look?
3. Nodes started in two containers on the same PC do not see each other. What do you check first?

## How to study this stage

1. **Check (first):** answer the self-check question of each of the five areas out loud. Mark only
   the areas where you got stuck.
2. **Top up:** read the resource for each marked area, the stated part only. Do not try to read
   everything; one or two hours per area is enough.
3. **Practise:** do the exercise as predict → run → compare.
4. **Move on:** do not wait until it is perfect. When the next lesson really stops you, come back
   to the area in question. What you learn at the moment you need it stays best.

## References

- The Missing Semester of Your CS Education (MIT) - <https://missing.csail.mit.edu/>
- Pro Git - <https://git-scm.com/book/en/v2>
- CMake Tutorial - <https://cmake.org/cmake/help/latest/guide/tutorial/index.html>
- ament_cmake user documentation - <https://docs.ros.org/en/jazzy/How-To-Guides/Ament-CMake-Documentation.html>
- Python Packaging User Guide - <https://packaging.python.org/en/latest/tutorials/installing-packages/>
- About domain ID - <https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Domain-ID.html>
- Docker networking overview - <https://docs.docker.com/engine/network/>
