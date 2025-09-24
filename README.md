1. Клонировать
git clone https://github.com/SchekaturovAA/AI_Agregator.git;
2. Создать виртуальное окружение 
python -m venv  venv;
python .venv\Scripts\activate;
pip install -r requirements.txt;
3. Выполнить миграции
cd ai_agregator\
python manage.py makemigrations;
python manage.py migrate;
4. Создать суперпользователя
python manage.py createsuperuser;
5. Запустить сервер
python manage.py runserver 8***;