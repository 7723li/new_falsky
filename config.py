import os
os.environ.setdefault('FLASKY_ADMIN','li542131220@163.com')
os.environ.setdefault('FLASKY_MAIL_SENDER',os.environ.get('FLASKY_ADMIN'))
os.environ.setdefault('MAIL_PASSWORD','abc123')
basedir = os.path.abspath(os.path.dirname(__file__))

class config:
	CSRF_ENABLED = True
	SECRET_KEY = 'you-will-never-guess'
	
	#这是我们数据库文件的路径
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	#文件夹，SQLAlchemy-migrate 数据文件存储在这里。
	SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
	SQLALCHEMY_TRACK_MODIFICATIONS=True

	OPENID_PROVIDERS = [
	    { 'name': '腾讯', 'url': '@qq.com' },
	    { 'name': '网易', 'url': '@163.com' },
	    { 'name': '新浪', 'url': '@sina.com' },
	    { 'name': '21CN', 'url': '@21CN.com' },
	    { 'name': '其他', 'url': '@' }]

	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 25
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = os.environ.get('FLASKY_MAIL_SENDER')

	POSTS_PER_PAGE = 10

	WHOOSH_BASE = os.path.join(basedir, 'search.db')
	MAX_SEARCH_RESULTS = 50

config=config