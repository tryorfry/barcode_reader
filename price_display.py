import sys, time
import sqlite3
import RPi.GPIO as GPIO
from RPLCD import CharLCD
import pprint as pprint

import barcode_reader

pp = pprint.PrettyPrinter()

def sql_row_in_dict_factory(cursor, row):
    d = {}
    for index, col in enumerate(cursor.description):
        d[col[0]] = row[index]

    return d

def query_with_barcode(barcode):
    """" given the barcode find the record that matches barcode from STOCK_DETAIL table"""
    conn = sqlite3.connect('./shop_data.db')
    conn.row_factory = sql_row_in_dict_factory
    c = conn.cursor()
    r = c.execute('SELECT * FROM STOCK_DETAIL WHERE BARCODE = ?', (barcode,)).fetchone()
    conn.close()
    #pp.pprint(r)

    return r or {}

def run_barcode_scanner():
    if not barcode_reader.is_barcode_scanner_connected_in_usb_port():
        print("Fatal Error: Barcode scanner is not connected. Please connect the scanner first!")
        sys.exit()

    try:
        while True:
            barcode = barcode_reader.barcode_reader()
            display_data(barcode)
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    except Exception as err:
        print(err)

def display_in_lcd(data):
    #print(data['RETAIL_PRICE'])
    lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

    if 'RETAIL_PRICE' not in data or 'ITEM_NAME' not in data:
        display_string = "NOT FOUND\r\nSORRY"
    else:
        # first row of LCD display item name        
        display_string = data['ITEM_NAME'][0:14] + '\r\n'
        # 2nd row of LCD display price
        display_string += '$' + str(data['RETAIL_PRICE'])

    lcd.clear()
    lcd.home()
    time.sleep(1)

    print(display_string)
    lcd.write_string(display_string)
    

def display_data(barcode):
    matched_record = query_with_barcode(barcode)
    print(matched_record)
    display_in_lcd(matched_record)


if __name__ == '__main__':
    run_barcode_scanner()
