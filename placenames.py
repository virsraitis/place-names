# -*- coding: utf-8 -*-
"""
Gathers place names from https://vietvardi.lgia.gov.lv/vv/to_www.sakt
"""

def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open("./placenames_log.txt", "a") as f:
        f.write(timestamp + ' : ' + message + '\n')
        print(timestamp + ' : ' + message + '\n')

def add_results_to_df (df):
    html = driver.page_source
    data = BeautifulSoup(html, 'html.parser')

    table = data.find("table", {"id": "rezult"})
    tbody = table.find("tbody")
    rows = tbody.find_all('tr')

    for i, row in enumerate(rows):
        # if i==2:
        #     log_progress('Pamatnosaukums: ' + col[1].contents[0].replace('\n',''))
        if i>=2:
            col = row.find_all('td')
            if (len(col)!=0):
                data_dict = {'Name': col[1].contents[0].replace('\n',''),
                             'Object_ID': col[2].contents[0].replace('\n',''),
                             'Object_type': col[3].contents[0].replace('\n',''),
                             'Object_status': col[4].contents[0].replace('\n',''),
                             'Official_name': col[5].contents[0].replace('\n',''), # Source abbreviation in square brackets
                             'Other_names': col[6].contents[0].replace('\n',''),
                             'Administrative_or_territorial_unit': col[7].contents[0].replace('\n',''),
                             'Latitude': col[8].contents[0].replace('\n',''),
                             'Longitude': col[9].contents[0].replace('\n','')}
                for nobr in col[6].find_all('nobr'):
                    data_dict['Other_names'] += nobr.contents[0] + '\n'
                data_dict['Other_names'] = data_dict['Other_names'].rstrip('\n')
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df, df1], ignore_index=True)
    return df

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

table_attribs = ['Name', 'Object_ID', 'Object_type', 'Object_status', 'Official_name', 'Other_names', 
                 'Administrative_or_territorial_unit', 'Latitude', 'Longitude']
driver = webdriver.Chrome()
df = pd.DataFrame(columns=table_attribs)
url = 'https://vietvardi.lgia.gov.lv/vv/to_www.sakt'

log_progress('Start')
driver.get(url)

driver.implicitly_wait(0.5)

# Objekta veids / Object type
select_element_veids = driver.find_element(By.NAME, 'p_veids')
select_veids = Select(select_element_veids)

select_veids.select_by_value('apdzīvotā vieta')

# Ierakstu skaits / Results per page
select_element_q_size = driver.find_element(By.NAME, 'p_ier_sk')
select_q_size = Select(select_element_q_size)

select_q_size.select_by_value('100')

# Meklēt / Search button
submit_button = driver.find_element(by=By.NAME, value="Meklet")
submit_button.click()

df = add_results_to_df(df)

# Nākamie 100 ieraksti / Next page of results
while True:
    try:
        submit_next_page = driver.find_element(by=By.NAME, value="p_nak")
    except NoSuchElementException:
        df = add_results_to_df(df)
        df.to_csv('./data_frame.csv', index=False)
        log_progress('End')
        break
    finally:
        submit_next_page.click()
        df = add_results_to_df(df)

driver.quit()