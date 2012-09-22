#!/usr/bin/python

import quick2wire.spi as Spibus
from bitstring import Bits
import time

class MAX31855(object):
    '''Python driver for [MAX38155 Cold-Junction Compensated Thermocouple-to-Digital Converter](http://www.maximintegrated.com/datasheet/index.mvp/id/7273)
   
     Requires:
     - [quick2wire.spi, quick2wire.asm_generic_ioctl.py, quick2wire.spi_ctypes](https://github.com/quick2wire/quick2wire-python-api)
     - [bitstring](http://code.google.com/p/python-bitstring/)
     - [Raspberry Pi](http://www.raspberrypi.org/)

    '''
    def __init__(self, pin, units = "c"):
        '''Initialize SPI bus
        
        Parameters:
        - pin:   CS pin used on Raspberry Pi (0 or 1) 
        - units: (optional) unit of measurement to return. ("c" (default) | "k" | "f")
        
        '''
        self.pin = pin
        self.units = units
        self.data = None
        self.spi = Spibus.SPIDevice(self.pin, 0)

    def get(self):
        '''Reads SPI bus and returns current value of thermocouple.'''
        self.read()
        return getattr(self, "to_" + self.units)(self.bin_to_tc_temperature())

    def get_rj(self):
        '''Reads SPI bus and returns current value of reference junction.'''
        self.read()
        return getattr(self, "to_" + self.units)(self.bin_to_rj_temperature())

    def read(self):
        '''Reads 32 bits of the SPI bus for processing and stores as 32-bit bitstring.'''
        raw_spi = self.spi.transaction(Spibus.reading(4))
        self.data = Bits(bytes=raw_spi[0], length=32)
        self.checkErrors()

    def checkErrors(self, data_32 = None):
        '''Checks bit 16 to see if there are any SCV, SCG, or OC faults'''
        if data_32 is None:
            data_32 = self.data
        anyErrors = data_32[15]
        noConnection = data_32[31]
        shortToGround = data_32[30]
        shortToVCC = data_32[29]
        if anyErrors:
            if noConnection:
                raise MAX31855Error("No Connection")
            elif shortToGround:
                raise MAX31855Error("Thermocouple short to ground")
            elif shortToVCC:
                raise MAX31855Error("Thermocouple short to VCC")
            else:
                raise MAX31855Error("???")
                
    def bin_to_tc_temperature(self, data_32 = None):
        '''Takes a 32-bit bitstring and returns a thermocouple temperature in celsius.'''
        if data_32 is None:
            data_32 = self.data
        tc_data = data_32[:14]
        return self.convert_tc_data(tc_data)

    def bin_to_rj_temperature(self, data_32 = None):
        '''Takes a 32-bit bitstring and returns a reference junction temperature in celsius.'''
        if data_32 is None:
            data_32 = self.data
        rj_data = data_32[16:28]
        return self.convert_rj_data(rj_data)

    def convert_tc_data(self, tc_data):
        '''Convert thermocouple bitstring to a useful number (celsius).'''
        return tc_data.int * 0.25

    def convert_rj_data(self, rj_data):
        '''Convert reference junction bitstring to a useful number (celsius).'''
        return rj_data.int * 0.0625

    def to_c(self, celsius):
        '''Celsius passthrough for generic to_* method.'''
        return celsius

    def to_k(self, celsius):
        '''Convert celsius to kelvin.'''
        return celsius + 273.15

    def to_f(self, celsius):
        '''Convert celsius to fahrenheit.'''
        return celsius * 9.0/5.0 + 32

    def test_conversions(self):
        '''Verify conversion to signed two's complement int and conversion factor from datasheet is working as expected.'''
        print "Test conversions from MAX31855 datasheet"
        print "External Thermocouple:"
        tc_tests = [['0110 0100 0000 00',1600.00],
                ['0011 1110 1000 00',1000.00],
                ['0000 0110 0100 11',100.75],
                ['0000 0001 1001 00', 25.00],
                ['0000 0000 0000 00',  0.00],
                ['1111 1111 1111 11', -0.25],
                ['1111 1111 1111 00', -1.00],
                ['1111 0000 0110 00',-250.00]]
        for test in tc_tests:
            value =  self.convert_tc_data(Bits(bin=test[0]))
            result = (value == test[1])
            print '"{}" should equal {}: {}'.format(test[0], test[1], result)
        print "Internal Reference Junction:"
        rj_tests = [['0111 1111 0000',127.0000],
                ['0110 0100 1001',100.5625],
                ['0001 1001 0000', 25.0000],
                ['0000 0000 0000', 0.0000],
                ['1111 1111 1111',-0.0625],
                ['1111 1111 0000',-1.0000],
                ['1110 1100 0000',-20.0000],
                ['1100 1001 0000',-55.0000]]
        for test in rj_tests:
            value =  self.convert_rj_data(Bits(bin=test[0]))
            result = (value == test[1])
            print '"{}" should equal {}: {} ({})'.format(test[0], test[1], result, value)

class MAX31855Error(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

if __name__ == "__main__":
    thermocouple = MAX31855(1, "f")
    thermocouple.test_conversions()
    while(True):
        try:
            print "tc: {} and rj: {}".format(thermocouple.get(), thermocouple.get_rj())
            time.sleep(.5)
        except KeyboardInterrupt:
            break