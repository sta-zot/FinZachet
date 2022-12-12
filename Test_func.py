############################ Import libs#################################################

import linecache
import re
import sys
from time import sleep

import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from questions_db import questions_list



##############################################################################################

########################################Functions##############################################


def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def select_answer(
        drv: webdriver,
        questions_selector: str = '//div[@class = "questionsMainLk__main-main-title"]') -> None:

    questions = drv.find_element(By.XPATH, questions_selector)
    que_txt = questions.text.split('.')[0]
    answers = questions_list[que_txt]
    for answer in answers:
        selector = f'//span[text() = "{answer.strip()}"]'
        drv.find_element(By.XPATH, selector).click()


# Function for start automatic executing test
def stoper() -> None:
    answer = input("Continue? Yes/No: ").lower()
    if answer == "yes":
        return None
    elif answer == "no":
        sys.exit(1)


def start_test(user: dict, drv: webdriver, url: str) -> int:
    """
    Функция принимает словарь с данными пользователя и проходит тест
    """
    wait = WebDriverWait(drv, 10)

    drv.get(url)
    element = WebDriverWait(drv, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Участвовать")]')))
    element.click()
    del element
    sleep(0.5)
    email = drv.find_element(By.XPATH, '//input[@placeholder = "Email"]')
    email.clear()
    email.send_keys(user["email"])
    paswd = drv.find_element(By.XPATH, '//input[@placeholder = "Пароль"]')
    paswd.clear()
    paswd.send_keys(user['pass'])
    paswd.send_keys(Keys.ENTER)
    sleep(1)
    del email, paswd
    sleep(1)
    # stoper()
    # Edit profile
    try:
        drv.find_element(
            By.XPATH,
            ('//div[@class = "authorizationForm__inner-title" and text() = "Изменить данные профиля"]')
        )
        print("Заполнение формы при регистрации")
    except Exception:
        print("Изменение Профиля")
        drv.find_element(By.XPATH, ('//span[text() = "Изменить"]')).click()

    sleep(1)
    if drv.find_element(By.XPATH, '//input[@placeholder = "Имя (будет указано в сертификате)" ]'):
        uname = drv.find_element(By.XPATH, '//input[@placeholder = "Имя (будет указано в сертификате)" ]')
        uname.clear();
        uname.send_keys(user["name"]);
        del uname
    if user["gender"].lower() == "м":
        drv.find_element(By.XPATH, '//*[.="Муж"]').click()
    else:
        drv.find_element(By.XPATH, '//*[.="Жен"]').click()
    # Change user age
    u_age = drv.find_element(By.XPATH, '//input[@placeholder = "Введите возраст"]')
    sleep(1)
    ActionChains(drv) \
        .move_to_element(u_age) \
        .pause(1) \
        .click_and_hold() \
        .pause(1) \
        .send_keys(Keys.BACKSPACE) \
        .send_keys(Keys.BACKSPACE) \
        .send_keys(user["age"]). \
        perform()
    # Change education level
    drv.find_element(By.XPATH, '//input[@placeholder = "Образование"]').click()
    if drv.find_element(By.XPATH, '//div[@class = "select__item" and contains(text(), "профес")]'):
        drv.find_element(By.XPATH, '//div[@class = "select__item" and contains(text(), "профес")]').click()
    # Change region
    drv.find_element(By.XPATH, '//input[@placeholder = "Регион"]').click()
    if drv.find_element(By.XPATH, '//div[@class = "select__item" and contains(text(), "Рязан")]'):
        drv.find_element(By.XPATH, '//div[@class = "select__item" and contains(text(), "Рязан")]').click()
    sleep(1)

    drv.find_element(By.XPATH, ('//div[@class = "button__name" and text() = "Сохранить"] ')).click()
    sleep(1)
    # Starting test
    print("Starting test")
    try_count = 3

    while try_count > 0:
        try:
            participate = drv.find_element(By.XPATH, '//button[.= "Участвовать"]')
            print("Executing JS script")
            drv.execute_script('Elem =  arguments[0]; Elem.click()', participate)
            # ActionChains(drv)\
            #     .move_to_element(participate)\
            #     .pause(1)\
            #     .click_and_hold()\
            #     .pause(1)\
            #     .perform()

            break
        except TimeoutException as err:
            again = drv.find_element('//button[contains(text(), "Еще раз")]')
            print("Executing JS script")
            drv.execute_script('Elem =  arguments[0]; Elem.click()', again)
            again.click()



    sleep(1)

    if drv.find_element(By.XPATH, '//button[.="Начать"]'):
        drv.find_element(By.XPATH, '//button[.="Начать"]').click()
    sleep(1)
    try:
        if drv.find_element(By.XPATH, '//button[.="Завершить"]'):
            drv.find_element(By.XPATH, '//button[.="Завершить"]').click()
            sleep(1)
            drv.find_element(By.XPATH,'//a[@class = "lkButton headerLk__btn-lk"]').click()
            participate = drv.find_element(By.XPATH, '//button[.= "Участвовать"]')
            print("Executing JS script")
            drv.execute_script('Elem =  arguments[0]; Elem.click()', participate)
            sleep(1)
            if drv.find_element(By.XPATH, '//button[.="Начать"]'):
                drv.find_element(By.XPATH, '//button[.="Начать"]').click()
    except NoSuchElementException as e:
        pass





    questions_count = int(
        re.match(
            r"\D*?(\d+)",
            drv.find_element(By.XPATH, '//span[@class = "questionsMainLk__main-nums-big"]/following-sibling::span').text)\
        .group(1)
    )
    print(questions_count)

    iter_c = questions_count
    while iter_c > 0:
        sleep(0.5)
        select_answer(drv)
        bt_next = drv.find_element(By.XPATH, '//div[.= "Следующий"]')
        bt_next.click()
        iter_c = iter_c - 1

    # Send certificate to email
    drv.find_element(By.XPATH, '//button[@class = "linkAlt-black" and contains(Text(), "Отправить")]').click()
    # close_email_notification
    drv.find_element(By.XPATH, '//i[@class = "icon-crossAlt"]').click()
    # Quit to main page
    drv.find_element(By.XPATH, '//a[@class = "lkButton"]').click()

    while True:
        if input('Cosing browser? "YES/NO"').lower() == 'yes':
            drv.close()
            drv.quit()
            print("GoodBy")
            sys.exit(0)

    drv.quit()
    return 0


# Function for check headers or value may be not need
def check_in(what_ch, where_ch):
    for item in what_ch:
        if item in where_ch:
            return True
        else:
            return False


# Initiation
def init_Chrome():
    service = Service(executable_path="WebDrivers/chromedriver.exe")
    useragent = UserAgent()
    drv_options = webdriver.ChromeOptions()
    drv_options.add_argument(f"user-agent={useragent.random}")
    drv_options.add_argument("--disable-blink-features=AutomationControlled")
    # drv_options.add_argument("--headless")
    # drv_options.headless = True
    d = webdriver.Chrome(service = service, options=drv_options)
    return d


def init_Firefox():
    d = webdriver.Firefox()
    return d


def get_users(path: str) -> list:
    '''Функция принимает путь к файлу и возращает список словарей в формате имя-пол-возраст-email'''
    user_list = []
    # Считываем данные из файла при помощи библиотеки Pandas
    excel_data = pd.read_excel(path)
    # Конвертируем данные в CSV
    users_raw = excel_data.to_csv().split(sep="\r\n")
    headers = excel_data.columns.tolist()
    iter_count = 0
    # В цикле собираем список в нужном формате
    for row in users_raw:
        if check_in(headers, row):
            continue
        row = row.split(sep=',')
        iter_count = iter_count + 1
        try:
            # print([{headers[0]:row[1], headers[1]:row[2], headers[2]:row[3],headers[3]:row[4]}])
            user_list.append({headers[0]: row[1], headers[1]: row[2], headers[2]: row[3], headers[3]: row[4]})
        except IndexError as error:
            print(f"ERROR in {iter_count} iteration.\nError description: {error} : {row}")
            continue
    return user_list


def check_driver_work(drv: webdriver, url: str) -> None:
    drv.get(url)
    print(drv.page_source.encode("utf-8"))
    sleep(10)
    drv.quit()


if __name__ == "__main__":
    pass
