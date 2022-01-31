from crypt import methods
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

@app.errorhandler(500)
def Internal_Server_Error(e):
    # note that we set the 500 status explicitly
    return render_template('errors/500.html'), 500



### Μέθοδος μετονομασίας και αποθήκευσης εικόνας ###
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



@app.route("/home/")
@app.route("/index/")
@app.route("/<ordering_by>")
@app.route("/")
def root(ordering_by=None):
    
    page = request.args.get("page", 1, type=int)
    
    if ordering_by=="rating":
        movies = Movie.query.order_by(Movie.rating.desc()).paginate(per_page=5, page=page)
    elif ordering_by=="release_year":
        movies = Movie.query.order_by(Movie.release_year.desc()).paginate(per_page=5, page=page)
    else:
        movies = Movie.query.order_by(Movie.date_created.desc()).paginate(per_page=5, page=page)
    
    return render_template("index.html", movies=movies, ordering_by=ordering_by)



@app.route("/movies_by_author/<int:author_id>", methods=['GET'])
def movies_by_author(author_id):

    user = User.query.get_or_404(author_id)
    page = request.args.get("page", 1, type=int)
    ordering_by=request.args.get("ordering_by", None)

    if ordering_by=="rating":
        movies = Movie.query.filter_by(author=user).order_by(Movie.rating.desc()).paginate(per_page=2, page=page)
    elif ordering_by=="release_year":
        movies = Movie.query.filter_by(author=user).order_by(Movie.release_year.desc()).paginate(per_page=2, page=page)
    else:
        movies = Movie.query.filter_by(author=user).order_by(Movie.date_created.desc()).paginate(per_page=2, page=page)

    count=len(Movie.query.filter_by(author=user).all())
    
    return render_template("movies_by_author.html", movies=movies, author=user, ordering_by=ordering_by, count_movies_by_User=count)



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
        title = form.title.data
        plot = form.plot.data
        release_year = form.release_year.data
        rating = float(int(form.rating.data)/10)

        if form.image.data:
            try:
                image_file = image_save(form.image.data, 'movies_images', (640, 360))
            except:
                abort(415)

            movie = Movie(title=title,
                              plot=plot,
                              author=current_user,
                              image=image_file,
                              release_year=release_year,
                              rating=rating)
        else:
            movie = Movie(title=title, plot=plot, author=current_user, release_year=release_year, rating=rating)
        
        db.session.add(movie)
        db.session.commit()

        flash(f"Η ταινία με τίτλο {movie.title} δημιουργήθηκε με επιτυχία", "success")

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

        flash("Η ταινία διεγράφη με επιτυχία.", "success")

        return redirect(url_for("root"))

    flash("Η ταινία δε βρέθηκε.", "warning")

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
    
    form = NewMovieForm(title=movie.title, plot=movie.plot, image=movie.image, release_year = movie.release_year, rating=int(10*movie.rating) )

    if request.method == 'POST' and form.validate_on_submit():
        movie.title = form.title.data
        movie.plot = form.plot.data
        movie.image= form.image.data
        
        movie.release_year = form.release_year.data
        movie.rating = float(int(form.rating.data)/10)


        if form.image.data:
            try:
                image_file = image_save(form.image.data, 'movies_images', (640, 360))
            except:
                abort(415)

            movie.image = image_file


        db.session.commit()

        flash(f"Η επεξεργασία της ταινίας <b>{movie.title}</b> έγινε με επιτυχία.", "success")

        return redirect(url_for('root'))

    return render_template("new_movie.html", form=form, page_title="Επεξεργασία Ταινίας")
