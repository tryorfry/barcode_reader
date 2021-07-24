import os
import time
import shutil
import conf

from selenium import webdriver
import sqlite3
import xlrd
import pprint

class StockReport(object):
    def __init__(self):
        self.driver = webdriver.Chrome(conf.selenium_chrome_driver)
    
    def login(self):
        self.driver.get(conf.login_url)
        time.sleep(4)
        username = self.driver.find_element_by_id("UserName")
        password = self.driver.find_element_by_id("Password")

        username.send_keys(conf.user_name)
        time.sleep(1)

        password.send_keys(conf.password)
        time.sleep(1)
        
        self.driver.find_element_by_id("submitBtn").click()
        time.sleep(3)

    def download_report(self):
        self.driver.get(conf.stock_with_price_url)
        time.sleep(2)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_LinkButton2").click()
        
        time.sleep(1)
        downloaded_filename = max([conf.download_directory + "/" + f for f in os.listdir(conf.download_directory)], key=os.path.getctime)
        shutil.move(downloaded_filename, os.path.join(conf.download_directory, conf.downloaded_latest_file_name))
    
    def logout(self):
        self.driver.find_element_by_id("ctl00_logoutBtn").click()
        time.sleep(3)

    def __quit_browser(self):
        self.driver.quit()

    def __del__(self):
        self.__quit_browser()


class LoadReportInSQLite(object):
    def __init__(self, db_file=conf.db_file, latest_report_file=conf.download_directory + '/' + conf.downloaded_latest_file_name):
        self.latest_report_file = latest_report_file
        self.dbc = sqlite3.connect(db_file)

    def create_table(self):
        cursor = self.dbc.cursor()
        #cursor.execute('drop table STOCK_DETAIL')

        sql = '''CREATE TABLE IF NOT EXISTS STOCK_DETAIL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        DEPARTMENT CHAR(200) NOT NULL,
        CATEGORY CHAR(200) NOT NULL,   
        ITEM_NUMBER INTEGER,
        ITEM_NAME CHAR(300),    
        BARCODE INTEGER,n
        QUANTITY INTEGER,
        RETAIL_PRICE FLOAT,
        TOTAL_RETAIL_PRICE FLOAT,
        COST FLOAT,
        TOTAL_COST FLOAT,
        SUPPLIER CHAR(200)
        
        )'''
        cursor.execute(sql)

        self.dbc.commit()
    
    def data_from_excel_file(self):
        """reads data from excel file and send the rows map data in dictionary"""
        excel_file = self.latest_report_file
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

    def load_data_in_table(self, data):
        """given the stock detail data in dictionary load in STOCK_DETAIL"""
        cursor = self.dbc.cursor()

        values = []
        for row in data:
            values.append(tuple(row[key] for key in ['dept', 'category', 'item_no', 'item_name', 'barcode', 'quantity', 'retai_price', 'total_retail', 'cost', 'total_cost', 'supplier']))

        cursor.executemany("""INSERT INTO STOCK_DETAIL ('DEPARTMENT', 'CATEGORY', 'ITEM_NUMBER', 'ITEM_NAME', 'BARCODE', 'QUANTITY', 'RETAIL_PRICE', 'TOTAL_RETAIL_PRICE', 'COST', 'TOTAL_COST', 'SUPPLIER')
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values
        )

        self.dbc.commit()

    def __del__(self):
        self.dbc.close()


class QueryStock(object):
    def __init__(self, db_file=conf.db_file):
        self.dbc = sqlite3.connect(db_file)

    def __sql_row_in_dict_factory(self, cursor, row):
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]

        return d

    def query_with_barcode(self, barcode):
        """" given the barcode find the record that matches barcode from STOCK_DETAIL table"""
        self.dbc.row_factory = self.__sql_row_in_dict_factory
        cursor = self.dbc.cursor()
        search_result = cursor.execute('SELECT * FROM STOCK_DETAIL WHERE BARCODE = ?', (barcode,)).fetchone()
        print(search_result)

        return search_result

    def __del__(self):
        self.dbc.close()


if __name__ == "__main__":
    stock_report = StockReport()
    stock_report.login()
    stock_report.download_report() 
    stock_report.logout()

    loader = LoadReportInSQLite()
    loader.create_table()
    data = loader.data_from_excel_file()
    loader.load_data_in_table(data)

    search = QueryStock()    
    search.query_with_barcode(8906001238294)
