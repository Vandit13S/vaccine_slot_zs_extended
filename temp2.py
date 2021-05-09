from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import  pandas as pd
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.blocking import BlockingScheduler
import yagmail
global driver

yag_smtp_connection = yagmail.SMTP( user="freebikeduke@gmail.com", password="India*132", host='smtp.gmail.com')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class userlist(db.Model):
    srno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    n = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    filler1 = db.Column(db.String(500), nullable=True)
    filler2 = db.Column(db.String(500), nullable=True)
    filler3 = db.Column(db.String(500), nullable=True)
    filler4 = db.Column(db.String(500), nullable=True)
    filler5 = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return '<Pincode %r email %s>' % (self.n,self.email)


def get_details(n):
    global driver
    #print("Created by Vandit")
    # Here Chrome  will be used
    '''driver = webdriver.Chrome(ChromeDriverManager().install())
    now = datetime.now()'''

    # URL of website
    url = "https://www.cowin.gov.in/home"

    # Opening the website
    driver.get(url)

    # getting the text box by class name
    text_box = driver.find_element_by_id("mat-input-0")

    # entering pin code in text box
    text_box.send_keys('{0}'.format(n))

    # click on search button
    searchbutton = driver.find_element_by_class_name("pin-search-btn")
    searchbutton.click()

    '''clicking radio for age 18-44    

    checkBox = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "flexRadioDefault2")))   
    time.sleep(2)
    checkBox.click()
    isSelected = driver.find_element_by_id("flexRadioDefault2").is_selected()
    print(isSelected)'''

    # elements = driver.find_element_by_class_name("center-box")
    elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "center-box")))

    time.sleep(2)

    # Selenium hands the page source to Beautiful Soup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    covid_centres = soup.find_all("h5", {"class": "center-name-title"})
    centre = ""
    for i in covid_centres:
        centre += i.text + "\n"

    # flag
    contains_digit = False

    booking_status = soup.find_all("div", {"class": 'vaccine-box vaccine-box1 vaccine-padding'})

    res = ""
    for a_booking_status in booking_status:
        # check that slot is available
        result = a_booking_status.text
        if ("45+" in result):
            result = result.replace("45+", "")

            # check for any digit
            for number in result:
                if number.isdigit():
                    res = res + str(a_booking_status.text) + "\n"
                    contains_digit = True
                    break

    # driver.close()

    if (contains_digit):
        res="Vaccination slots are available at following centres for pincode {0} \n".format(n)+centre+"\n\n"+"Following is the list of available slots on for upto 1 week\nFor all the slots available at above centres visit https://www.cowin.gov.in/home \n"+ res
        return res
    else:
        res = "Vaccine is not available at any centre"
        return res

'''def write_data(res, n):
    now = datetime.now()
    f_dt=str(now.strftime("%Y%m%d_%H%M%S"))
    f_nm = str(n) + '_' + f_dt
    with open('{0}.txt'.format(f_nm), 'a') as f:
        f.write(res)'''

def get_email(n):
    pincode_to_check = userlist.query.filter_by(n=n).all()
    email_str = ""
    for i in pincode_to_check:
        email_str += str(i.email) + ","
    email_list = list(email_str.split(","))
    email_list.pop()
    email_list = list(set(email_list))
    return email_list

def send_mail(lst,sub,body):
    if body != "Vaccine is not available at any centre":
        yag_smtp_connection.send(lst, sub, body)

def driver_code():
    global driver
    pincode_to_check = userlist.query.all()
    driver = webdriver.Chrome(ChromeDriverManager().install())
    pin = set()
    for i in pincode_to_check:
        pin.add(i.n)
        #write_data(get_details(i.n), i.n)
    for i in pin:
        send_mail(get_email(i),"Vaccine Notifier {0}".format(i),get_details(i))

    driver.close()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(driver_code, 'interval', minutes=3)
    scheduler.start()

