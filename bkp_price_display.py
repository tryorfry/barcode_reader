import conf
import mechanize
import Cookie
import cookielib

import pprint
pp = pprint.PrettyPrinter(indent=4)

cookiejar = cookielib.LWPCookieJar()
br = mechanize.Browser()
br.set_cookiejar(cookiejar)
br.addheaders = [("User-agent", "Mozilla/5.0")] 
br.set_handle_robots(False)



res = br.open(conf.login_url)
br.addheaders = [('Cookie','cookiename=cookie value')]
pp.pprint(res.geturl()) 
pp.pprint(br.forms()[0])
print(br.forms())

first_form = br.forms()[0].name
print(first_form)
br.select_form(first_form)

br.set_all_readonly(False)

br.form.new_control('hidden', '__LASTFOCUS',   {'value': 'sss'})    
br.form.new_control('hidden', '__EVENTTARGET',   {'value': 'sss'})  
br.form.new_control('hidden', '__EVENTARGUMENT',   {'value': 'sss'})  
br.form.new_control('hidden', '__VIEWSTATE',   {'value': 'sss'})
br.form.new_control('hidden', '__VIEWSTATEGENERATOR',   {'value': 'sss'})
br.form.new_control('hidden', '__EVENTVALIDATION', {'value': 'sds'})

br.form['UserName'] = conf.user_name
br.form['Password'] = conf.password
#br.form['ddlLanguages'] = 0
# Login
br.submit()
print(br.response().read())
os.exit;

res1 = br.open('https://s2.equipweb.biz/NIlaTradersPteLtd/CRReport/CRReport.aspx?r=StockOnHandReportItemSummary.rpt')
content = br.response().read()
print(res1.geturl())



"""import requests
import conf
import pprint
pp = pprint.PrettyPrinter(indent=4)

session = requests.session()

session.get(conf.login_url)
pp.pprint(session.cookies)
os.exit


headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Raspbian Chromium/78.0.3904.108 Chrome/78.0.3904.108 Safari/537.36


res = session.post(conf.login_url, headers=headers, data={'UserName': conf.user_name, 'Password': conf.password, 'ddlLanguages': conf.language})
print res.text
"""


