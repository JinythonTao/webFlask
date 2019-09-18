import os, random, requests
import faker
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_paginate import Pagination, get_page_parameter
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user
from app.models import User, Post
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm


# 请求之前
@app.before_request
def before_request():
    if current_user.is_authenticated:
        # 去掉now()函数默认的毫秒级别，时间精确到秒
        timeNow = str(datetime.now()).split(".")[0]
        timeFormat = datetime.strptime(timeNow, "%Y-%m-%d %H:%M:%S")
        current_user.last_seen = timeFormat
        db.session.commit()


# 首页视图函数
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('动态发布成功！')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    # 下一页
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    # 前一页
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


# 登录视图函数
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误，请重试~')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# 注册视图函数
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜您！您的账号{}已成功注册，快来登录体验一下吧！'.format(form.username.data))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 退出视图函数
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 用户编辑
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # 新增用户头像
        avatar = request.files["avatar"]
        fileName = avatar.filename
        # 上传后存储位置和允许上传的图片格式
        UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
        flag = '.' in fileName and fileName.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('上传文件类型错误, 仅支持jpg, png, gif 格式图片')
            return redirect(url_for('edit_profile'))
        avatar.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.username, fileName))
        current_user.avatar = '/static/images/avatar/{}_{}'.format(current_user.username, fileName)
        db.session.commit()
        flash("用户资料修改成功!")
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        current_user.location = form.location.data
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='资料编辑',
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 {} 未找到.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('不能关注自己哟!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('你正在关注： {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 {} 未找到.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('不能取消关注自己!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('你已经取消关注： {}.'.format(username))
    return redirect(url_for('user', username=username))


# 发现视图
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    # 下一页
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    # 前一页
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title='发现', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 删除动态
@app.route('/posts/delete/<int:post_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(post_id):
    movie = Post().query.get_or_404(post_id)  # 获取动态记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('动态消息已删除成功!')
    return redirect(url_for('user', username=current_user.username))  # 重定向回个人中心


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('请查看邮箱内容, 并依据提示信息进行密码修改!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='密码重置', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('恭喜您, 密码重置成功!')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# 游戏视图函数
@app.route('/game')
def game():
    heroList = os.listdir(app.config["GAME_FOLDER"])
    random.shuffle(heroList)
    gameImageList = []
    for image in heroList:
        gameImageList.append('images/game/' + image)
    return render_template("game.html", imageList=gameImageList)


# 伪数据生成器
f = faker.Faker(locale='zh_CN')


# 电影视图函数
@app.route('/movie/<tag>')
def movie(tag):
    # 电影数据
    tagList = ["热门", "最新", "豆瓣高分", "冷门佳片", "华语", "欧美", "韩国", "日本"]
    movieType = [" 剧情 / 喜剧", "剧情 / 科幻", "剧情 / 悬疑", "剧情 / 历史 / 战争", "动作 / 科幻 / 冒险"]
    dateList = [f.date_between("-5y", "today") for i in range(50)]
    addressList = [f.country() for i in range(20)]
    countList = [84, 62, 108, 79, 124, 110, 89, 105]
    # 访问豆瓣,获取影片信息
    url = "https://movie.douban.com/j/search_subjects?"
    param = "type=movie&tag={tag}&page_limit={count}&page_start=0".format(tag=tag, count=countList[tagList.index(tag)])
    movieList = requests.get(url + param).json().get("subjects")
    movies = []
    # 封装电影数据
    for movie in movieList:
        # 豆瓣图片有限制,利用图片缓存异步加载的方式解决
        imageUrl = "https://images.weserv.nl/?url=" + movie["cover"].split("//")[1]
        movies.append(
            {"电影名称": movie["title"], "电影图片": imageUrl, "电影详情": movie["url"],
             "电影评分": movie["rate"], "电影类型": random.choice(movieType),
             "制片地区/国家": tag if tag == "韩国" or tag == "日本" else random.choice(addressList),
             "是否新片": "是" if movie["is_new"] else "否", "上映时间": random.choice(dateList)})
    
    PER_PAGE = 20  # 每页显示数量
    total = len(movies)  # 数据总数
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码, 默认为1
    start = (page - 1) * PER_PAGE  # 每页开始位置
    end = start + PER_PAGE  # 每页结束位置
    pagination = Pagination(bs_version=3, per_page=PER_PAGE, page=page, total=total)
    movie_per_page = movies[start: end]
    return render_template("movie.html", tagList=tagList, movies=movie_per_page, pagination=pagination)
