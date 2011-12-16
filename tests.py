import unittest

class APITest(unittest.TestCase):

    def setUp(self):
        self._clean_test_data()
        self._init_test_data()

    def test_should_save_and_get_daylog(self):
        print('hello world, we can enjoy tests')
    
    def _clean_test_data(self):
        pass

    def _init_test_data(self):
        pass

if __name__ == '__main__':
    unittest.main()
