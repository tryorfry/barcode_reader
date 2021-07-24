#!/usr/bin/python

# Inspired by https://www.piddlerintheroot.com/barcode-scanner/
# https://www.raspberrypi.org/forums/viewtopic.php?f=45&t=55100
# from 'brechmos'

import logging
from glob import glob
import subprocess
import os, sys, re

CHARMAP_LOWERCASE = {4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k',
                     15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v',
                     26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7',
                     37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';',
                     52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'}
CHARMAP_UPPERCASE = {4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K',
                     15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V',
                     26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&',
                     37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':', 52: '"',
                     53: '~', 54: '<', 55: '>', 56: '?'}
CR_CHAR = 40
SHIFT_CHAR = 2

def list_usb():
    return [str(usb, 'utf-8') for usb in subprocess.check_output(['/usr/bin/lsusb']).splitlines()]

def is_barcode_scanner_connected_in_usb_port():
    for usb in list_usb():
        if re.search('barcode', usb, re.IGNORECASE):
            print(usb)
            return True
    return False

def hidraw_file_to_usb_map():
    """ lsusb will list all the usb ports. Barcode scanner connects as a HID(human interface device - like keyboards, mouse etc)
        barcode scannner when connected to usb port it makes it availabel as one of the /dev/hidraw file. 
        This function basically finds out which /dev/hidraw file the barcode scanner is attached.

        step 1. list the /dev/hidraw
        step 2. is to list /sys/class file to find out which /dev/hidraw file 
    """
    mapping = {}
    hidraw_filename = glob('/dev/hidraw*')
    for hidraw in hidraw_filename:
        sys_file = "/sys/class/hidraw/{0}/device/uevent".format(hidraw.split('/')[2])
        usb_name = subprocess.check_output("cat {0} | grep HID_NAME|cut -d '=' -f 2".format(sys_file), shell=True)
        mapping[hidraw] = str(usb_name, 'utf-8').strip()

    return mapping


def identify_hid_file_for_barcode_reader(match_pattern='honeywell|barcode|scanner'):
    """from mapping of the hidraw to HID_NAME - find the /dev/hidraw file.
    This is to identify the barcode port instead of hardcoding after checking manually"""
    mapping = hidraw_file_to_usb_map()

    for hid_file, hid_name in mapping.items():
        if re.search(match_pattern, hid_name, re.IGNORECASE):
            return hid_file
    
    raise Exception("No barcode scanner was attached to the system. Could not find the hid file. Search pattern used is {0}".format(match_pattern))

def barcode_reader():
    barcode_string_output = ''
    # barcode can have a 'shift' character; this switches the character set
    # from the lower to upper case variant for the next character only.
    # /sys/class/hidraw/hidraw4/device/uevent
    # hidraw1 - mouse
    # hidraw2 - keyboard
    # hidraw4 - barcode reader
    hid_file_for_barcode_scanner = identify_hid_file_for_barcode_reader()
    CHARMAP = CHARMAP_LOWERCASE
    with open(hid_file_for_barcode_scanner, 'rb') as fp:
        while True:
            # step through returned character codes, ignore zeroes
            for char_code in [element for element in fp.read(8) if element > 0]:
                if char_code == CR_CHAR:
                    # all barcodes end with a carriage return
                    return barcode_string_output

                if char_code == SHIFT_CHAR:
                    # use uppercase character set next time
                    CHARMAP = CHARMAP_UPPERCASE
                else:
                    # if the charcode isn't recognized, add nothing. should be numbers only
                    barcode_string_output += CHARMAP.get(char_code, '')
                    # reset to lowercase character map
                    CHARMAP = CHARMAP_LOWERCASE

if __name__ == '__main__':
    if not is_barcode_scanner_connected_in_usb_port():
        print("Fatal Error: Barcode scanner is not connected. Please connect the scanner first!")
        sys.exit()

    try:
        while True:
            upcnumber = barcode_reader()
            print('-----{0}'.format(upcnumber))
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt')
    except Exception as err:
        logging.error('funny error' + err)

    #print(list_usb())
    # print(hidraw_file_to_usb_map())
    #print(identify_hid_file_for_barcode_reader())
    # print(is_barcode_scanner_connected_in_usb_port())