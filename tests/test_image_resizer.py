from unibox.processing.image_resizer_next import get_new_dimensions

import unittest


class TestGetNewDimensions(unittest.TestCase):

    def test_landscape_orientation(self):
        self.assertEqual(get_new_dimensions(1920, 1080, 720), (1280, 720))

    def test_portrait_orientation(self):
        self.assertEqual(get_new_dimensions(1080, 1920, 720), (720, 1280))

    def test_square_orientation(self):
        self.assertEqual(get_new_dimensions(1000, 1000, 500), (500, 500))

    def test_aspect_ratio_gt_one(self):
        self.assertEqual(get_new_dimensions(1000, 500, 250), (500, 250))

    def test_aspect_ratio_lt_one(self):
        self.assertEqual(get_new_dimensions(500, 1000, 250), (250, 500))

    def test_float_point(self):
        # 835 / 600 * 400 = 556.66
        self.assertEqual(get_new_dimensions(835, 600, 400), (557, 400))

    def test_neg_number1(self):
        with self.assertRaises(ValueError):
            get_new_dimensions(835, 600, -400)

    def test_neg_number2(self):
        with self.assertRaises(ValueError):
            get_new_dimensions(835, -600, 400)

    def test_neg_number3(self):
        # min_side = -1时返回原图尺寸
        self.assertEqual(get_new_dimensions(835, 600, -1), (835, 600))

    def test_long_side(self):
        self.assertEqual(get_new_dimensions(2000, 400, 1000, resize_by_longer_side=True), (1000, 200))

    def test_long_side2(self):
        # min_side = -1时返回原图尺寸
        self.assertEqual(get_new_dimensions(2000, 400, -1, resize_by_longer_side=True), (2000, 400))

    def test_long_side3(self):
        # 512 * 0.9 = 460.8
        self.assertEqual(get_new_dimensions(1000, 512, 900, resize_by_longer_side=True), (900, 461))


if __name__ == '__main__':
    unittest.main()
