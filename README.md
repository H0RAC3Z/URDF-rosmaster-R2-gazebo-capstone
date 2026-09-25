## Quick Setup

Clone repository:
git clone <YOUR-GITHUB-REPOSITORY>
cd r2_ros2

Build image
docker build -t r2-ros2-humble -f docker/Dockerfile .

Give docker perms to the X display server:
xhost +local:docker

Run container 
docker run -d \
  --name r2-ros2 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "$(pwd):/root/r2_ros2" \
  r2-ros2-humble

Entry into bash on container:
docker exec -it r2-ros2 bash

Set up environment:
source /opt/ros/humble/setup.bash

colcon build --symlink-install

source install/setup.bash

export IGN_GAZEBO_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$IGN_GAZEBO_RESOURCE_PATH
export GZ_SIM_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$GZ_SIM_RESOURCE_PATH

Open gazebo on Docker:
ign gazebo -r empty.sdf

Open another terminal and enter the docker container:
docker exec -it r2-ros2 bash

Spawn the robot in that terminal that you opened:
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2

Rerunning:

Open another terminal inside the image:
docker exec -it r2-ros2 bash

Launch Gazebo
ign gazebo -r empty.sdf

Open another terminal and open another bash in the container:
docker exec -it r2-ros2 bash

Spawn robot in that new terminal:
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2

Navigate to the steering document to test steering.

Running the services/topics (REQUIRED TO TEST STEERING):
ros2 run ros_gz_bridge parameter_bridge \
  /clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock \
  /model/yahboom_r2_gazebo/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist \
  /model/yahboom_r2_gazebo/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry \
  /model/yahboom_r2_gazebo/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V \
  /world/empty/model/yahboom_r2_gazebo/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model \
  --ros-args \
  -r /model/yahboom_r2_gazebo/cmd_vel:=/cmd_vel \
  -r /model/yahboom_r2_gazebo/odometry:=/odom \
  -r /model/yahboom_r2_gazebo/tf:=/tf \
  -r /world/empty/model/yahboom_r2_gazebo/joint_state:=/joint_states


