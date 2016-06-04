import os
from flask import Flask, url_for
from flask.ext.admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import Markup

basedir = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(basedir, 'files')
database_path = os.path.join(basedir, 'data-dev.sqlite')

app = Flask(__name__, static_folder='files')
app.config['SECRET_KEY'] = 'my secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_path

db = SQLAlchemy(app)
admin = Admin(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    image = db.relationship('Image')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    path = db.Column(db.String, unique=True)

    def __repr__(self):
        return self.name


class UserView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.image or not model.image.path:
            return ''

        return Markup(
            '<img src="%s">' %
            url_for('static',
                    filename=form.thumbgen_filename(model.image.path))
        )

    column_formatters = {
        'image': _list_thumbnail
    }

    edit_template = 'edit_user.html'


class ImageView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup(
            '<img src="%s">' %
            url_for('static',
                    filename=form.thumbgen_filename(model.path))
        )

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for
    # the field.
    form_extra_fields = {
        'path': form.ImageUploadField(
            'Image', base_path=file_path, thumbnail_size=(100, 100, True))
    }


admin.add_view(UserView(User, db.session))
admin.add_view(ImageView(Image, db.session))


@app.route('/')
def index():
    return 'Hello World'


def build_sample_db():
    db.drop_all()
    db.create_all()

    usernames = ['oneuser', 'anotheruser']
    for u in usernames:
        user = User()
        user.username = u
        db.session.add(user)

    images = ["Buffalo", "Elephant", "Leopard", "Lion", "Rhino"]
    for name in images:
        image = Image()
        image.name = name
        image.path = name.lower() + ".jpg"
        db.session.add(image)
    db.session.commit()


if __name__ == '__main__':
    if not os.path.exists(database_path):
        build_sample_db()
    app.run(debug=True)
