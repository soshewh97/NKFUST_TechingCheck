#-*- coding:utf-8 -*-
#/usr/bin/python2.7
import requests
import re
import urllib
import sys
import time
from bs4 import BeautifulSoup
session = requests.Session()
#session.cookies.get_dict()
UserName = raw_input('身份證字號:')
PassWord = raw_input('password:')

reload(sys)
sys.setdefaultencoding("utf-8")

def myheaders(referer):
    my_headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
        "Referer": referer,
        }
    return my_headers

proxies = {
        "http":"http://192.168.1.51:8080",
        "https":"http://192.168.1.51:8080",
        }
cook={}

def reqcookies(cook_na,cook_va):
    cook[cook_na]=cook_va
    return cook

def gethomework(Url):
    get_homework = session.get(Url,)
    while get_homework.status_code == 500 :
        print '500'
        time.sleep(2)
        get_homework = session.get(Url,)
    return get_homework

#設定post的key以及value
postlist = {"Login1$UserName":UserName,
        "Login1$Password":PassWord,
        "Login1$LoginButton.x":"0",
        "Login1$LoginButton.y":"0",
        "__EVENTTARGET":"",
        "__EVENTARGUMENT":""}

teching_main_url = 'http://teaching.nkfust.edu.tw/Course'
teching_url = 'http://teaching.nkfust.edu.tw/Course/login.aspx?AspxAutoDetectCookieSupport=1'
teching_url_login = 'http://teaching.nkfust.edu.tw/Course/login.aspx'
#teching_homework = 'http://teaching.nkfust.edu.tw/Course/homework/teacher/main.aspx'
teching_transfer = 'http://teaching.nkfust.edu.tw/Course/transfer.aspx'

first_cookies = session.get(teching_url_login,)
if (first_cookies.status_code == 200):
    print "[info]連接成功"
    login_cookies =  first_cookies.cookies.get_dict()
    login_cookies = reqcookies('ASP.NET_SessionId',login_cookies['ASP.NET_SessionId'])
    getlogin_post = BeautifulSoup( first_cookies.text , 'html.parser' )  #BS4解析網頁 抓取post 內容

    for postvalue in getlogin_post.find_all('input'):
        if (postvalue.get('value')):
            postlist[postvalue.get('name')] = postvalue.get('value')

    tech_login = session.post(teching_url ,headers = myheaders(teching_url_login) ,cookies = login_cookies ,data=postlist ,allow_redirects=False ,)

    if (tech_login.status_code == 302):
        print '[info]登入成功!'
        get_tutor =  reqcookies('Nkfust_Authentication',tech_login.cookies['Nkfust_Authentication'])
        get_tutor = {'Nkfust_Authentication':tech_login.cookies['Nkfust_Authentication'] }
        print '[info]取得課程'
        tutor_url = "http://teaching.nkfust.edu.tw/Course/tutor/tutor_1.aspx"
        gettutor =  session.get(tutor_url,)

        if (gettutor.status_code == 200):
            gettutor_cht = BeautifulSoup(gettutor.text,'html.parser')
            courseID ={}
            for getform in gettutor_cht.select('font > a'):
                if (getform.get('href')[3:4] == 'w' ):
                    print getform.get_text() ," 課號" , ''.join(re.findall('\d',getform.get('href')))[:4]
                    courseID[''.join(re.findall('\d',getform.get('href')))[:4]] =  teching_main_url+getform.get('href')[2:]

            input_course = raw_input('courseID:')
            #print courseID[input_course]
            acy = re.findall('acy=.*?\&',courseID[input_course]) #取得學年度
            semester =  re.findall('semester=.*?\&',courseID[input_course]) #取得學期 上 or 下
            pcrsno = re.findall('pcrsno=.*?\&',courseID[input_course]) #取得永久課號
            crsname = re.findall('crsname=.*?\&' ,courseID[input_course]) #課程名稱
            year_type = re.findall('year_type=.*',courseID[input_course]) #取得year_type


            teching_homework = 'http://teaching.nkfust.edu.tw/Course/homework/teacher/'
            teching_origin = 'http://teaching.nkfust.edu.tw/Course'

            acy = acy[0][4:].strip('&')
            print '[info]學年度：%s' % acy
            semester = semester[0][9:].strip('&')
            print '[info]學期：%s' % semester
            pcrsno = pcrsno[0][7:].strip('&')
            print '[info]永久課號：%s' % pcrsno
            crsname = crsname[0][8:].strip('&')
            print '[info]課程名稱：%s' % crsname
            year_type = year_type[0][10:]
            print '[info]year_type：%s' % year_type

            homework = session.get(teching_origin + '/wcrs_home.aspx?crsno=%s&acy=%s&semester=%s&pcrsno=%s&crsname=%s&year_type=%s' %(input_course,acy,semester,pcrsno,crsname,year_type),  )

            homework_url = teching_homework + 'main.aspx?acy=%s&semester=%s&crsno=%s&crsname=%s' % (acy,semester,input_course,crsname)
            homework = session.get(homework_url,  )
            #print homework.url
            if ( homework.status_code == 200 ):
                homework_comment = BeautifulSoup(homework.text,'html.parser')
                gethref_comment = homework_comment.select('a[href^=comment.aspx?grouping]')
                print  '資料比數：',len(gethref_comment)
                homework_array = {}
                homework_name = []
                for check_homework in range(len(gethref_comment)):
                    get_homeurl = gethomework( teching_homework + gethref_comment[check_homework].get('href'))
                    homework_array[check_homework+1] = []
                    homeworklist_soup = BeautifulSoup(get_homeurl.text,'html.parser')
                    homework_table = homeworklist_soup.find_all('table',attrs = {'align':'Center'})

                    for homework_tr in homework_table[0].find_all('tr'):
                        homework_td = homework_tr.find_all('td')
                        for homework_list in range(len(homework_td)):
                            if (homework_list == 3):
                                homework_name.append(homework_td[homework_list].get_text().strip())
                                #print (homework_td[homework_list].get_text().strip())
                            if (homework_list == 10) :
                                #print homework_td[homework_list].get_text()
                                if not  ( homework_td[homework_list].get_text().strip()) :
                                    homework_array[check_homework+1].append(0)
                                    #print '0'
                                else:
                                    homework_array[check_homework+1].append(1)
                                    #print '1'

            #print homework_array
            for i in  range(len(homework_array[1])):
                print homework_name[i],
                for j in range(len(homework_array)):
                    print homework_array[j+1][i],
                print
