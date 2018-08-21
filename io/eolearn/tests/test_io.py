import unittest
import logging

import numpy

from sentinelhub import BBox, CRS
from sentinelhub import DataSource, ServiceType

from eolearn.io import *
from eolearn.io.utilities import parse_time_interval
from eolearn.core import EOPatch

logging.basicConfig(level=logging.DEBUG)


class TestEOPatch(unittest.TestCase):

    class TaskTestCase:
        """
        Container for each task case of eolearn-io functionalities
        """

        def __init__(self, name, request, bbox, time_interval,
                     eop=None, layer=None, data_size=None):
            self.name = name
            self.request = request
            self.layer = layer
            self.data_size = data_size

            if eop is None:
                self.eop = request.execute(bbox=bbox, time_interval=time_interval)
            elif isinstance(eop, EOPatch):
                self.eop = request.execute(eop, bbox=bbox, time_interval=time_interval)
            else:
                raise TypeError('Task {}: Argument \'eop\' should be an EOPatch, not {}'.format(
                    name, eop.__class__.__name__))


    @classmethod
    def setUpClass(cls):

        bbox = BBox(bbox=(-5.05, 48.0, -5.00, 48.05), crs=CRS.WGS84)
        time_interval = ('2017-1-1', '2018-1-1')
        img_width = 100
        img_height = 100
        resx = '53m'
        resy = '78m'

        # existing eopatch
        cls.eeop = SentinelHubWMSInput(
            layer='BANDS-S2-L1C',
            height=img_height,
            width=img_width,
            data_source=DataSource.SENTINEL2_L1C).execute(bbox=bbox, time_interval=time_interval)

        cls.create_patches = [

            cls.TaskTestCase(
                name='generalWmsTask',
                layer='BANDS-S2-L1C',
                data_size=13,
                request=SentinelHubWMSInput(
                    layer='BANDS-S2-L1C',
                    height=img_height,
                    width=img_width,
                    data_source=DataSource.SENTINEL2_L1C),
                bbox=bbox,
                time_interval=time_interval,
                eop=None
            ),

            cls.TaskTestCase(
                name='generalWcsTask',
                layer='BANDS-S2-L1C',
                data_size=13,
                request=SentinelHubWCSInput(
                    layer='BANDS-S2-L1C',
                    resx=resx,
                    resy=resy,
                    data_source=DataSource.SENTINEL2_L1C),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='S2 L1C WMS',
                layer='BANDS-S2-L1C',
                data_size=13,
                request=S2L1CWMSInput(
                    layer='BANDS-S2-L1C',
                    height=img_height,
                    width=img_width),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='S2 L1C WCS',
                layer='BANDS-S2-L1C',
                data_size=13,
                request=S2L1CWCSInput(
                    layer='BANDS-S2-L1C',
                    resx=resx,
                    resy=resy),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='L8 L1C WMS',
                layer='TRUE-COLOR-L8',
                data_size=3,
                request=L8L1CWMSInput(
                    layer='TRUE-COLOR-L8',
                    height=img_height,
                    width=img_width),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='L8 L1C WMS',
                layer='TRUE-COLOR-L8',
                data_size=3,
                request=L8L1CWMSInput(
                    layer='TRUE-COLOR-L8',
                    height=img_height,
                    width=img_width),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='S2 L2A WMS',
                layer='BANDS-S2-L2A',
                data_size=12,
                request=S2L2AWMSInput(
                    layer='BANDS-S2-L2A',
                    height=img_height,
                    width=img_width),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='S2 L2A WCS',
                layer='BANDS-S2-L2A',
                data_size=12,
                request=S2L2AWCSInput(
                    layer='BANDS-S2-L2A',
                    resx=resx,
                    resy=resy),
                bbox=bbox,
                time_interval=time_interval,
                eop=EOPatch()
            ),

            cls.TaskTestCase(
                name='DEM_wms',
                layer='DEM',
                data_size=1,
                request=DEMWMSInput(
                    layer='DEM',
                    height=img_height,
                    width=img_width),
                bbox=bbox,
                time_interval=time_interval,
                eop=None,
            ),

            cls.TaskTestCase(
                name='DEM_wcs',
                layer='DEM',
                data_size=1,
                request=DEMWCSInput(
                    layer='DEM',
                    resx=resx,
                    resy=resy),
                bbox=bbox,
                time_interval=time_interval,
                eop=None,
            ),
        ]

        cls.update_patches = [
            cls.TaskTestCase(
                name='generalWmsTask_to_empty',
                layer='BANDS-S2-L1C',
                data_size=13,
                eop=EOPatch(),
                request=SentinelHubWMSInput(
                    layer='BANDS-S2-L1C',
                    height=img_height,
                    width=img_width,
                    data_source=DataSource.SENTINEL2_L1C),
                bbox=bbox,
                time_interval=time_interval,
            ),

            cls.TaskTestCase(
                name='DEM_to_existing_patch',
                layer='DEM',
                data_size=1,
                eop=cls.eeop.__deepcopy__(),
                request=DEMWCSInput(
                    layer='DEM',
                    resx=resx,
                    resy=resy),
                bbox=bbox,
                time_interval=time_interval,
            ),
        ]

        cls.task_cases = cls.create_patches + cls.update_patches

    def test_return_type(self):
        for task in self.task_cases:
            with self.subTest(msg='Test case {}'.format(task.name)):
                self.assertTrue(isinstance(task.eop, EOPatch),
                                "Expected return type of task is EOPatch!")

    def test_time_interval(self):
        for task in self.task_cases:
            with self.subTest(msg='Test case {}'.format(task.name)):
                self.assertEqual(task.eop.meta_info['time_interval'],
                                 parse_time_interval(('2017-1-1', '2018-1-1')))

    def test_auto_feature_presence(self):
        for task in self.task_cases:
            with self.subTest(msg='Test case {}'.format(task.name)):
                self.assertTrue(task.layer in task.eop.data or task.eop.data_timeless)
                self.assertTrue('IS_DATA' in task.eop.mask)

    def test_feature_dimension(self):
        for task in self.task_cases:
            with self.subTest(msg='Test case {}'.format(task.name)):

                masks = [task.layer]
                for mask in masks:
                    if task.eop.data and mask in task.eop.data:
                        self.assertTrue(isinstance(task.eop.data[mask], numpy.ndarray))
                        self.assertEqual(task.eop.data[mask].shape[-1], task.data_size)

                masks = ['DEM']
                for mask in masks:
                    if task.eop.data_timeless and mask in task.eop.data_timeless:
                        self.assertTrue(isinstance(task.eop.data_timeless[mask], numpy.ndarray))
                        self.assertEqual(task.eop.data_timeless[mask].shape[-1], task.data_size)

                masks = ['IS_DATA']
                for mask in masks:
                    if task.eop.mask and mask in task.eop.mask:
                        self.assertTrue(isinstance(task.eop.mask[mask], numpy.ndarray))
                        self.assertEqual(task.eop.mask[mask].shape[-1], 1)


if __name__ == '__main__':
    unittest.main()
