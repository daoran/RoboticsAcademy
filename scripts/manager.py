#!/usr/bin/env python3
import sys
print(sys.path)

import asyncio
import websockets
import os
import threading
import time
import json


GAZEBO_RESOURCE_PATH = "export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH:"
DISPLAY = ":0"
GZCLIENT_EXERCISES = set(["follow_line", "obstacle_avoidance", "vacuum_cleaner", "vacuum_cleaner_loc", "color_filter", "drone_cat_mouse", "3dreconstruction", "follow_turtlebot", "global_navigation", "follow_road", "dl_digit_classifier", "human_detection"])

instructions = {
    "follow_line": {
        "gazebo_path": "/RoboticsAcademy/exercises/follow_line/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/follow_line/web-template/launch/simple_line_follower_ros_headless.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/follow_line/web-template/exercise.py 0.0.0.0",
        "instructions_gui": "python3 /RoboticsAcademy/exercises/follow_line/web-template/gui.py 0.0.0.0"
    },
    "obstacle_avoidance": {
        "gazebo_path": "/RoboticsAcademy/exercises/obstacle_avoidance/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/obstacle_avoidance/web-template/launch/obstacle_avoidance_f1_headless.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/obstacle_avoidance/web-template/exercise.py 0.0.0.0"
    },
    "vacuum_cleaner": {
        "gazebo_path": "/RoboticsAcademy/exercises/vacuum_cleaner/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/vacuum_cleaner/web-template/launch/vacuum_cleaner_headless.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/vacuum_cleaner/web-template/exercise.py 0.0.0.0"
    },
    "vacuum_cleaner_loc": {
        "gazebo_path": "/RoboticsAcademy/exercises/vacuum_cleaner_loc/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/vacuum_cleaner_loc/web-template/launch/vacuum_cleaner_headless.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/vacuum_cleaner_loc/web-template/exercise.py 0.0.0.0"
    },
    "color_filter": {
        "instructions_host": "python3 /RoboticsAcademy/exercises/color_filter/web-template/exercise.py 0.0.0.0"
    },
    "drone_cat_mouse": {
        "gazebo_path": "/RoboticsAcademy/exercises/drone_cat_mouse/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/drone_cat_mouse/web-template/launch/drone_cat_mouse.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/drone_cat_mouse/web-template/exercise.py 0.0.0.0"
    },
    "3dreconstruction": {
        "gazebo_path": "/RoboticsAcademy/exercises/3d_reconstruction/web-template/launch",
        "instructions_ros": [
            "/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/3d_reconstruction/web-template/launch/3d_reconstruction_ros.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/3d_reconstruction/web-template/exercise.py 0.0.0.0"
    },
    "follow_turtlebot": {
        "gazebo_path": "/RoboticsAcademy/exercises/follow_turtlebot/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/follow_turtlebot/web-template/launch/follow_turtlebot.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/follow_turtlebot/web-template/exercise.py 0.0.0.0"
    },
    "global_navigation": {
        "gazebo_path": "/RoboticsAcademy/exercises/global_navigation/web-template/launch",
        "instructions_ros": [
            "/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/global_navigation/web-template/launch/taxiholo_1_citylarge_headless.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/global_navigation/web-template/exercise.py 0.0.0.0"
    },
    "follow_road": {
        "gazebo_path": "/RoboticsAcademy/exercises/follow_road/web-template/launch",
        "instructions_ros": ["/opt/ros/noetic/bin/roslaunch ./RoboticsAcademy/exercises/follow_road/web-template/launch/follow_road.launch"],
        "instructions_host": "python3 /RoboticsAcademy/exercises/follow_road/web-template/exercise.py 0.0.0.0"
    },
    "dl_digit_classifier": {
        "instructions_host": "python3 /RoboticsAcademy/exercises/dl_digit_classifier/web-template/exercise.py 0.0.0.0"
    },
    "human_detection": {
        "instructions_host": "python3 /RoboticsAcademy/exercises/human_detection/web-template/exercise.py 0.0.0.0"
    },
}


def export_gazebo(exercise):
    gazebo_path = GAZEBO_RESOURCE_PATH + instructions[exercise]["gazebo_path"] + ";"
    return gazebo_path


def ros_instructions(exercise):
    roslaunch_cmd = '/bin/sh -c "export PWD="/";' \
                    'chmod +rwx /;' \
                    'export DISPLAY=:0;' \
                    'export OLDPWD=/etc/ros/rosdep;' \
                    'export LD_LIBRARY_PATH=/opt/ros/noetic/lib:/usr/lib/x86_64-linux-gnu/gazebo-11/plugins;' \
                    'export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:$GAZEBO_MODEL_PATH;' \
                    'export GAZEBO_MODEL_DATABASE_URI=http://gazebosim.org/models;' \
                    'export ROS_DISTRO=noetic;' \
                    'export PKG_CONFIG_PATH=/opt/ros/noetic/lib/pkgconfig;' \
                    'export OGRE_RESOURCE_PATH=/usr/lib/x86_64-linux-gnu/OGRE-1.9.0;' \
                    'export SHLVL=1;' \
                    'export GAZEBO_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:${GAZEBO_PLUGIN_PATH};' \
                    'export TERM=xterm;' \
                    'export ROS_VERSION=1;' \
                    'export GAZEBO_MASTER_URI=http://localhost:11345;' \
                    'ROS_ETC_DIR=/opt/ros/noetic/etc/ros;' \
                    'export CMAKE_PREFIX_PATH=/opt/ros/noetic;' \
                    'export ROS_PACKAGE_PATH=/opt/ros/noetic/share;' \
                    'chmod +x /opt/ros/noetic/bin/rosmaster;' \
                    'export PYTHONPATH=/opt/ros/noetic/lib/python3/dist-packages;' \
                    'chmod +x /opt/ros/noetic/bin/roslaunch;' \
                    'export ROS_ROOT=/opt/ros/noetic/share/ros;' \
                    'export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH;' \
                    'export ROS_MASTER_URI=http://localhost:11311;' \
                    'export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;' \
                    'export ROS_PACKAGE_PATH=/opt/ros/noetic/share:/PX4-Autopilot:/PX4-Autopilot/Tools/sitl_gazebo:/catkin_ws/src/drone_wrapper:/catkin_ws/src/drone_assets;'
    roslaunch_cmd = roslaunch_cmd + export_gazebo(exercise)
    for instruction in instructions[exercise]["instructions_ros"]:
        roslaunch_cmd = roslaunch_cmd + instruction + ";"
    roslaunch_cmd = roslaunch_cmd + '"'
    return roslaunch_cmd


def start_gzclient(exercise, width, height):
    # Configure browser screen width and height for gzclient
    gzclient_config_cmds = ["echo [geometry] > ~/.gazebo/gui.ini;",
                            "echo x=0 >> ~/.gazebo/gui.ini;",
                            "echo y=0 >> ~/.gazebo/gui.ini;",
                            f"echo width={width} >> ~/.gazebo/gui.ini;",
                            f"echo height={height} >> ~/.gazebo/gui.ini;"]

    # Write display config and start gzclient
    gzclient_cmd = (f"export DISPLAY={DISPLAY};" +
                    export_gazebo(exercise) +
                    "".join(gzclient_config_cmds) +
                    "gzclient --verbose")
    gzclient_thread = DockerThread(gzclient_cmd)
    gzclient_thread.start()

def start_console(width, height):
    # Write display config and start the console
    width = int(width) / 10; height = int(height) / 18
    console_cmd = f"export DISPLAY=:1;"
    console_cmd += f"xterm -geometry {int(width)}x{int(height)} -fa 'Monospace' -fs 10 -bg black -fg white"

    console_thread = DockerThread(console_cmd)
    console_thread.start()

def start_vnc(display, internal_port, external_port):
    # Start VNC server without password, forever running in background
    x11vnc_cmd = f"x11vnc -display {display} -nopw -forever -xkb -bg -rfbport {internal_port}"
    x11vnc_thread = DockerThread(x11vnc_cmd)
    x11vnc_thread.start()

    # Start noVNC with default port 6080 listening to VNC server on 5900
    novnc_cmd = f"/noVNC/utils/launch.sh --listen {external_port} --vnc localhost:{internal_port}"
    novnc_thread = DockerThread(novnc_cmd)
    novnc_thread.start()

def start_exercise(exercise):
    host_cmd = instructions[exercise]["instructions_host"]
    host_thread = DockerThread(host_cmd)
    host_thread.start()

    try:
        gui_cmd = instructions[exercise]["instructions_gui"]
        gui_thread = DockerThread(gui_cmd)
        gui_thread.start()
    except KeyError:
        pass

async def kill_simulation():
    cmd_gzweb = "pkill -9 -f exercise.py"
    os.popen(cmd_gzweb)
    cmd_gui = "pkill -9 -f gui.py"
    os.popen(cmd_gui)
    cmd_host = "pkill -9 -f node"
    os.popen(cmd_host)
    cmd_host = "pkill -9 -f gzserver"
    os.popen(cmd_host)
    cmd_client = "pkill -9 -f gzclient"
    os.popen(cmd_client)
    cmd_ros = "pkill -9 -f roslaunch"
    os.popen(cmd_ros)
    cmd_rosout = "pkill -9 -f rosout"
    os.popen(cmd_rosout)
    cmd_mel = "pkill -9 -f melodroot"
    os.popen(cmd_mel)
    cmd_rosout = "pkill -9 -f rosout"
    os.popen(cmd_rosout)
    cmd_x11vnc = "pkill -9 -f x11vnc"
    os.popen(cmd_x11vnc)
    cmd_novnc = "pkill -9 -f launch.sh"
    os.popen(cmd_novnc)
    os.popen(cmd_novnc)
    cmd_console = "pkill -9 -f tilda"
    os.popen(cmd_console)
    """cmd_py = "pkill -9 -f python3"
    os.popen(cmd_py)"""


class DockerThread(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd

    def run(self):
        stream = os.popen(self.cmd)
        out = stream.read()
        print(out)
        

async def hello(websocket, path):
    # name = await websocket.recv()
    print(websocket)
    async for name in websocket:
        print(name)
        data = json.loads(name)
        command = data["command"]
        if command == "open":
            print("> Starting simulation")
            xserver_cmd = "/usr/bin/Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile ./xdummy.log -config ./xorg.conf :0"
            xserver_thread = DockerThread(xserver_cmd)
            xserver_thread.start()

            # X Server for Console
            console_xserver_cmd = "/usr/bin/Xorg -noreset +extension GLX +extension RANDR +extension RENDER -logfile ./console_xdummy.log -config ./xorg.conf :1"
            console_xserver_thread = DockerThread(console_xserver_cmd)
            console_xserver_thread.start()

            # Start the exercise
            start_exercise(data["exercise"])

            if data["exercise"] not in ["color_filter", "dl_digit_classifier", "human_detection"]:
                roslaunch_cmd = ros_instructions(data["exercise"])
                roslaunch_thread = DockerThread(roslaunch_cmd)
                roslaunch_thread.start()
                time.sleep(5)

                if (data["exercise"] in GZCLIENT_EXERCISES):
                    # Start x11vnc servers
                    start_vnc(DISPLAY, 5900, 6080)
                    start_vnc(":1", 5901, 1108)

                    # Start gazebo client
                    width = data.get("width", 1920)
                    height = data.get("height", 1080)
                    start_gzclient(data["exercise"], width, height)
                    start_console(width, height)
                else:
                    gzweb_cmd = 'cd /gzweb; npm start -p 8080'
                    gzweb_thread = DockerThread(gzweb_cmd)
                    gzweb_thread.start()
            else:
                if (data["exercise"] in GZCLIENT_EXERCISES):
                    start_vnc(":1", 5900, 1108)
                    start_console(1920, 1080)

        elif command == "resume":
            print("RESUME SIMULATIOn")
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/unpause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif command == "stop":
            print("STOP SIMULATIOn")
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/pause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif command == "start":
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/unpause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif command == "reset":
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/reset_simulation"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        else:
            print("ALL KILED")
            await kill_simulation()

        greeting = f"Hello {name}!"

        await websocket.send("Done")
        # print(f"> {greeting}")

start_server = websockets.serve(hello, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
