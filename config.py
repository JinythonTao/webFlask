import os

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# 数据库相关配置
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# 邮件相关配置
MAIL_SERVER = "smtp.163.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "flasktest1108@163.com"
MAIL_PASSWORD = "taojin1108"
ADMINS = ['flasktest1108@163.com']

# 分页配置&头像存储位置
POSTS_PER_PAGE = 5
UPLOAD_FOLDER = os.getcwd() + '/app/static/images/avatar/'

# 游戏图片储存位置
GAME_FOLDER = os.getcwd() + '/app/static/images/game/'

