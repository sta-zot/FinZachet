############################ Import libs#################################################

import linecache
import re
import sys
from time import sleep

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
def start_test(user: dict, drv: webdriver, url: str) -> int:
    """
    Функция принимает словарь с данными пользователя и проходит тест
        :param: user Параметр с типом словарь содержащий информацию о проходящем иестирование/ A parameter with the dictionary type containing information about the being tested
        :param: drv Параметр являющийся объектом класса webdriver./ A parameter that is the webdriver instances
        :param: url Строковый параметр содержащий адрес WEB сайта/ This is string parameter containing the address of a WEB site
    """
    wait = WebDriverWait(drv, 10)
    drv.get(url)
    print(f"{user['name']} начал тестирование")
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
    paswd.send_keys(user['password'])
    paswd.send_keys(Keys.ENTER)
    sleep(1)
    del email, paswd
    # Edit profile
    try:
        drv.find_element(
            By.XPATH,
            ('//div[@class = "authorizationForm__inner-title" and text() = "Изменить данные профиля"]')
        )
        print("Заполнение формы при регистрации")
    except Exception:
        print("Изменение данных в профиле")
        drv.find_element(By.XPATH, ('//span[text() = "Изменить"]')).click()
    sleep(1)
    if drv.find_element(By.XPATH, '//input[@placeholder = "Имя (будет указано в сертификате)" ]'):
        uname = drv.find_element(By.XPATH, '//input[@placeholder = "Имя (будет указано в сертификате)" ]')
        uname.clear()
        uname.send_keys(user["name"])
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
    if drv.find_element(By.XPATH, f'//div[@class = "select__item" and contains(text(), "{user["edu_lvl"]}")]'):
        drv.find_element(By.XPATH, f'//div[@class = "select__item" and contains(text(), "{user["edu_lvl"]}")]').click()
    # Change region
    drv.find_element(By.XPATH, '//input[@placeholder = "Регион"]').click()
    if drv.find_element(By.XPATH, f'//div[@class = "select__item" and contains(text(), "{user["region"]}")]'):
        drv.find_element(By.XPATH, f'//div[@class = "select__item" and contains(text(), "{user["region"]}")]').click()
    sleep(1)
    drv.find_element(By.XPATH, ('//div[@class = "button__name" and text() = "Сохранить"] ')).click()
    sleep(1)
    # Starting test
    print("Начало тестирования:")
    try_count = 3
    try:
        again = drv.find_element(By.XPATH, '//button[.= "Еще раз"]')
        drv.execute_script('Elem =  arguments[0]; Elem.click()', again)
    except NoSuchElementException as err:
        participate = drv.find_element(By.XPATH, '//button[.= "Участвовать"]')
        drv.execute_script('Elem =  arguments[0]; Elem.click()', participate)
    sleep(1)

    # if drv.find_element(By.XPATH, '//button[.="Начать"]'):
    #     drv.find_element(By.XPATH, '//button[.="Начать"]').click()
    # sleep(1)
    try:
        if drv.find_element(By.XPATH, '//button[.="Завершить"]'):
            drv.find_element(By.XPATH, '//button[.="Завершить"]').click()
            sleep(1)
            drv.find_element(By.XPATH, '//a[@class = "lkButton headerLk__btn-lk"]').click()
            participate = drv.find_element(By.XPATH, '//button[.= "Участвовать"]')
            print("Executing JS script")
            drv.execute_script('Elem =  arguments[0]; Elem.click()', participate)
            sleep(1)
            if drv.find_element(By.XPATH, '//button[.="Начать"]'):
                drv.find_element(By.XPATH, '//button[.="Начать"]').click()
    except NoSuchElementException as e:
        pass
    # Получаем количество вопросов
    questions_count = int(
        re.match(
            r"\D*?(\d+)",
            drv.find_element(By.XPATH,
                             '//span[@class = "questionsMainLk__main-nums-big"]/following-sibling::span').text).group(1)
    )
    iter_c = questions_count
    while iter_c > 0:
        sleep(0.5)
        select_answer(drv)
        bt_next = drv.find_element(By.XPATH, '//div[.= "Следующий"]')
        bt_next.click()
        iter_c -= 1
    sleep(0.5)
    drv.find_element(By.XPATH, '//button[.= "Завершить"]').click()
    # Send certificate to email
    drv.find_element(By.XPATH, ('//button[.= "отправить НА email" ]')).click()
    sleep(0.5)
    # close_email_notification
    drv.find_element(By.XPATH, '//div[@class = "authorizationForm__close" ]').click()
    # Quit to main page
    drv.find_element(By.XPATH, '//a[contains(@class, "headerLk__btn-lk")]').click()
    drv.quit()
    return 0


def init_Chrome():
    """
    Функция создаёт экземпляр webdriver с заданными параметрами.
    Все парамеры задаются локально непосредственно в функции.
    :return: webdriver.Chrome instance
    """
    # Варианты агентов можно посмотреть здесь https://github.com/fake-useragent/fake-useragent
    agents = ["ie", "msie", "chrome", "google", 'google chrome', "firefox", 'ff', "safari"]
    service = Service(executable_path="WebDrivers/chromedriver.exe")
    useragent = UserAgent()
    drv_options = webdriver.ChromeOptions()
    drv_options.add_argument(f"user-agent={useragent.random}")
    drv_options.add_argument("--disable-blink-features=AutomationControlled")
    # drv_options.add_argument("--headless")
    # drv_options.headless = True
    d = webdriver.Chrome(service=service, options=drv_options)
    return d


def init_firefox():
   pass

# Function deprecated
# def get_users(path: str) -> list:
#     '''Функция принимает путь к файлу и возращает список словарей в формате имя-пол-возраст-email'''
#     user_list = []
#     # Считываем данные из файла при помощи библиотеки Pandas
#     excel_data = pd.read_excel(path)
#     # Конвертируем данные в CSV
#     users_raw = excel_data.to_csv().split(sep="\r\n")
#     headers = excel_data.columns.tolist()
#     iter_count = 0
#     # В цикле собираем список в нужном формате
#     for row in users_raw:
#         if check_in(headers, row):
#             continue
#         row = row.split(sep=',')
#         iter_count = iter_count + 1
#         try:
#             # print([{headers[0]:row[1], headers[1]:row[2], headers[2]:row[3],headers[3]:row[4]}])
#             user_list.append({headers[0]: row[1], headers[1]: row[2], headers[2]: row[3], headers[3]: row[4]})
#         except IndexError as error:
#             print(f"ERROR in {iter_count} iteration.\nError description: {error} : {row}")
#             continue
#     return user_list




if __name__ == "__main__":
    pass
