# YaMDb

Проект YaMDb предоставляет сервис по агрегации отзывов пользователей на различные произведения с возможность совместного обсуждения для зарегистрированных пользователей. 
***
# Особенности проекта
- Администратор может добавлять произведения, категории и жанры.
- Пользователи сервиса могут оставлять текстовые отзывы.
- Пользователи могут ставить оценки произведениям в диапазоне от 1 до 10 
- Из пользовательских оценок формируется усреднённая оценка произведения (рейтинг). На одно произведение пользователь может оставить только один отзыв.
- Пользователи могут оставлять комментарии к отзывам.
- Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.
- Для неавторизованных пользователей работа с API доступна в режиме чтения.
- Реализованы пользовательские роли и права доступа для них.
- Возможна самостоятельная регистрация новых пользователей.
- Доступна возможность импортировать демо-данные из csv-файлов проекта.
***
## Пользовательские роли и права доступа:
-   **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
-   **Аутентифицированный пользователь (**`user`**)** — может читать всё, как и **Аноним**, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. 
-   **Модератор (**`moderator`**)** — те же права, что и у **Аутентифицированного пользователя**, плюс право удалять и редактировать **любые** отзывы и комментарии.
-   **Администратор (**`admin`**)** — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
-   **Суперюзер Django** обладает правами администратора, пользователя с правами `admin`. 
****
 
# Технологии
- Python 3.9
- Django 3.2
- SQLite
- Simple JWT
- django_rest_framework 3.12.4
- django-filter 22.1
- pytest 6.2.4
***
## Запуск проекта:
Клонировать репозиторий
```sh
git clone <ssh ссылка>
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции 
```
python manage.py migrate
```
Выполнить загрузку демо-информации в базу данных:
```
python manage.py import_csv_data
```
Запустить локальный сервер
```
python manage.py runserver 8000
```
Перейти по адресу сервера
```
127.0.0.1:8000
```

## Примеры запросов
Основные эндпоинты API
```
http://127.0.0.1:8000/api/v1/categories/
```
```
http://127.0.0.1:8000/api/v1/genres/
```
```
http://127.0.0.1:8000/api/v1/titles/
```
пример POST запроса на http://127.0.0.1:8000/api/v1/genres/: 
```
{
    "name": "Детектив",
    "slug": "detective"
}
```
***
### Основные эндпоинты для аутентификации нового пользователя
> Для аутентификации применены JWT-токены.

  Регистрация нового пользователя:
```
http://127.0.0.1:8000/api/v1/auth/signup/
```
  Получение JWT-токена:
```
http://127.0.0.1:8000/api/v1/auth/token/
```
Токен необходимо передавать в заголовке каждого запроса, в поле Authorization. Перед самим токеном должно стоять ключевое слово Bearer и пробел.
***
### Полный список эндпойнтов, методы и параметры запросов описаны в докуметации:
```
http://127.0.0.1:8000/redoc/
```
***
## Авторы проекта:<br>
Александр Киреев - [https://github.com/kireev20000](https://github.com/kireev20000) 
- модели, view и эндпойнты для произведений, категорий, жанров; реализация импорта данных из csv файлов. 

Константин Костенко -  [https://github.com/beehead](https://github.com/beehead)
- тимлид, система регистрации и аутентификации, права доступа, работу с токеном, систему подтверждения через e-mail.

Никита Бобков - [https://github.com/makls555](https://github.com/makls555)
- разработка ресурсов отзывов и комментариев.
***
Дата разработки - март 2023
***
Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg