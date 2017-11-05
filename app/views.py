from . import app, db, lm
from .forms import LoginForm, EditForm, RegisterForm, PostForm, SearchForm
from .models import User, Post
from flask import render_template, flash, redirect, session, url_for, request, g, Response
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime

from camera import VideoCamera

#user_loader 回调,用于从数据库加载用户
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    #print(current_user)#flask_login.mixins.AnonymousUserMixin object
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()

@app.route('/' , methods=['GET','POST'])
@app.route('/index' , methods=['GET','POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    user = g.user
    if g.user.is_authenticated:
        posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    else:
        posts=''        
    return render_template("index.html",
        form=form,
        title = 'Home',
        user = user ,
        posts = posts)
	

@app.route('/register', methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        nickname=form.nickname.data
        email=form.email.data
        if User.query.filter_by(email=email).first() or User.query.filter_by(nickname=nickname).first():
            flash('Email address or Nickname has been used.')
            return render_template('register.html',form=form)
        user=User(nickname=nickname,email=email)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',
        form=form, providers = app.config['OPENID_PROVIDERS'])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    # g 全局变量是一个在请求生命周期中用来存储和共享数据,登录的用户存储在这里
    # 检查 g.user 是否被设置成一个认证用户，如果是的话将会被重定向到首页
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        if User.query.filter_by(email=email).first() is None:
            flash('Not register yet.')
            return redirect(url_for('login'))
        session['remember_me']=form.remember_me.data
        user=User.query.filter_by(email=form.email.data).first()
        login_user(user, remember = session['remember_me'])
        return redirect(url_for('index'))
    return render_template('login.html',
        title = 'Sign In',
        form = form,)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname,page=1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('user',nickname=g.user.nickname))
    posts = user.posts.paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('user.html',
        user = user,
        posts = posts)    

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        if User.query.filter_by(nickname=form.nickname.data).first() is None:
            g.user.nickname = form.nickname.data
            g.user.about_me = form.about_me.data
            db.session.add(g.user)
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit'))
        else:
            g.user.about_me = form.about_me.data
            db.session.add(g.user)
            db.session.commit()
            if form.nickname.data!=g.user.nickname:
                flash('Nickname has been used.')
            g.user.about_me = form.about_me.data
            flash('Your about_me have been saved.')
            return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form,
        email=g.user.email)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

@app.route('/followers/<nickname>')
@login_required
def followers(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    followers=user.followers.all()
    return  render_template('followers.html',
        user=user,
        followers=followers,
        followers_num=len(followers))

@app.route('/followed/<nickname>')
@login_required
def followed(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    followeds=user.followed.all()
    return  render_template('followed.html',
        user=user,
        followeds=followeds,
        followed_num=len(followeds),)

@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', \
        query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS']).all()
    return render_template('search_results.html',
        query = query,
        results = results)

@app.route('/video')
@login_required
def video():
    return Response(video_gen(VideoCamera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')

def video_gen(camera):
    while True:
        frame=camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    #这是很有必要的因为这个函数是被作为异常的结果被调用
    #如果异常是被一个数据库错误触发，
    #数据库的会话会处于一个不正常的状态，
    #因此我们必须把会话<!--回滚-->到正常工作状态在渲染 500 错误页模板之前
    db.session.rollback()
    return render_template('500.html'), 500