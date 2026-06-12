#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qr_reader.py — QR Kod Okuyucu Node (Simülasyon Modu)
Gerçek kamera olmadığında QR doğrulamayı simüle eder.
"""

import rospy
from std_msgs.msg import String
from std_srvs.srv import Trigger, TriggerResponse


class QRReaderNode:
    def __init__(self):
        rospy.init_node('qr_reader', anonymous=False)

        self.expected_qr = rospy.get_param('~expected_qr', '')

        self.result_pub = rospy.Publisher(
            '/qr_reader/result', String, queue_size=10)

        self.trigger_srv = rospy.Service(
            '/qr_reader/trigger', Trigger, self._trigger_callback)

        rospy.loginfo("[QR Reader] Simülasyon modu — hazır.")

    def _trigger_callback(self, req):
        expected = rospy.get_param('/qr_reader/expected_qr', '')
        rospy.loginfo("[QR Reader] QR okunuyor... Beklenen: %s", expected)
        rospy.sleep(1.0)

        if expected:
            rospy.loginfo("[QR Reader] QR simüle edildi: %s", expected)
            self.result_pub.publish(String(data=expected))
            return TriggerResponse(success=True, message=expected)
        else:
            return TriggerResponse(success=False, message="QR okunamadı")

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = QRReaderNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
