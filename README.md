# Проект hw05_final
_**Основной стэк**_:  
![Python](https://img.shields.io/badge/python-3.7-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-2.19-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![SQLite3](https://img.shields.io/badge/SQLite-3-%23316192.svg?style=for-the-badge&logo=SQLite3&logoColor=white) 

**Проект был выполнен в учебных целях, чтобы получить навыки работы с
библиотекой Django.**

## Содержание и возможности/Content and Features:

* Создание постов с картинками. 
* Комментирование постов.
* Подписки на авторов.
* Объединение пользователей в группы.
* Панель управления для админа.

## Установка/Installation

Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/Yohimbe227/hw05_final.git
```
```bash
cd goodorbad/
```
Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
source env/bin/activate
```
Обновить pip:
```bash
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
Выполнить миграции:
```bash
python manage.py migrate
```
Запустить админку:
```bash
python manage.py runserver
```

## Лицензия/License

Студентам Яндекс Практикума копировать запрещено совсем и категорически! А учиться кто будет? ;)
