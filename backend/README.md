## Проект FOODGRAM
#Описание
Foodgram - сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. 
Зарегистрированным пользователям также будет доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

#Установка
Клонировать репозиторий и перейти в него в командной строке:

*git clone git@github.com:PolianskaiaAnna/foodgram.git cd backend*

Cоздать и активировать виртуальное окружение:

*python -m venv venv source venv/bin/activate*

Установить зависимости из файла requirements.txt:

*python -m pip install --upgrade pip pip install -r requirements.txt*

Перейти в папку проекта:

*cd backend_foodgram*

Выполнить миграции:

*python manage.py migrate*

Запустить проект:

*python manage.py runserver*

#Импорт данных из .csv файла
Для импорта данных из CSV файла, которые находятся в папке data/ingredients.csv, выполнить команду:

*python manage.py importcsv

#Регистрация пользователей
Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email, username, first_name, last_name, password на эндпоинт /api/users/.
После этого email и password пользователь отправляет на эндроинт api/auth/token/login/, в ответ получает токен. 
При желании пользователь может установить и удалить аватар запросом на эндпоинт /api/users/me/avatar/, а также изменить пароль запросом на эндпоинт /api/users/set_password/.

#Использование
API доступно по адресу /api/
