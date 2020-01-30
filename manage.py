from flask_script import Manager, Server
from main import app, db, User, Post, Comment, Tag
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)

# db.drop_all()
db.create_all()

user = User(username='fake_name', password='test')
user.posts.append(Post('Post Title'))
user.posts.append(Post('Second Title'))
user.posts.append(Post('Third Title'))
db.session.add(user)
db.session.commit()

@manager.shell
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Post=Post,
        Comment=Comment,
        Tag=Tag
    )

if __name__ == "__main__":
    manager.run()
