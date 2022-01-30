from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import LoginManager

app = Flask(__name__)

app.config["SECRET_KEY"] = '\x84\x19p\x02\x86\xcb\xf5V!\xa5?\x86\x80.\xce\xd3\x0cx\x828\x90(\xd9'
app.config['WTF_CSRF_SECRET_KEY'] = '\xb0\xcbx\xd3f\x7f\x11%\xf7`\x8e\xe4jU\x9f|\xe0\x0cRR\x04\x88wi'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ImdbApp_database.db"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://geoapos:12345@localhost/ImdbApp_database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "login"

login_manager.login_message_category = "warning"

login_manager.login_message = "Παρακαλούμε κάντε login για να μπορέσετε να δείτε αυτή τη σελίδα."





from ImdbApp import routes, models
