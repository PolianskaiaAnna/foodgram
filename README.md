Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

# Проект FOODGRAM
## Описание
Foodgram - сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. 
Зарегистрированным пользователям также будет доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка
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

## Импорт данных из .csv файла
Для импорта данных из CSV файла, которые находятся в папке data/ingredients.csv, выполнить команду:

*python manage.py importcsv*

## Регистрация пользователей
Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email, username, first_name, last_name, password на эндпоинт /api/users/.
После этого email и password пользователь отправляет на эндроинт api/auth/token/login/, в ответ получает токен. 
При желании пользователь может установить и удалить аватар запросом на эндпоинт /api/users/me/avatar/, а также изменить пароль запросом на эндпоинт /api/users/set_password/.

## Использование
API доступно по адресу /api/

## Доступные эндпоинты

*/api/recipes/ - рецепты.* 
GET-запрос доступен всем пользователям. Доступна фильтрация по избранному, автору, списку покупок и тегам.
POST-запрос доступен только авторизированным пользователям.


*/api/recipes/{id}/get-link/ - получение короткой ссылки на рецепт.*


*/api/recipes/download_shopping_cart/ - скачать файл со списком покупок* 
TXT-файл, доступно только авторизованным пользователям.


*/api/recipes/{id}/shopping_cart/ - Добавить рецепт в список покупок/Удалить из списка покупок*
Доступно только авторизованным пользователям.


*/api/recipes/{id}/favorite/ - Добавить рецепт в избранное/Удалить из избранного*
Доступно только авторизованным пользователям.


*/api/users/subscriptions/ - Мои подписки*
Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.


*/api/users/{id}/subscribe/ - Подписаться/отписаться от пользователя*


*/api/tags/ - Список тегов*


*/api/ingredients/ - Список ингредиентов*

## Примеры запросов

GET-запрос на эндпоинт: /api/recipes/ возвращает список рецептов.
Ответ: {
  "count": 123,
  "next": "/api/recipes/?page=4",
  "previous": "/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}

GET-запрос на эндпоинт: /api/users/ возвращает список пользователей
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": false,
      "avatar": "http://foodgram.example.org/media/users/image.png"
    }
  ]
}





