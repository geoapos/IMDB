from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from ImdbApp.models import User, Movie
from flask_login import current_user
from datetime import datetime

current_year = datetime.now().year



def maxImageSize(max_size=4):
   max_bytes = max_size * 1024 * 1024
   def _check_file_size(form, field):
      if len(field.data.read()) > max_bytes:
         raise ValidationError(f'Το μέγεθος της εικόνας δε μπορεί να υπεβαίνει τα {max_size} MB')

   return _check_file_size


def validate_email(form, email):
   user = User.query.filter_by(email=email.data).first()
   if user:
      raise ValidationError('Αυτό το email υπάρχει ήδη!')


class SignupForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email"), validate_email])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])
    
    password2 = StringField(label="Επιβεβαίωση password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες"),
                                       EqualTo('password', message='Τα δύο πεδία password πρέπει να είναι τα ίδια')])
    
    submit = SubmitField('Εγγραφή')


    def validate_username(self, username):
      user = User.query.filter_by(username=username.data).first()
      if user:
         raise ValidationError('Αυτό το username υπάρχει ήδη!')




class LoginForm(FlaskForm):
 
    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό.")])
    
    remember_me = BooleanField(label="Remember me")

    submit = SubmitField('Είσοδος')



class NewMovieForm(FlaskForm):
    title = StringField(label="Τίτλος Ταινίας",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=50, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    plot = TextAreaField(label="Υπόθεση της Ταινίας",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Length(min=5, message="Η υπόθεσητης τανίας πρέπει να έχει τουλάχιστον 5 χαρακτήρες")])
    
    image = FileField('Εικόνα Ταινίας', validators=[Optional(strip_whitespace=True),
                                                           FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                            'Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                                           maxImageSize(max_size=4)])
                                                           
    release_year = IntegerField(label="Έτος πρώτης προβολής ταινίας",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       NumberRange(min=1888, max=current_year, message=f"Το έτος πρώτης προβολής πρέπει να ειναι μετάξυ 1888 και {current_year}!")])

    rating = IntegerField(label="Βαθμολογία Ταινίας",
                           validators=[DataRequired(message="Αυτό το πεδίο πρέπει να ειναι ακέραιος αριθμός μεταξυ του 1 και 100 και δε μπορεί να είναι κενό."), 
                                       NumberRange(min=1, max=100, message="Η βαθμολογία πρέπει να ειναι μετάξυ 1 και 100!")])

    submit = SubmitField('Αποστολή')





class AccountUpdateForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    profile_image = FileField('Εικόνα Προφίλ', validators=[Optional(strip_whitespace=True),
                                                           FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                            'Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                                           maxImageSize(max_size=2)])
   
    submit = SubmitField('Αποστολή')


    def validate_username(self, username):
      if username.data != current_user.username:
         user = User.query.filter_by(username=username.data).first()
         if user:
            raise ValidationError('Αυτό το username υπάρχει ήδη!')

    def validate_email(self, email):
      if email.data != current_user.email:
         user = User.query.filter_by(email=email.data).first()
         if user:
            raise ValidationError('Αυτό το email υπάρχει ήδη!')
