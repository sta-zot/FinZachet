############################ Import libs#################################################
from Test_func import *
from user_data import User_data

##############################################################################################

URL = "http://Finzachet.ru"

if __name__ == '__main__':
    user_data = User_data('data/fin.xlsx')
    print(user_data.get_data())
    # browser = init_Firefox()
    # start_test(
    #     {"name": "Ингутянов Кылым", "age": 21, "email": "ingutqilim@bk.ru", "gender": "м", "pass": "Ingushkav69"},
    #     init_Chrome(), url=URL
    # )
