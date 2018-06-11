from app import creat_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Role, Post, Category, Comment, Follow, ApplyForBestPost
import os

if os.path.exists('.env'):
    print("Importing environment from .env")
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = creat_app(os.getenv('TJ_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Category=Category,
                Post=Post, Comment=Comment, Follow=Follow, ApplyForBestPost=ApplyForBestPost)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role, Category

    upgrade()

    Role.insert_roles()
    Category.insert_categories()


if __name__ == "__main__":
    manager.run()