
# Учебный проект hw05_final
Стандартный блог.
## Содержание и возможности:
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

## License

Студентам Яндекс Практикума копировать запрещено совсем и категорически! А учиться кто будет? ;)
