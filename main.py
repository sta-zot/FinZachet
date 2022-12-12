############################ Import libs#################################################
from Test_func import *
##############################################################################################

URL = "http://Finzachet.ru"








if __name__ == '__main__':
    # browser = init_Firefox()
    start_test(
        {"name": "Ингутянов Кылым", "age": 21, "email": "ingutqilim@bk.ru", "gender": "м", "pass": "Ingushkav69"},
        init_Chrome(), url=URL
    )
