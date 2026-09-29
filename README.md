# Quick Setup

### 1. Clone repository
```
git clone git@github.com:H0RAC3Z/URDF-rosmaster-R2-gazebo-capstone.git
```   
```
cd URDF-rosmaster-R2-gazebo-capstone/
```   

### 2. Build image
```
docker build -t r2-ros2-humble -f docker/Dockerfile .
```   

### 3. Give docker perms to the X display server
```
xhost +local:docker
```   

### 4. Run container
```
docker run -d \
  --name r2-ros2 \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "$(pwd):/root/r2_ros2" \
  r2-ros2-humble
```   

### 5. Entry into bash on container
```
docker exec -it r2-ros2 bash
```   

### 6. Set up environment
```
source /opt/ros/humble/setup.bash

colcon build --symlink-install

source install/setup.bash

export IGN_GAZEBO_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$IGN_GAZEBO_RESOURCE_PATH
export GZ_SIM_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$GZ_SIM_RESOURCE_PATH
```   

### 7. Open gazebo on Docker
```
ign gazebo -r empty.sdf
```   

### 8. Open another terminal and enter the docker container
```
docker exec -it r2-ros2 bash
```   

### 9. Spawn the robot in that terminal that you opened
```
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2
```   

# Rerunning

### 1. Open another terminal inside the image
```
docker exec -it r2-ros2 bash
```   

### 2. Launch Gazebo
```
ign gazebo -r empty.sdf
```   

### 3. Open another terminal and open another bash in the container
```
docker exec -it r2-ros2 bash
```   

### 4. Spawn robot in that new terminal
```
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2
```   

## Steering
### 1. Single command to configure speed and wheel turn
```
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.5}}"
```   
linear.x = forward speed in m/s (negative = reverse)   
angular.z = desired turn rate; positive = left, negative = right. The plugin converts this into a steering angle internally using the wheelbase we gave it.   

### 2. Continuous command
```
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}"
```   
Empty {} default all parameters to 0.   

### 3. Keyboard controller
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```   
The middle column is “straight” steering with the top key being forward and bottom being backward.

### 4. Testing the data output of joint radians (BROKEN FOR NOW)
```
ros2 topic echo /vehicle/steering_angle_rad
```   

### 5. Testing speed (BROKEN FOR NOW)
```
ros2 topic echo /vehicle/speed_mps
```   

### 6. Running the services/topics (REQUIRED TO TEST STEERING)
```
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
```


