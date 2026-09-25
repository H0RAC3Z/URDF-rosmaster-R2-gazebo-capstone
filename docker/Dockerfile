FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ros-humble-desktop \
    ros-humble-joint-state-publisher-gui \
    ros-humble-ros-gz \
    ros-humble-gz-ros2-control \
    ros-humble-teleop-twist-keyboard \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/r2_ros2

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "export GZ_SIM_RESOURCE_PATH=/root/r2_ros2/install/yahboomcar_description/share:\$GZ_SIM_RESOURCE_PATH" >> /root/.bashrc && \
    echo "if [ -f /root/r2_ros2/install/setup.bash ]; then source /root/r2_ros2/install/setup.bash; fi" >> /root/.bashrc

CMD ["tail", "-f", "/dev/null"]
