import unittest
import logging
import os
import shutil
import datetime
import numpy as np

from eolearn.core import EOPatch, FeatureType

logging.basicConfig(level=logging.DEBUG)


class TestEOPatch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.mkdir('./test_outputs')

    def test_add_feature(self):
        bands = np.arange(2*3*3*2).reshape(2, 3, 3, 2)

        eop = EOPatch()
        eop.add_feature(FeatureType.DATA, 'bands', bands)

        self.assertTrue(np.array_equal(eop.data['bands'], bands), msg="Data numpy array not stored")

    def test_get_feature(self):
        bands = np.arange(2*3*3*2).reshape(2, 3, 3, 2)

        eop = EOPatch()
        eop.add_feature(FeatureType.DATA, 'bands', bands)

        eop_bands = eop.get_feature(FeatureType.DATA, 'bands')

        self.assertTrue(np.array_equal(eop_bands, bands), msg="Data numpy array not returned properly")

    def test_remove_feature(self):
        bands = np.arange(2*3*3*2).reshape(2, 3, 3, 2)
        names = ['bands1', 'bands2', 'bands3']

        eop = EOPatch()
        eop.add_feature(FeatureType.DATA, names[0], bands)
        eop.data[names[1]] = bands
        eop[FeatureType.DATA][names[2]] = bands

        for feature_name in names:
            self.assertTrue(feature_name in eop.data, "Feature {} was not added to EOPatch".format(feature_name))
            self.assertTrue(np.array_equal(eop.data[feature_name], bands), "Data of feature {} is "
                                                                           "incorrect".format(feature_name))

        eop.remove_feature(FeatureType.DATA, names[0])
        del eop.data[names[1]]
        del eop[FeatureType.DATA][names[2]]
        for feature_name in names:
            self.assertFalse(feature_name in eop.data, msg="Feature {} should be deleted from "
                                                           "EOPatch".format(feature_name))

    def test_check_dims(self):
        bands_2d = np.arange(3*3).reshape(3, 3)
        bands_3d = np.arange(3*3*3).reshape(3, 3, 3)

        with self.assertRaises(ValueError):
            EOPatch(data={'bands': bands_2d})

        eop = EOPatch()
        for feature_type in FeatureType:
            if feature_type.is_spatial() and not feature_type.is_vector():
                with self.assertRaises(ValueError):
                    eop[feature_type][feature_type.value] = bands_2d

    def test_concatenate(self):
        eop1 = EOPatch()
        bands1 = np.arange(2*3*3*2).reshape(2, 3, 3, 2)
        eop1.add_feature(FeatureType.DATA, 'bands', bands1)

        eop2 = EOPatch()
        bands2 = np.arange(3*3*3*2).reshape(3, 3, 3, 2)
        eop2.add_feature(FeatureType.DATA, 'bands', bands2)

        eop = eop1 + eop2

        self.assertTrue(np.array_equal(eop.data['bands'], np.concatenate((bands1, bands2), axis=0)),
                        msg="Array mismatch")

    def test_concatenate_different_key(self):
        eop1 = EOPatch()
        bands1 = np.arange(2*3*3*2).reshape(2, 3, 3, 2)
        eop1.add_feature(FeatureType.DATA, 'bands', bands1)

        eop2 = EOPatch()
        bands2 = np.arange(3*3*3*2).reshape(3, 3, 3, 2)
        eop2.add_feature(FeatureType.DATA, 'measurements', bands2)

        eop = eop1 + eop2
        self.assertTrue('bands' in eop.data and 'measurements' in eop.data, "Failed to concatenate different features")

    def test_concatenate_timeless(self):
        eop1 = EOPatch()
        mask1 = np.arange(3*3*2).reshape(3, 3, 2)
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'mask1', mask1)
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'mask', 5 * mask1)

        eop2 = EOPatch()
        mask2 = np.arange(3*3*2).reshape(3, 3, 2)
        eop2.add_feature(FeatureType.DATA_TIMELESS, 'mask2', mask2)
        eop2.add_feature(FeatureType.DATA_TIMELESS, 'mask', 5 * mask1)  # add mask1 to eop2

        eop = EOPatch.concatenate(eop1, eop2)

        for name in ['mask', 'mask1', 'mask2']:
            self.assertTrue(name in eop.data_timeless)
        self.assertTrue(np.array_equal(eop.data_timeless['mask'], 5 * mask1), "Data with same values should stay "
                                                                              "the same")

    def test_concatenate_missmatched_timeless(self):
        mask = np.arange(3*3*2).reshape(3, 3, 2)

        eop1 = EOPatch()
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'mask', mask)
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'nask', 3 * mask)

        eop2 = EOPatch()
        eop2.add_feature(FeatureType.DATA_TIMELESS, 'mask', mask)
        eop2.add_feature(FeatureType.DATA_TIMELESS, 'nask', 5 * mask)

        with self.assertRaises(ValueError):
            eop = eop1 + eop2

    def test_equals(self):
        eop1 = EOPatch(data={'bands': np.arange(2*3*3*2).reshape(2, 3, 3, 2)})
        eop2 = EOPatch(data={'bands': np.arange(2*3*3*2).reshape(2, 3, 3, 2)})

        self.assertTrue(eop1 == eop2)

        eop1.add_feature(FeatureType.DATA_TIMELESS, 'dem', np.arange(3*3*2).reshape(3, 3, 2))

        self.assertFalse(eop1 == eop2)

    def test_save_load(self):
        eop1 = EOPatch()
        mask1 = np.arange(3*3*2).reshape(3, 3, 2)
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'mask1', mask1)
        eop1.add_feature(FeatureType.DATA_TIMELESS, 'mask', 5 * mask1)

        eop1.save('./test_outputs/eop1/')

        eop2 = EOPatch.load('./test_outputs/eop1')

        self.assertEqual(eop1, eop2)

    def test_timestamp_consolidation(self):
        # 10 frames
        timestamps = [datetime.datetime(2017, 1, 1, 10, 4, 7),
                      datetime.datetime(2017, 1, 4, 10, 14, 5),
                      datetime.datetime(2017, 1, 11, 10, 3, 51),
                      datetime.datetime(2017, 1, 14, 10, 13, 46),
                      datetime.datetime(2017, 1, 24, 10, 14, 7),
                      datetime.datetime(2017, 2, 10, 10, 1, 32),
                      datetime.datetime(2017, 2, 20, 10, 6, 35),
                      datetime.datetime(2017, 3, 2, 10, 0, 20),
                      datetime.datetime(2017, 3, 12, 10, 7, 6),
                      datetime.datetime(2017, 3, 15, 10, 12, 14)]

        data = np.random.rand(10, 100, 100, 3)
        mask = np.random.randint(0, 2, (10, 100, 100, 1))
        mask_timeless = np.random.randint(10, 20, (100, 100, 1))
        scalar = np.random.rand(10, 1)

        eop = EOPatch(timestamp=timestamps,
                      data={'DATA': data},
                      mask={'MASK': mask},
                      scalar={'SCALAR': scalar},
                      mask_timeless={'MASK_TIMELESS': mask_timeless})

        good_timestamps = timestamps.copy()
        del good_timestamps[0]
        del good_timestamps[-1]
        good_timestamps.append(datetime.datetime(2017, 12, 1))

        removed_frames = eop.consolidate_timestamps(good_timestamps)

        self.assertEqual(good_timestamps[:-1], eop.timestamp)
        self.assertEqual(len(removed_frames), 2)
        self.assertTrue(timestamps[0] in removed_frames)
        self.assertTrue(timestamps[-1] in removed_frames)
        self.assertTrue(np.array_equal(data[1:-1, ...], eop.data['DATA']))
        self.assertTrue(np.array_equal(mask[1:-1, ...], eop.mask['MASK']))
        self.assertTrue(np.array_equal(scalar[1:-1, ...], eop.scalar['SCALAR']))
        self.assertTrue(np.array_equal(mask_timeless, eop.mask_timeless['MASK_TIMELESS']))

    @classmethod
    def tearDown(cls):
        shutil.rmtree('./test_outputs/', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
