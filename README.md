# Quick Setup

Go through the below steps and skip rerunning 

#### 1. Clone repository
```
git clone git@github.com:H0RAC3Z/URDF-rosmaster-R2-gazebo-capstone.git
```   
```
cd URDF-rosmaster-R2-gazebo-capstone/
```   

#### 2. Build image
```
docker build -t r2-ros2-humble -f docker/Dockerfile .
```   

#### 3. Give docker perms to the X display server
```
xhost +local:docker
```   

#### 4. Run container
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

#### 5. Entry into bash on container
```
docker exec -it r2-ros2 bash
```   

#### 6. Set up environment
```
source /opt/ros/humble/setup.bash

colcon build --symlink-install

source install/setup.bash

export IGN_GAZEBO_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$IGN_GAZEBO_RESOURCE_PATH
export GZ_SIM_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:$GZ_SIM_RESOURCE_PATH
```   

#### 7. Open gazebo on Docker
```
ign gazebo -r empty.sdf
```   

#### 8. Open another terminal and enter the docker container
```
docker exec -it r2-ros2 bash
```   

#### 9. Spawn the robot in that terminal that you opened
```
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2
```   



# Steering
#### 1. Running the services/topics (REQUIRED TO TEST STEERING)
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

#### 2. Single command to configure speed and wheel turn
```
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.5}}"
```   
linear.x = forward speed in m/s (negative = reverse)   
angular.z = desired turn rate; positive = left, negative = right. The plugin converts this into a steering angle internally using the wheelbase we gave it.   

#### 2. Continuous command
```
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}"
```   
Empty {} default all parameters to 0.   

#### 2. Keyboard controller
```
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```   
The middle column is “straight” steering with the top key being forward and bottom being backward.

#### 3. Testing the data output of joint radians
```
ros2 topic echo /vehicle/steering_angle_rad
```   

#### 4. Testing speed
```
ros2 topic echo /vehicle/speed_mps
```   

exit can be used to exit the docker container terminal.


# Sending vehicle state to KUKSA

`vehicle_state_publisher.py` publishes speed and steering as ROS 2 `Float64`
messages. `write_to_kuksa.py` subscribes to those topics and writes the current
values to KUKSA Databroker as `Vehicle.Speed` (km/h) and
`Vehicle.SteeringAngle` (rad). The writer converts the ROS speed from m/s to
km/h to match the standard VSS `Vehicle.Speed` unit. `Vehicle.SteeringAngle`
is the custom signal declared in `OBD.json`; load that file as part of the
Databroker VSS configuration before starting the bridge.

The Docker image installs `kuksa-client` in a virtual environment with access
to the system ROS 2 Python packages. 

Start KUKSA Databroker on the default gRPC endpoint `127.0.0.1:55555`

#### Make sure you are in the github repo root directory and run the below to start kuksa databroker
```
docker run --rm -it -p 55555:55555 -v "$(pwd)/OBD.json:/OBD.json" ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure --vss /OBD.json
```   

Then, in terminals where the ROS 2 environment is sourced, run the existing
Gazebo `/joint_states` bridge and these two nodes:

```
python3 vehicle_state_publisher.py
python3 write_to_kuksa.py
```

The publisher and writer must share a ROS 2 domain. If the databroker runs in
a different container or host, set `KUKSA_HOST` to an address reachable from
the writer's environment.

### Testing if Kuksa Databroker has received the data

#### 1. Open Kuksa client
```
kuksa-client grpc://127.0.0.1:55555
```   
#### 2. Get vehicle speed
```
getValue Vehicle.Speed
```   
#### 3. Get vehicle steering angle
```
getValue Vehicle.SteeringAngle
```

Steering angle should match up directly, but vehicle speed is converted from m/s to km/h (conversion rate = m/s multiplied by 3.6).

# If Issues with Rerunning

#### 1. Start the docker container assuming it has shut down since the last time used
```
docker start -ai r2-ros2
```   
Then Ctrl+C

#### 2. Give docker proper permissions
```
xhost +local:docker
```   

#### 3. Open another terminal inside the image
```
docker exec -it r2-ros2 bash
```   

#### 4. Launch Gazebo
```
ign gazebo -r empty.sdf
```   

#### 5. Open another terminal and open another bash in the container
```
docker exec -it r2-ros2 bash
```   

#### 6. Spawn robot in that new terminal
```
ros2 run ros_gz_sim create \
  -world empty \
  -file /root/r2_ros2/src/yahboomcar_description/urdf/yahboomcar_R2_gazebo.urdf \
  -name yahboom_r2_gazebo \
  -z 0.2
```   