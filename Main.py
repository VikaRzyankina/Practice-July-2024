from fastapi import FastAPI, Response
import sqlite3 as sq
from datetime import datetime as dt
from pydantic import BaseModel
from peewee import *

class Store(BaseModel):  #Класс для обработки информации  json-файла
    Name: str
    City: str
    Street: str
    House: int
    Open_Time: str
    Close_Time: str

app = FastAPI()


@app.get("/city/", status_code= 200)   #Запрос на вывод всех городов
async def read_root():
    try:
        conn = sq.connect('City_List')
        cursor = conn.cursor()

        query = "SELECT * FROM City"
        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()
        return {"All City": data}
    except Exception:
        return Response("Bad request", status_code=400)

@app.get("/city/{city_id}/street/", status_code= 200)    #Запрос на вывод всех улиц определенного города
async def read_root(city_id):
    try:
        conn = sq.connect('City_List')
        cursor = conn.cursor()


        query = ("SELECT Street.* FROM Street INNER JOIN City ON City.[Название] = Street.[Город] and  City.id = '" + city_id + "'")
        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()
        return {"All street": data}
    except Exception:
        return Response("Bad request", status_code=400)

@app.get("/shop/", status_code= 200)   #Запрос на получение списка магазинов в зависимости от параметров фильтрации
async def root(street: str = '', city: str = '', open: int = ''):
    try:
        conn = sq.connect('City_List')
        cursor = conn.cursor()
        query = ("SELECT * FROM Store")

        #Далее идет сортировка по введенным параметрам

        if street != "":  # есть улица
            query = ("SELECT Store.* FROM Store INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица]")
            if city != "": # есть улица есть город
                query = ("SELECT Store.* FROM Store, City INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица] "
                         " AND City.id = '" + city + "' AND City.[Название] = Store.[Город]")
                if open == 1: # есть улица есть город открыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store,City INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица] "
                             "AND City.id = '" + city + "' AND City.[Название] = Store.[Город] AND  '" + str(system_time) +
                             "' < [Время закрытия] AND  '" + str(system_time) + "' > [Время открытия]")
                elif open == 0: # есть улица есть город закрыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store,City INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица] "
                            "AND City.id = '" + city + "' AND City.[Название] = Store.[Город] AND '" + str(system_time) +
                             "' > [Время закрытия] OR  '" + str(system_time) + "' < [Время открытия]")

            elif city == "": # есть улица нет города
                query = ("SELECT Store.* FROM Store INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица]")
                if open == 1: # есть улица нет города открыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица] "
                             "AND  '" + str(system_time) + "' < [Время закрытия] AND  '" + str(system_time) + "' > [Время открытия]")
                elif open == 0: # есть улица нет города закрыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store INNER JOIN Street ON Street.id = '" + street + "' AND Street.[Название] = Store.[Улица] "
                            "AND '" + str(system_time) + "' > [Время закрытия] OR  '" + str(system_time) + "' < [Время открытия]")

        elif street == "":  #  нет улицы
            if city != "":  # нет улицы но есть город
                query = ("SELECT Store.* FROM Store INNER JOIN City ON City.id = '" + city + "' AND City.[Название] = Store.[Город]")
                if open == 1:  # нет улицы но есть город открыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store INNER JOIN City ON City.id = '" + city + "' AND City.[Название] = Store.[Город] "
                             "AND  '" + str(system_time) + "' < [Время закрытия] AND  '" + str(system_time) + "' > [Время открытия]")
                if open == 0:  # нет улицы но есть город закрыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store INNER JOIN City ON City.id = '" + city + "' AND City.[Название] = Store.[Город]"
                             " AND '" + str(system_time) + "' > [Время закрытия] OR  '" + str(system_time) + "' < [Время открытия]")
            elif city == "":# нет улицы нет города
                if open == 1:   # нет улицы нет города открыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store WHERE '" + str(system_time) + "' < [Время закрытия] AND  '" + str(system_time) + "' > [Время открытия]")
                elif open == 0: # нет улицы нет города закрыто
                    system_time = dt.time(dt.now())
                    query = ("SELECT Store.* FROM Store WHERE '" + str(system_time) + "' > [Время закрытия] OR  '" + str(system_time) + "' < [Время открытия]")


        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()
        return {"All store": data}
    except Exception:
        return Response("Bad request", status_code=400)


@app.post("/shop/", status_code= 200) #Обработка запроса на запись нового магазина
async def read_root(table : Store):
    conn = sq.connect('City_List')
    cursor = conn.cursor()
    try:
        query = "INSERT INTO Store ([Название],[Город], [Улица], [Дом], [Время открытия], [Время закрытия]) VALUES (?, ?, ?, ?, ?, ?)"

        cursor.execute(query, (table.Name, table.City, table.Street,table.House, table.Open_Time, table.Close_Time,))
        conn.commit()
        cursor.execute("SELECT Store.id FROM Store WHERE Store.[Название] = '" + table.Name + "' AND Store.[Город]  = '" + table.City + "'" 
                       " AND Store.[Улица] = '" + table.Street + "' AND Store.[Дом] = " + str(table.House) +
                       " AND Store.[Время открытия] = '" + str(table.Open_Time) + "' AND Store.[Время закрытия] =   '" + str(table.Close_Time) + "'")
        data = cursor.fetchall()
        conn.commit()
        return {"Received data": data}
    except Exception:
        return Response("Bad request", status_code=400)