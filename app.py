import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import (
    UserMixin, LoginManager, login_user,
    logout_user, current_user, login_required
)
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import SelectField, TextAreaField, StringField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_admin.form import SecureForm
from sqlalchemy.orm import load_only
from sqlalchemy import Index
from flask_caching import Cache

# ===============================================================
#  Flask App Configuration
# ===============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secret_key_for_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'test@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS', 'password')
app.config['ADMINS'] = ['e.uyo@alustudent.com']

# ===============================================================
#  Extensions Initialization
# ===============================================================
db = SQLAlchemy(app)
mail = Mail(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})   # <-- Template caching enabled

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ===============================================================
#  Models
# ===============================================================
@login_manager.user_loader
def load_user(user_id):
    return Administrator.query.get(int(user_id))


class Administrator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Article('{self.title}', '{self.category}')"


# ---- CREATE INDEXES FOR SEARCH SPEED (major boost) ----
Index('idx_article_content', Article.content)

# ===============================================================
#  Initialize Database + Default Admin
# ===============================================================
with app.app_context():
    db.create_all()
    if Administrator.query.filter_by(username='admin').first() is None:
        initial_admin = Administrator(username='admin', email='admin@agri-naija.com')
        initial_admin.set_password('supersecretpassword')
        db.session.add(initial_admin)
        db.session.commit()
        print("Initial admin created: admin / supersecretpassword (change ASAP)")

# ===============================================================
#  Master Categories
# ===============================================================
MASTER_CATEGORIES = [
    'Aquaculture',
    'Crop Farming',
    'Livestock Management',
    'Soil and Irrigation',
    'Agri-Business Finance',
    'Market Analysis'
]

# ===============================================================
#  Flask-Admin Views
# ===============================================================
class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return super().index()


class ArticleModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    form_columns = ['title', 'content', 'category', 'date_posted']
    column_searchable_list = ['title', 'content', 'category']
    column_filters = ['category', 'date_posted']

    form_overrides = {
        'category': SelectField,
        'content': TextAreaField
    }

    form_args = {
        'category': {'label': 'Category'},
        'content': {
            'label': 'Content (Supports HTML for images/videos)',
            'render_kw': {'rows': 20}
        }
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.category.choices = [(c, c) for c in MASTER_CATEGORIES]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.category.choices = [(c, c) for c in MASTER_CATEGORIES]
        return form

    def is_accessible(self):
        return current_user.is_authenticated


class AdministratorForm(SecureForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', description="Leave blank to keep existing password")


class AdminModelView(ModelView):
    form = AdministratorForm
    form_excluded_columns = ['password_hash']
    column_exclude_list = ['password_hash']

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(
    app,
    name='Agri-Naija CMS',
    template_mode='bootstrap3',
    index_view=CustomAdminIndexView(name='Home')
)
admin.add_view(ArticleModelView(Article, db.session, category="Content"))
admin.add_view(AdminModelView(Administrator, db.session, category="Security"))

# ===============================================================
#  Authentication Routes
# ===============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Administrator.query.filter_by(username=username).options(
            load_only(Administrator.id, Administrator.password_hash)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('admin/admin_login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# ===============================================================
#  Public Routes
# ===============================================================

# ---- HOME PAGE (CACHED for 60 seconds) ----
@cache.cached(timeout=60)
@app.route('/')
@app.route('/home')
def home():
    articles = (Article.query
        .options(load_only(Article.id, Article.title, Article.category, Article.date_posted))
        .order_by(Article.date_posted.desc())
        .limit(3)
        .all()
    )

    featured = articles[0] if articles else None
    latest = articles[1:] if len(articles) > 1 else []

    return render_template('index.html', featured=featured, latest=latest)


@app.route('/articles')
def article_list():
    search_query = request.args.get('search')
    category_filter = request.args.get('category')
    page = request.args.get('page', 1, type=int)

    query = Article.query.options(load_only(Article.id, Article.title, Article.category, Article.date_posted))

    if search_query:
        query = query.filter(
            Article.title.ilike(f'%{search_query}%') |
            Article.content.ilike(f'%{search_query}%') |
            Article.category.ilike(f'%{search_query}%')
        )

    if category_filter and category_filter != 'all':
        query = query.filter_by(category=category_filter)

    articles = query.order_by(Article.date_posted.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'article_list.html',
        articles=articles,
        categories=MASTER_CATEGORIES,
        current_category=category_filter,
        search_query=search_query
    )


@app.route('/article/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return redirect(url_for('contact'))

        try:
            msg = Message(
                subject=f'New Contact Form Submission from {name}',
                sender=app.config['MAIL_USERNAME'],
                recipients=app.config['ADMINS'],
                body=f"From: {name} <{email}>\n\nMessage:\n{message}"
            )
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('There was a problem sending your message.', 'danger')

    return render_template('contact.html')

# ===============================================================
#  Static File Caching (Performance)
# ===============================================================
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "public, max-age=31536000"
    return r

# ===============================================================
#  Run App
# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
