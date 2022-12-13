"""
Modul for class User_data
"""
import pandas as pd
from datetime import date
import os


class User_data:
    __instance = None
    __file_des = ''
    __csv_path = ''
    __csv_headers = []

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        else:
            return cls.__instance

    def __init__(self, excel_path):
        if self.__csv_path == "":
            self.__csv_path = self.create_csv(excel_path)
        if self.__file_des == "":
            self.__file_des = open(self.__csv_path, 'r', encoding="utf-8")
        if self.__csv_headers:
            pass
        else:
            self.__csv_headers = [s.strip() for s in self.__file_des.readline().split(',')]


    def get_data(self) -> dict:
        """

        :return: User data dictionary
        """
        fields = [s.strip() for s in self.__file_des.readline().split(',')]
        # Нужно реализовать проверку всех полей и в случае отсутствия таковых
        user_data = dict(zip(self.__csv_headers, fields))
        return user_data

    @staticmethod
    def create_csv(path: str) -> str:
        csv_path = f'data/{date.today().strftime(r"%d.%m.%y")}.csv'
        data_frame = pd.read_excel(path)
        data_frame.to_csv(csv_path, index=False, encoding='utf-8', lineterminator='\n')
        return csv_path

    def __del__(self):
        if self.__file_des:
            self.__file_des.close()
        if os.path.isfile(self.__csv_path):
            os.remove(self.__csv_path)


if __name__ == "__main__":
    print("This module contains classes")
