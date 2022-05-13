import sys  # Get the path to the "model" directory
import unittest

sys.path.append("C:\\Users\\monty.minh\\Documents\\Optimizer")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
