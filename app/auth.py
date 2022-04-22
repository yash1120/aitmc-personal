from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["password"]

        if not '@' in email:
            user = User.query.filter_by(username=email).first()

            if not user:
                return render_template("login.html", error = "User doesn't exist!",user=current_user)

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('views.blogs',user=current_user))
            else:
                return render_template("login.html", error = "Incorrect password!", email = email,user=current_user)

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error = "User doesn't exist!",user=current_user)

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('views.blogs',user=current_user))
        else:
            return render_template("login.html", error = "Incorrect password!", email = email)
    return render_template("login.html",user=current_user)


@auth.route('/register', methods = ["GET", "POST"])
def register():
	if request.method == "POST":
		form = request.form
		username = form["username"]
		email = form["email"]
		password = form["password"]

		if not '@' in email:
			return render_template("register.html", error = "Invalid Email!", email = email, username = username, password = password,user=current_user)

		temp1 = User.query.filter_by(username=username).first()
		if temp1:
			return render_template("register.html", error = "Username already in use!", error1 = True, email = email, password = password,user=current_user)
		

		temp2 = User.query.filter_by(email=email).first()
		if temp2:
			return render_template("register.html", error = "Email already in use!", error2 = True, username = username, password = password,user=current_user)

		user = User(username = username, email = email, password = generate_password_hash(password, method='sha256'))
		db.session.add(user)
		db.session.commit()

		login_user(user)
		return redirect(url_for('views.blogs',user=current_user))
		
	elif request.method == "GET":
		return render_template("register.html",user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home",user=current_user))
