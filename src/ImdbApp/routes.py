from datetime import datetime
from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash, abort)

from ImdbApp.forms import SignupForm, LoginForm, NewMovieForm, AccountUpdateForm

from ImdbApp import app, db, bcrypt

from ImdbApp.models import User, Movie

from flask_login import login_user, current_user, logout_user, login_required

import secrets, os

from PIL import Image



@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


@app.errorhandler(415)
def unsupported_media_type(e):
    # note that we set the 415 status explicitly
    return render_template('errors/415.html'), 415




# To size είναι ένα tuple της μορφής (640, 480)
def image_save(image, where, size):
    random_filename = secrets.token_hex(12)
    file_name, file_extension = os.path.splitext(image.filename)
    image_filename = random_filename + file_extension

    image_path = os.path.join(app.root_path, 'static/images', where, image_filename)

    img = Image.open(image)

    img.thumbnail(size)

    img.save(image_path)

    return image_filename



@app.route("/index/")
@app.route("/")
def root():
    page = request.args.get("page", 1, type=int)
    movies = Movie.query.order_by(Movie.date_created.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", movies=movies)



@app.route("/movies_by_author/<int:author_id>")
def movies_by_author(author_id):

    user = User.query.get_or_404(author_id)

    page = request.args.get("page", 1, type=int)
    movies = Movie.query.filter_by(author=user).order_by(Movie.date_created.desc()).paginate(per_page=5, page=page)

    return render_template("movies_by_author.html", movies=movies, author=user)



@app.route("/signup/", methods=["GET", "POST"])
def signup():

    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data

        encrypted_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=encrypted_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Ο λογαριασμός για τον χρήστη <b>{username}</b> δημιουργήθηκε με επιτυχία", "success")

        return redirect(url_for('login'))
    

    return render_template("signup.html", form=form)




@app.route("/login/", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("root"))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            flash(f"Η είσοδος του χρήστη με email: {email} στη σελίδα μας έγινε με επιτυχία.", "success")
            login_user(user, remember=form.remember_me.data)

            next_link = request.args.get("next")

            return redirect(next_link) if next_link else redirect(url_for("root"))
        else:
            flash("Η είσοδος του χρήστη ήταν ανεπιτυχής, παρακαλούμε δοκιμάστε ξανά με τα σωστά email/password.", "warning")

    return render_template("login.html", form=form)




@app.route("/logout/")
def logout():
    logout_user()
    flash("Έγινε αποσύνδεση του χρήστη.", "success")
    return redirect(url_for("root"))




@app.route("/new_movie/", methods=["GET", "POST"])
@login_required
def new_movie():
    form = NewMovieForm()

    if request.method == 'POST' and form.validate_on_submit():
        movie_title = form.movie_title.data
        movie_body = form.movie_body.data
        release_year = form.release_year.data
        rating = form.rating.data


        if form.movie_image.data:
            try:
                image_file = image_save(form.movie_image.data, 'movies_images', (640, 360))
            except:
                abort(415)

            movie = Movie(movie_title=movie_title,
                              movie_body=movie_body,
                              author=current_user,
                              movie_image=image_file,
                              release_year=release_year,
                              rating=rating)
        else:
            movie = Movie(movie_title=movie_title, movie_body=movie_body, author=current_user, release_year=release_year, rating=rating)

        db.session.add(movie)
        db.session.commit()

        flash(f"Το άρθρο με τίτλο {movie.movie_title} δημιουργήθηκε με επιτυχία", "success")

        return redirect(url_for("root"))

    return render_template("new_movie.html", form=form, page_title="Εισαγωγή Νέας Ταινίας", current_year=datetime.now().year)




@app.route("/full_movie/<int:movie_id>", methods=["GET"])
def full_movie(movie_id):

    movie = Movie.query.get_or_404(movie_id)

    return render_template("full_movie.html", movie=movie)



@app.route("/delete_movie/<int:movie_id>", methods=["GET", "POST"])
@login_required
def delete_movie(movie_id):

    movie = Movie.query.filter_by(id=movie_id, author=current_user).first_or_404()

    if movie:

        db.session.delete(movie)
        db.session.commit()

        flash("Το άρθρο διεγράφη με επιτυχία.", "success")

        return redirect(url_for("root"))

    flash("Το άρθρο δε βρέθηκε.", "warning")

    return redirect(url_for("root"))




@app.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm(username=current_user.username, email=current_user.email)
 
    
    if request.method == 'POST' and form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data

        # image_save(image, where, size)

        if form.profile_image.data:

            try:
                image_file = image_save(form.profile_image.data, 'profiles_images', (150, 150))
            except:
                abort(415)

            current_user.profile_image = image_file

        db.session.commit()

        flash(f"Ο λογαριασμός του χρήστη <b>{current_user.username}</b> ενημερώθηκε με επιτυχία", "success")

        return redirect(url_for('root'))


    return render_template("account_update.html", form=form)



@app.route("/edit_movie/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):

    movie = Movie.query.filter_by(id=movie_id, author=current_user).first_or_404()

    form = NewMovieForm(movie_title=movie.movie_title, movie_body=movie.movie_body)

    if request.method == 'POST' and form.validate_on_submit():
        movie.movie_title = form.movie_title.data
        movie.movie_body = form.movie_body.data


        if form.movie_image.data:
            try:
                image_file = image_save(form.movie_image.data, 'movies_images', (640, 360))
            except:
                abort(415)

            movie.movie_image = image_file


        db.session.commit()

        flash(f"Το άρθρο με τίτλο <b>{movie.movie_title}</b> ενημερώθηκε με επιτυχία.", "success")

        return redirect(url_for('root'))

    return render_template("new_movie.html", form=form, page_title="Επεξεργασία Ταινίας")
