from selenium import webdriver
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import re
import time

class HKJCRaceResult:
    """ Load a HKJC race result webpage and extract informations
        1. Race tab
        2. Performance
        3. Result
    """
    def __init__(self, browser_path):
        """ initiate a browser

        Parameters: browser_path (str) - the browser_path, recommend to use firefox
        """
        self.browser = webdriver.Firefox(executable_path=browser_path)

    def load_race_source(self, year, month, day, race_num, quit_session=False):
        """ load the specific race result

        Parameters: year (str) - year
                    month (str) - month
                    day (str) - day
                    race_num (str) - the race number
                    quit_session (boo) - quit this session or not, optional, default is False
        """
        url = 'https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate={}/{}/{}&RaceNo={}'.format(year, month, day, race_num)

        self.browser.get(url)

        counter = 0
        while True:
            counter += 1
            time.sleep(5)
            self.soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            check_if_load = self.soup.find_all('div', class_='localResults commContent')

            if check_if_load:
                break
            elif counter == 5:
                print('Failed to load expected page source')
                break
            else:
                continue

        if quit_session:
            self.close_browser()

    def extract_race_tab(self):
        """ extract race tab
        """
        # race tab
        race_tab = self.soup.find_all('div', class_='race_tab')[0]
        rt_table = race_tab.find_all('table')[0].find_all('td')
        rt_info = [i.text for i in rt_table if i.text != '']

        return rt_info

    def extract_race_performance(self):
        """ extract race performance
        """
        # performance
        performance = self.soup.find_all('div', class_='performance')[0]
        # table header
        p_table_header = [i.text for i in performance.find_all('thead')[0].find_all('td')]
        # table content
        p_table = performance.find_all('table')[0].find_all('tbody')[0].find_all('td')
        # reshape dimension
        p_table_arr = np.array([re.sub(r'\s+', ' ', i.text) for i in p_table]).reshape((-1,len(p_table_header)))
        performance_info = pd.DataFrame(p_table_arr, columns=p_table_header)

        return performance_info

    def extract_race_result(self):
        """ extract race result
        """
        # result
        result = self.soup.find_all('div', class_='dividend_tab f_clear')[0].find_all('table')[0]
        # table header
        result_header = [i.text for i in result.find_all('thead')[0].find_all('tr', class_='bg_e6caae')[0].find_all('td')]
        # table content
        result_tr = result.find_all('tbody')[0].find_all('tr')
        # process table content
        max_td = np.max([len(i.find_all('td')) for i in result_tr])
        all_tr = list()

        # pad length not max
        for j in result_tr:
            sec_len = len(j.find_all('td'))
            if sec_len < max_td:
                this_sec = [all_tr[-1][0]]*(max_td-sec_len) + [i.text for i in j.find_all('td')]
            else:
                this_sec = [i.text for i in j.find_all('td')]
            all_tr.append(this_sec)

        result_info = pd.DataFrame(all_tr, columns=result_header)

        return result_info

    def close_browser(self):
        """ close the current session
        """
        self.browser.close()
