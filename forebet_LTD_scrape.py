import requests
from bs4 import BeautifulSoup
import sys

leagues = {
           'big5': ['It1', 'Es1', 'Fr1', 'PR', 'De1', 'Nl1'],
           'arg': ['Ar1', 'Ar2', 'Ar3', 'Ar4'],
           'wcq': ['WCQ'],  # world cup qualifications
           'cl': ['CL']  # champion's league
}
# bounds for draw quote:
down_q = 3.4
up_q = 5
# bounds for favourite team quote
down_fav = 1
up_fav = 3

# command line arguments (if present)
if len(sys.argv) == 2:
    key = sys.argv[1]
else:
    key = 0
    # print allowed leagues list
    print(' Available lists of leagues \n key : [league acronyms]')
    for k in leagues:
        print(k, leagues[k])
    # choose the allowed leagues to check
    while key not in list(leagues.keys()):
        key = input('enter the league key u wanna play kiddo : ')
        if key not in list(leagues.keys()):
            print('try again kiddo')
        
allowed_leagues = leagues[key]

# Web-scraping
html = ('https://www.forebet.com/en/football-tips-and-predictions-for-today/'
        'predictions-under-over-goals')
page = requests.get(html)
soup = BeautifulSoup(page.content, 'html.parser')
# day = soup.find(class_ = 'schema')
# day = soup.find(class_='contentmiddle')
# all matches have class tr_0 or tr_1
# day_matches = day.find_all(class_ = ['tr_0','tr_1'])
day_matches = soup.find_all(class_=['tr_0', 'tr_1'])

# diagnostic: check if the scraper sees the matches and if recog the leagues
'''
for match in day_matches:
    league = match.find(class_='shortTag').get_text(strip=True)
    print(league)
    print(league in allowed_leagues)
    print(match.find('a').get_text())
'''

for match in day_matches:
    league = match.find(class_='shortTag').get_text(strip=True)
    # the match is in the right league?
    if league in allowed_leagues:
        # print(match.find('a').get_text())
        if match.find(class_='lmin_td') is not None:
            match_playing = match.find(class_='lmin_td').get_text()
            if not match_playing.split():
                # if thematch is a probable over:
                if match.find(class_='predict').get_text() == 'Over':
                    match_name = match.find('a').get_text()
                    avg_score = match.find(class_='avg_sc').get_text()
                    # link to the web page of the match
                    match_html = (['https://www.forebet.com/{}'
                                  .format(match.find('a')['href'])][0])
                    match_page = requests.get(match_html)
                    match_soup = BeautifulSoup(match_page.content,
                                               'html.parser')
                    # match_booker1 = match_soup.find(class_ = 'susp_-1')
                    match_bookies = match_soup.find(class_='susp_-1')
                    match_odds = match_bookies.find_all(class_='odds',
                                                        limit=3)
                    float_odds = [float(m.get_text()) for m in match_odds]
                    draw_odd = float_odds[1]
                    one_odd = float_odds[0]
                    two_odd = float_odds[2]
                    if ((draw_odd > down_q)
                            & (draw_odd < up_q)
                            & (min(one_odd, two_odd) < up_fav)
                            & (min(one_odd, two_odd) > down_fav)):
                        print(match_name)
                        print('1x2 odds : {}'.format(float_odds))
                        print('exp # scores : {}'.format(avg_score))
