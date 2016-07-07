#!/usr/bin/env python
import roslib
import rospy
import tf
import tf2_ros
import geometry_msgs.msg
import serial
import time
import math
import string
import glob
import sensor_table
import find_dng
import threespace_api as tsa
from threespace_api import *
from socket import *
from threespace_ros.msg import dataVec

rospy.init_node("publisher")
r = rospy.Rate(100)
suffix = "_data_vec"
dongle_list = find_dng.returnDev("dng")
publishers = {}
dv_publishers = {}
broadcasters = {}
for d in dongle_list:
    tsa.TSDongle.broadcastSynchronizationPulse(d)
    for device in d:
        if device is None:
            rospy.logerr("No Sensor Found")
        else:
            # quat = tsa.TSWLSensor.getTaredOrientationAsQuaternion(device)
            id_ = str(device)
            id_ = id_[id_.find('W'):-1]
            rospy.logerr(id_)
            # rospy.logerr(quat)
            frame = sensor_table.sensor_table.get(id_)
            rospy.logerr("Adding publisher for %s : %s", id_, frame)
            rospy.logerr("Battery at %s Percent ", tsa.TSWLSensor.getBatteryPercentRemaining(device))
            br = tf2_ros.TransformBroadcaster()
            # pub = rospy.Publisher(frame, geometry_msgs.msg.QuaternionStamped, queue_size = 100)
            dv_pub = rospy.Publisher(frame+suffix, dataVec, queue_size=100)
            broadcasters[frame] = br
            # publishers[frame] = pub
            dv_publishers[frame] = dv_pub
            tsa.TSWLSensor.setStreamingSlots(device, slot0='getTaredOrientationAsQuaternion',
                                             slot1='getAllCorrectedComponentSensorData')

t = geometry_msgs.msg.TransformStamped()
g = geometry_msgs.msg.QuaternionStamped()
dv = dataVec()
dev_list = []
for d in dongle_list:
    for dev in d:
        # batch = tsa.TSWLSensor.getStreamingBatch(device)
        if dev is not None:
            dev_list.append(dev)

while not rospy.is_shutdown():
    # r.sleep()
    # for d in dongle_list:
    for device in dev_list:
        if device is not None:
            # while True:
            #    quat = tsa.TSWLSensor.getTaredOrientationAsQuaternion(device)
            #    print quat
            # quat = tsa.TSWLSensor.getTaredOrientationAsQuaternion(device)
            # print quat
            # gyro = tsa.TSWLSensor.getCorrectedGyroRate(device)
            # print gyro
            # compass = tsa.TSWLSensor.getCorrectedCompassVector(device)
            # print compass
            # accel = tsa.TSWLSensor.getCorrectedAccelerometerVector(device)
            # print accel
            # globalAccel = tsa.TSWLSensor.getCorrectedLinearAccelerationInGlobalSpace(device)
            # print globalAccel
            # full = tsa.TSWLSensor.getAllCorrectedComponentSensorData(device)
            # print full
            # r.sleep()
            batch = tsa.TSWLSensor.getStreamingBatch(device)
            # if batch is not None:
            # quat = batch[0:4]
            # full = batch[4:]
            # if (quat is not None)and(full is not None):
            if batch is not None:
                # if (batch is not None):
                quat = batch[0:4]
                full = batch[4:]
                id_ = str(device)
                id_ = id_[id_.find('W'):-1]
                frame = sensor_table.sensor_table.get(id_)
                # rospy.logwarn("%s : %s ---> %s",id,frame,quat)
                # p = publishers.get(frame)
                d = dv_publishers.get(frame)
                # b = broadcasters.get(frame)
                # t.header.stamp = rospy.Time.now()
                # t.header.frame_id = "world"
                # t.child_frame_id = frame
                # t.transform.translation.x = 0.0
                # t.transform.translation.y = 0.0
                # t.transform.translation.z = 0.0
                # g.quaternion.x = quat[0]
                # g.quaternion.y = quat[1]
                # g.quaternion.z = quat[2]
                # dv.header.stamp = rospy.Time.now()
                dv.header.stamp = rospy.get_rostime()
                # g.quaternion.w = quat[3]
                dv.quat.quaternion.x = quat[0]
                dv.quat.quaternion.y = quat[1]
                dv.quat.quaternion.z = quat[2]
                dv.quat.quaternion.w = quat[3]
                dv.gyroX = full[0]
                dv.gyroY = full[1]
                dv.gyroZ = full[2]
                dv.accX = full[3]
                dv.accY = full[4]
                dv.accZ = full[5]
                dv.comX = full[6]
                dv.comY = full[7]
                dv.comZ = full[8]
                # t.transform.rotation = g.quaternion
                # b.sendTransform(t)
                # p.publish(g)
                d.publish(dv)

for d in dongle_list:
    tsa.TSDongle.close(d)
print publishers
print dv_publishers
print broadcasters
exit()

