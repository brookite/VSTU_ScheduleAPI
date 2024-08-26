# API Расписаний ВолгГТУ

Часть проекта по разбору расписаний ВолгГТУ
Проект написан с использованием Django и Django REST Framework

Инструкция для запуска API:

1. Клонируйте репозиторий

2. Перейдите в терминале в папку с репозиторием и создайте по желанию виртуальное окружение:

3. Выполните команды:

```bash
python -m pip install -r requirements.txt
python manage.py runserver
```

4. Чтобы создать аккаунт администратора используйте команду `python manage.py createsuperuser`

Базу данных можно заполнить тестовыми примерами, которые хранятся в папке `testdata`
Команда:

```bash
python manage.py load_testdata
```

Эти тестовые данные не должны быть огромными, см. [комментарий в скрипте-заполнителе](api/management/commands/load_testdata.py)

### ERD диаграмма

![ERD Диаграмма](resources/erd.png)
