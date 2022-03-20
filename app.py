import os
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy  # ORM
from flask_bootstrap import Bootstrap   #Bootstrap
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

# WebアプリとDB（sqlite3）の連携
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)   #ユーザーのログイン状態を管理するため秘密鍵を定義
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

#login manager をFlaskアプリと紐付け
login_manager = LoginManager()
login_manager.init_app(app)
#アプリケーション実行中のセッションからユーザー情報を読み取れるようにlogin_managerのuser_loaderが必須
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create db table column
# db.Column()メソッドの第一引数にはカラムの型、第二引数以降にはオプションを指定します
class BlogArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now(pytz.timezone('Asia/Tokyo')))
#User Table
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(25))


@app.route('/', methods=['GET'])
@login_required
def blog():
    if request.method == 'GET':
        # DBに登録されたデータをすべて取得する
        blogarticles = BlogArticle.query.all()
        return render_template('index.html', blogarticles=blogarticles)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')
        # BlogArticleのインスタンスを作成
        blogarticle = BlogArticle(title=title, body=body)
        db.session.add(blogarticle)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    # 引数idに一致するデータを取得する
    blogarticle = BlogArticle.query.get(id)
    if request.method == "GET":
        return render_template('update.html', blogarticle=blogarticle)
    else:
        # 上でインスタンス化したblogarticleのプロパティを更新する
        blogarticle.title = request.form.get('title')
        blogarticle.body = request.form.get('body')
        # 更新する場合は、add()は不要でcommit()だけでよい
        db.session.commit()
        return redirect('/')

@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    # 引数idに一致するデータを取得する
    blogarticle = BlogArticle.query.get(id)
    db.session.delete(blogarticle)
    db.session.commit()
    return redirect('/')

#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Userのインスタンスを作成
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Userテーブルからusernameに一致するユーザを取得
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

#Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')