cd SE-Project/PolyMetric/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
在SE-Project\PolyMetric\backend\apps\users 中
创建migrations文件夹以及__init__.py文件
在__init__.py文件中添加  default_app_config = 'apps.users.apps.UsersConfig'
python manage.py makemigrations
python manage.py migrate
python manage.py runserver