
import unittest
import os.path
import numpy as np

from eolearn.core import EOPatch
from eolearn.features import AddHaralickTask


class TestHaralick(unittest.TestCase):

    TEST_PATCH_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'TestInputs', 'TestPatch')

    @classmethod
    def setUpClass(cls):
        cls.patch = EOPatch.load(cls.TEST_PATCH_FILENAME)
        cls._prepare_patch(cls.patch)

        AddHaralickTask('ndvi', 'haralick', texture_feature='contrast', distance=1, angle=0, levels=255,
                        window_size=3, stride=1).execute(cls.patch)

        cls.initial_patch = EOPatch.load(cls.TEST_PATCH_FILENAME)
        cls._prepare_patch(cls.initial_patch)

    @staticmethod
    def _prepare_patch(patch):
        ndvi = patch.data['ndvi'][:10]
        ndvi[np.isnan(ndvi)] = 0
        patch.data['ndvi'] = ndvi

    def test_new_feature(self):
        haralick = self.patch.data['haralick']
        delta = 1e-4

        test_min = np.min(haralick)
        exp_min = 0.0
        self.assertAlmostEqual(test_min, exp_min, delta=delta, msg="Expected min {}, got {}".format(exp_min, test_min))

        test_max = np.max(haralick)
        exp_max = 15620.83333
        self.assertAlmostEqual(test_max, exp_max, delta=delta, msg="Expected max {}, got {}".format(exp_max, test_max))

        test_mean = np.mean(haralick)
        exp_mean = 1585.0905
        self.assertAlmostEqual(test_mean, exp_mean, delta=delta,
                               msg="Expected mean {}, got {}".format(exp_mean, test_mean))

        test_median = np.median(haralick)
        exp_median = 1004.916666
        self.assertAlmostEqual(test_median, exp_median, delta=delta,
                               msg="Expected median {}, got {}".format(exp_median, test_median))

    def test_unchanged_features(self):
        for feature, value in self.initial_patch.data.items():
            self.assertTrue(np.array_equal(value, self.patch.data[feature]),
                            msg="EOPatch data feature '{}' was changed in the process".format(feature))


if __name__ == '__main__':
    unittest.main()
