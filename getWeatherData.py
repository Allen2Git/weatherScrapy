# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pandas as pd
import requests
import calendar
import os

# try:
# 	request = urllib2.Request(url)
# 	response = urllib2.urlopen(request)
# 	htmlString = response.read()
# #	print html

# except urllib2.URLError, e:
#     if hasattr(e,"code"):
#         print e.code
#     if hasattr(e,"reason"):
#         print e.reason

# soup = BeautifulSoup(htmlString,"lxml")
# table = soup.find_all('table')[4]

# pd_tbl = pd.DataFrame(columns=range(0,8),index=[0])

class HTMLTableParser:
   
    def parse_url(self, url, tableNum):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        return self.parse_html_table(soup.find_all('table')[tableNum])
                  

    def parse_html_table(self, table):
        n_columns = 0
        n_rows=0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):
            
            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows+=1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)
                    
            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles %d do not match the number of columns %d" % (len(column_names),n_columns)) 

        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns = columns,
                          index= range(0,n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text(strip=True)
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1
                
        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass
        
        return df


#weatherUrl = "https://www.wunderground.com/history/airport/ZBYN/2017/1/15/DailyHistory.html?req_city=Taiyuan&req_statename=China&reqdb.zip=&reqdb.magic=&reqdb.wmo="
for year in range(1996, 2018):
	for mon in range(1,13):
		for day in range(1,calendar.monthrange(year,mon)[1]+1):
			fileName = "weather-%d-%d-%d.csv"%(year,mon,day)
			if not os.path.isfile(fileName):
				weatherUrl = "https://www.wunderground.com/history/airport/ZBYN/%d/%d/%d/DailyHistory.html?req_city=Taiyuan&req_statename=China&reqdb.zip=&reqdb.magic=&reqdb.wmo="%(year,mon,day)
				hp = HTMLTableParser()
				table = hp.parse_url(weatherUrl,4) # Grabbing the table from the tuple
				table["Time (CST)"]= "%d-%d-%d "%(year,mon,day) + table["Time (CST)"]
				#print table
				#table.head()
				table.to_csv(fileName, encoding='utf-8',index = False)
				print "weather file %s saved \n " % fileName

