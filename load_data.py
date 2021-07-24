import sqlite3
import xlrd
import pprint as pprint
pp = pprint.PrettyPrinter()

from stock_report_download import stock_report_download

def create_table():
    conn = sqlite3.connect('./shop_data.db')
    cursor = conn.cursor()
    #cursor.execute('drop table STOCK_DETAIL')

    sql = '''CREATE TABLE IF NOT EXISTS STOCK_DETAIL(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    DEPARTMENT CHAR(200) NOT NULL,
    CATEGORY CHAR(200) NOT NULL,   
    ITEM_NUMBER INTEGER,
    ITEM_NAME CHAR(300),    
    BARCODE INTEGER,
    QUANTITY INTEGER,
    RETAIL_PRICE FLOAT,
    TOTAL_RETAIL_PRICE FLOAT,
    COST FLOAT,
    TOTAL_COST FLOAT,
    SUPPLIER CHAR(200)
    )'''
    cursor.execute(sql)

    conn.commit()

    conn.close()

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
    pp.pprint(r)

    return r

def data_from_excel_file():
    """reads data from excel file and send the rows map data in dictionary"""
    excel_file = '/home/pi/Downloads/StockOnHandReportItemSummary.xls'
    wb = xlrd.open_workbook(excel_file)
    print(wb.sheet_names())
    sheet1 = wb.sheet_by_name(wb.sheet_names()[0])
    print(sheet1.row(0))

    header_row = sheet1.row(1) # first 0 th row is not much useful
    print(header_row)
    # [text:'dept', text:'category', text:'item no', text:'item name', text:'barcode', text:'quantity', text:'retail price', text:'total retail', text:'cost', text:'total cost', empty:'']

    headers = ['dept', 'category', 'item_no', 'item_name', 'barcode', 'quantity', 'retai_price', 'total_retail', 'cost', 'total_cost', 'supplier']
    data = []
    for row_index in range(2, sheet1.nrows):
        row = sheet1.row(row_index)
        row_values = [cell.value for cell in row]
        header_row_map = dict(zip(headers, row_values))
        data.append(header_row_map)

    return data

def load_data_in_table(data):
    """given the stock detail data in dictionary load in STOCK_DETAIL"""
    conn = sqlite3.connect('./shop_data.db')
    cursor = conn.cursor()

    values = []
    for row in data:
        values.append(tuple(row[key] for key in ['dept', 'category', 'item_no', 'item_name', 'barcode', 'quantity', 'retai_price', 'total_retail', 'cost', 'total_cost', 'supplier']))

    cursor.executemany("""INSERT INTO STOCK_DETAIL ('DEPARTMENT', 'CATEGORY', 'ITEM_NUMBER', 'ITEM_NAME', 'BARCODE', 'QUANTITY', 'RETAIL_PRICE', 'TOTAL_RETAIL_PRICE', 'COST', 'TOTAL_COST', 'SUPPLIER')
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values
    )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    stock_report_download()
    create_table()
    data = data_from_excel_file()
    load_data_in_table(data)
#    result = query_with_barcode(8906001238294)
#    pp.pprint(result)
