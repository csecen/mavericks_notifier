#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import smtplib
import requests
import config
import re

########### HELPERS ###########
# define send email function
def send_email(message):
    gmail_user = config.user
    gmail_password = config.password
    email_text = message

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gmail_user, email_text)
        server.close()
    except:
        exit(1)
###############################

# collect a few urls related to mavericks
msw_url = 'https://magicseaweed.com/Mavericks-Half-Moon-Bay-Surf-Report/162/'
surfline_url = 'https://www.surfline.com/surf-news/'
surfer_url = 'https://www.surfer.com/'

# scrape the conditions for 5 to 7 days out and determine if they are good
msw = requests.get(msw_url)
msw_soup = BeautifulSoup(msw.content, 'html.parser')
table = msw_soup.find('div', attrs={'class':'table-responsive-xs'})
days = table.find_all('tbody')
conditions = []

for day in days[-3:]:
    date = day.find('h6').text   # store the date
    rows = [row for row in day.find_all('tr')]   # collect every row in the table
    cond_count = 0

    for row in rows[1:9]:
        # collect that the data points needed to forecast good surf
        data_points = row.find_all('td')
        surf_height = data_points[1].text
        period = data_points[4].text
        swell = data_points[5]['title']
        wind = data_points[13]['title']
        
        # parse out the relevant data from each of the strings
        height = re.search('([0-9])-([0-9])', surf_height)
        min_height = int(height.group(1))
        max_height = int(height.group(2))
        period_time = int(re.search('[0-9][0-9]', period).group())
        w_s_match = '[W|N|S|E]{1,3}'
        swell_dir = re.search(w_s_match, swell).group()
        wind_dir = re.search(w_s_match, wind).group()
        
        # check that all the conditions add up to ideal conditions
        if (min_height > 20 and period > 15 and (swell_dir == 'W' or swell_dir == 'WNW' or swell_dir == 'NW')
            and (wind_dir == 'E' or wind_dir == 'ESE' or wind_dir == 'SE')):
            cond_count += 1
            
    # if there are enough times with good conidtions add the day to the list
    if cond_count >= 4:
        cond = '{0} will have good, consistant conditions'.format(date)
        conditions.append(cond)

# scrape news pages looking for a trend of the term mavericks
surfline = requests.get(surfline_url)
surfline_news = BeautifulSoup(surfline.content, 'html.parser')

surfer = requests.get(surfer_url)
surfer_news = BeautifulSoup(surfline.content, 'html.parser')

mavs_pattern = '[M|m][A|a][V|v][E|e][R|r][I|i][C|c][K|k][S|s]'

surfline_mavs = re.findall(mavs_pattern, surfline_news.text)
surfer_mavs = re.findall(mavs_pattern, surfer_news.text)

mavs_len = len(surfline_mavs) + len(surfer_mavs)

if mavs_len > 5 and len(conditions) > 1:
    opening = 'Mavericks is being mentioned in the news a lot and the conditions look good!\n\n'
    body = '\n'.join(conditions)
    ending = '\n\nBe ready!!'
    message = opening+body+ending
    send_email(message)
elif mavs_len > 5:
    message = 'Mavericks is being mentions in the news a lot, look out for something happening!'
    send_email(message)
elif len(conditions) > 1:
    opening = 'The conditions are starting to look good!\n\n'
    body = '\n'.join(conditions)
    ending = '\n\nLook out for the news'
    message = opening+body+ending
    send_email(message)
