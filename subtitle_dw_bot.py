from traceback import TracebackException
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from urllib.request import urlopen
import urllib.request
import os
from glob import glob
import zipfile
import traceback
from dotenv import load_dotenv
load_dotenv()

### Google API credentials
cse_api_key = os.environ.get("CSE_API_KEY")
cse_id = "87c1098fd4842328b" # https://cse.google.com/cse?cx=87c1098fd4842328b ONLY FOR YTS subtitle websites


hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}


# takes a id which is a folder and returns the srt file inside it. 
def get_file(id: str) -> str:
    path = glob(f'./{id}/*.srt')
    return path

# downloads and saves subtitle
def get_final_page(website_url, main_page_html, specific_lang_subs, id):
    ### requesting FINAL page
    i = 0
    while i<=len(specific_lang_subs):
        try:
            req2 = urllib.request.Request(specific_lang_subs[i][3], headers=hdr)
            f2 = urlopen(req2)
            dw_page_html = f2.read()
        except IndexError:
            dw_page_html = main_page_html

        def download_url(page):
            soup = BeautifulSoup(page, 'lxml')
            return soup.find('a', {'class': 'btn-icon download-subtitle'}).get('href')

        
        if website_url == "https://yifysubtitles.org":
            try:
                url = website_url + download_url(dw_page_html)
            except Exception as e:
                print(traceback.format_exc())
                return 'Subtitle not found.' 
                
        else:
            url = download_url(dw_page_html)

        try: 
            file_name = id + '.zip'
            req3 = urllib.request.Request(url, headers=hdr)
        except Exception as e:
            print(traceback.format_exc())
            return 'Try again.'
        
        ### downloading the zip file and storing
        dw_file_location = './'
        dw_file_path = dw_file_location + file_name

        try:
            u = urlopen(req3)
            f = open(dw_file_path, 'wb')
            meta = u.info()

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
            f.close()

            ### Unzipping file and deleting the zip
            with zipfile.ZipFile(dw_file_path, 'r') as zip_ref:
                zip_ref.extractall(dw_file_location + id)

            path = get_file(id)

            os.remove(dw_file_path)

            return path[0]


        except urllib.error.HTTPError:
            return 'Try again.'
    

def get_subtitle(query: str, id: str):
    lang = 'english'

    try: 
        def google_search(search_term, cse_api_key, cse_id, **kwargs):
            service = build("customsearch", "v1", developerKey=cse_api_key)
            res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

            try:
                return res['items']
            except KeyError:
                return False

        results = google_search(query, cse_api_key, cse_id, num=1)

    except Exception as e:
        print(traceback.format_exc())
        return 'Subtitle not found.' 

    if results != False:
    
        try:
            ### Grabbing all subtitles from yts-subs
            main_url = results[0]['link']

            sliced_main_url = main_url.split('/')

            website_url = sliced_main_url[0] + '//' + sliced_main_url[2]

            def get_page_html (url, **kwargs):
                hdr = kwargs.get('headers', None)
                if hdr != None:  
                    req = urllib.request.Request(url, headers=hdr)
                else:
                    req = urllib.request.Request(url)
                f = urlopen(req)
                return f.read()

            main_page_html = get_page_html(main_url, headers=hdr)
            specific_lang_subs = []

            try:
                # checking if main page is the final page
                if 'movie-imdb' in sliced_main_url  or 'movies' in sliced_main_url or 'movie' in sliced_main_url or 'movie-subtitles' in sliced_main_url :

                    ### Grabbing final URLs
                    def table_rows(page):
                        soup = BeautifulSoup(page, 'lxml')
                        table = soup.find('tbody')

                        return table.find_all('tr')

                    table_rows = table_rows(main_page_html)

                    ratings = []
                    for tr in table_rows:
                        try:
                            ratings.append(tr.find('span', {'class': 'label'}).text)
                        except:
                            ratings.append('0')

                    languages = []
                    for tr in table_rows:
                        languages.append(tr.find('span', {'class': 'sub-lang'}).text.lower())

                    dw_page_urls = []
                    titles = []
                    for tr in table_rows:
                        dw_page_urls.append(tr.find('a').get('href'))
                        titles.append(tr.find('a').text)

                    # KEYS [rating, language, title, download_page_URL]
                    all_subs = list(map(list, zip(ratings, languages, titles, dw_page_urls)))

                    for sub in all_subs:
                        if sub[1] == lang:
                            try:
                                title = sub[2].split('[')[1]
                                if title == "YTS.AG]" or title == "YTS.MX]":
                                    specific_lang_subs.append(sub)
                            except IndexError:
                                pass

                    if len(specific_lang_subs) == 0:
                        for sub in all_subs:
                            if sub[1] == lang:
                                specific_lang_subs.append(sub)
            
                    return get_final_page(website_url, main_page_html, specific_lang_subs, id)
                
                else:
                    path = get_final_page(website_url, main_page_html, specific_lang_subs, id)
                    return path

            except Exception:
                print(traceback.format_exc())
                return "Subtitle not found."



        except Exception :
            print(traceback.format_exc())
            return 'Subtitle not found.' 

    else:
        
        return "Subtitle not found."

print(get_subtitle("wakanda forever", "123"))