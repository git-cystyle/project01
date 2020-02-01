from flask import Flask, render_template
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

app = Flask(__name__)
app.config.from_object(DevConfig)

db: SQLAlchemy = SQLAlchemy(app)


# Class Definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User '{}'>".format(self.username)

post_tags_tbl = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tags_tbl, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.String(255))
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    db.title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)


def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(post_tags_tbl.c.post_id).label('total')
    ).join(
        post_tags_tbl
    ).group_by(Tag).order_by(text('total DESC')).limit(5).all()

    return recent, top_tags


@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent, top_tags=top_tags)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template('post.html', post=post, tags=tags, comments=comments, recent=recent, top_tags=top_tags)

if __name__ == "__main__":
    app.run()
