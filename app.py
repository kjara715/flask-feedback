"""Example flask app that stores passwords hashed with Bcrypt. Yay!"""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
# import bcrypt
# from flask_bcrypt import Bcrypt
# from flask.ext.bcrypt import Bcrypt
from models import connect_db, db, User, Feedback
from forms import SignUp, Login, AddFeedback




app = Flask(__name__)
# bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc12345"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    """Redirects user to the register route"""
    return redirect('/register')

@app.route("/register", methods=["GET", "POST"])
def register_user():

    form = SignUp()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        # on successful login, redirect to secret page
        return redirect(f"/users/{user.username}")

     
    return render_template("sign_up.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_user():

    form=Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            # on successful login, redirect to secret page
            return redirect(f"/users/{user.username}")

        else: 
            form.username.errors=["Bad username/password"]
        
    return render_template("login.html", form=form)

@app.route("/secret")
def secret_page():
    
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    return render_template("secret.html")

@app.route("/logout")
def logout_user():

    """Logs user out and redirects to the home page"""


    session.pop("username")
    return redirect("/")


@app.route("/users/<username>")
def user_info(username):
    """Displays user information along with details about any feedback given"""

    if "username" not in session:
        flash("You must be logged in to view user details")
        return redirect('/')

    if session["username"] != username:
        flash("You may only see your own user details")
        return redirect('/register')

    user=User.query.get(username)
    return render_template("user_details.html", user=user)

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):

    if username !=session["username"]:
        flash("You do not have permission to visit the add feedback page for another user")
        return redirect ('/register')

    user=User.query.get(username)
    form = AddFeedback()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username=user.username

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        session["username"] = user.username

        # on successful login, redirect to secret page
        return redirect(f"/users/{user.username}")

    
    return render_template("add_feedback_form.html", user=user, form=form)  

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
        """Deletes user from the db"""
        if username !=session["username"]:
            flash("You do not have permission to delete this user!")
            return redirect ('/register')
        
        user=User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()

        # session.pop("username")
        flash("Your account has been deleted")
        return redirect("/")

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Shows user form to update the feedback"""
    username=session["username"]
    user=User.query.get(username)
    feedback=Feedback.query.get_or_404(feedback_id)
    form=AddFeedback(obj=feedback) #use the same form to make edits

    #check to make sure this feedback belongs to the user trying to access the form
    if feedback not in user.feedback:
        flash("You do not have permission to edit this feedback")
        return redirect('/')

    if form.validate_on_submit():
        feedback.title=form.title.data
        feedback.content=form.content.data
        db.session.commit()
        flash("Your feedback has been updated")
        return redirect(f"/users/{username}")

    
    return render_template("edit_feedback.html", feedback=feedback, form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Deletes the feedback from the user"""
    username=session["username"]
    user=User.query.get(username)
    feedback=Feedback.query.get_or_404(feedback_id)

    if feedback not in user.feedback:
        flash("You do not have permission to delete this feedback")
        return redirect('/')

    db.session.delete(feedback)
    db.session.commit()
    flash("Your feedback was deleted")

    return redirect(f"/users/{username}")


     
