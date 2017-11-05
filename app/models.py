from . import db
from app import app
from hashlib import md5
import sys

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy

#没有像对 users 和 posts 一样把它声明为一个模式。
#因为这是一个辅助表，
#我们使用 flask-sqlalchemy 中的低级的 APIs 来创建没有使用关联模式
Followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
	#__tablename__='user'
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    #这并不是一个实际的数据库字段
    #对于一个一对多的关系，
    #db.relationship 字段通常是定义在“一”这一边
    #一对多
    posts = db.relationship('Post', 
        backref='author', 
        lazy='dynamic')
    '''
        #多对多
    registrations = db.Table('registrations',
        db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
        db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
    )
    class Student(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)

        classes = db.relationship('Class',
            secondary=registrations,
            backref=db.backref('students', lazy='dynamic'),
            lazy='dynamic')
        def study(self,class):
            if not self.is_studying(class):
                self.classes.append(class)

        def notstudy(self,class):
            if self.is_studying(class):
                self.classes.remove(class)

        def is_studying(self,class):
            return self.classes.filter(registrations.c.class_id == class.id).count()

    class Class(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String)
    '''
    #一对一自引用
    followed = db.relationship('User',
        secondary = Followers,#secondary 指明了用于这种关系的辅助表。
        primaryjoin = (Followers.c.follower_id == id),# 表示辅助表中连接左边实体(发起关注的用户)的条件
        secondaryjoin = (Followers.c.followed_id == id),#secondaryjoin 表示辅助表中连接右边实体(被关注的用户)的条件
        backref = db.backref('followers', lazy = 'dynamic'),#backref 定义这种关系将如何从右边实体进行访问(被关注用户的粉丝们)
        lazy = 'dynamic')#dynamic 模式表示直到有特定的请求才会运行查询

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self,user):
        #被关注者的id是目标用户（非本人）的id
        return self.followed.filter(Followers.c.followed_id == user.id).count()

    def followed_posts(self):
        #一共有三部分:连接，过滤以及排序。
        return Post.query.join(Followers, (Followers.c.followed_id == Post.user_id)).\
        filter(Followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode()).hexdigest() + '?d=mm&s=' + str(size)

    #用户认证
    def is_authenticated(self):
        return True

    #用户是无效
    def is_active(self):
        return True

    #伪造的用户
    def is_anonymous(self):
        return False

	#使用数据库生成的唯一的 id
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
	#__tablename__='post'
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

if enable_search:
    whooshalchemy.whoosh_index(app, Post)