from bika.lims.testing import BIKA_ROBOT_TESTING
from plone.testing import layered

import robotsuite
import unittest


ROBOT_TESTS = [
    'test_bika_setup.robot',
    'test_Client.robot'
    'test_Batch.robot',
    'test_AnalysisRequest.robot',
    'test_bika_Worksheets.robot',
    'test_ShowPartitions.robot',
]


def test_suite():
    suite = unittest.TestSuite()
    for RT in ROBOT_TESTS:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(RT), layer=BIKA_ROBOT_TESTING),
        ])
    return suite