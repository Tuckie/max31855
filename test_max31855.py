#!/usr/bin/python
from max31855 import MAX31855, MAX31855Error
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.thermocouple = MAX31855(1, 2, 3, 4)
        
    def test_convert_tc_data(self):
        '''Verify thermocouple conversion to signed two's complement int and conversion factor from datasheet is working as expected.'''
        tc_tests = [['0110 0100 0000 00',1600.00],
                ['0011 1110 1000 00',1000.00],
                ['0000 0110 0100 11',100.75],
                ['0000 0001 1001 00', 25.00],
                ['0000 0000 0000 00',  0.00],
                ['1111 1111 1111 11', -0.25],
                ['1111 1111 1111 00', -1.00],
                ['1111 0000 0110 00',-250.00]]
        for test in tc_tests:
            value =  self.thermocouple.convert_tc_data(int(test[0].replace(" ", ""), 2))
            self.assertEqual(value,  test[1])

    def test_convert_rj_data(self):
        '''Verify reference junction conversion to signed two's complement int and conversion factor from datasheet is working as expected.'''
        rj_tests = [['0111 1111 0000',127.0000],
                ['0110 0100 1001',100.5625],
                ['0001 1001 0000', 25.0000],
                ['0000 0000 0000', 0.0000],
                ['1111 1111 1111',-0.0625],
                ['1111 1111 0000',-1.0000],
                ['1110 1100 0000',-20.0000],
                ['1100 1001 0000',-55.0000]]
        for test in rj_tests:
            value =  self.thermocouple.convert_rj_data(int(test[0].replace(" ", ""), 2))
            self.assertEqual(value, test[1])

    def tearDown(self):
        self.thermocouple.cleanup()

if __name__ == '__main__':
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    #unittest.TextTestRunner(verbosity=2).run(suite)