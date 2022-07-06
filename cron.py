import os
os.system("sudo pkill python3")

os.system("sudo nohup python3 /home/ubuntu/chart_nikkei/charts_project/manage.py scrape &")
os.system("sudo nohup python3 /home/ubuntu/chart_nikkei/charts_project/manage.py runserver 0.0.0.0:80 &")
