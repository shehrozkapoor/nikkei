from bs4 import BeautifulSoup
import requests
from datetime import datetime
from .models import LineData


def line_data(end_date):
    url = "http://225navi.com/data/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")
    rows = table.findChildren(['th', 'tr'])
    for row in rows:
        headers = row.findChildren('th')
        for header in headers:
            head_val=header.string.strip()
            try:
                if head_val !="日付":
                    get_date = datetime.strptime(head_val,'%Y/%m/%d').strftime('%Y/%m/%d')
                    if get_date == end_date.strftime('%Y/%m/%d'):
                        cells = row.findChildren('td')
                        for idx,cell in enumerate(cells):
                            if idx == 3:
                                num = cell.text.strip()
                                print(f"this is line_num {num}")
                                try:
                                    line_data=LineData.objects.get(date=get_date.replace('/','-'),line_num=num,is_topix=False)
                                    print(f"data already saved on {get_date}")
                                except:
                                    line_data=LineData.objects.create(date=get_date.replace('/','-'),line_num=num,is_topix=False)
                                    print(f"data saved on {get_date}")
                        return "done"
            except:
                print(f"except run on {head_val}")
    return "done"


def line_data_7to10(end_date):
    url = "http://225navi.com/data/data5/"
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    soup.prettify()

    container = soup.find(class_="sc_table")
    table = container.find("table")
    rows = table.findChildren(['th', 'tr'])
    for row in rows:
        headers = row.findChildren('th')
        for header in headers:
            head_val=header.string.strip()
            try:
                if head_val !="日付":
                    get_date = datetime.strptime(head_val,'%Y/%m/%d').strftime('%Y/%m/%d')
                    if get_date == end_date.strftime('%Y/%m/%d'):
                        cells = row.findChildren('td')
                        for idx,cell in enumerate(cells):
                            if idx == 3:
                                num = cell.text.strip()
                                print(f"this is line_num {num}")
                                try:
                                    line_data=LineData.objects.get(date=get_date.replace('/','-'),line_num=num,is_topix=True)
                                    print(f"data already saved on {get_date}")
                                except:
                                    line_data=LineData.objects.create(date=get_date.replace('/','-'),line_num=num,is_topix=True)
                                    print(f"data saved on {get_date}")
                        return "done"
            except:
                print(f"except run on {head_val}")
    return "done"



