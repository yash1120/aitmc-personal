from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["password"]

        if not '@' in email:
            user = User.query.filter_by(username=email).first()

            if not user:
                return render_template("login.html", error="User doesn't exist!", user=current_user)

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('views.blogs', user=current_user))
            else:
                return render_template("login.html", error="Incorrect password!", email=email, user=current_user)

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error="User doesn't exist!", user=current_user)

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('views.blogs', user=current_user))
        else:
            return render_template("login.html", error="Incorrect password!", email=email, user=current_user)
    return render_template("login.html", user=current_user)


@auth.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
	if request.method == "GET":
		return render_template("edit_profile.html", user=current_user)
	elif request.method == "POST":
		form = request.form
		operation_type = form["type"]
		if operation_type == "change_username":
			username = form["username"]
			password = form["password"]
			user = User.query.filter_by(username=current_user.username).first()
			if check_password_hash(user.password, password):
				user = User.query.filter_by(username=current_user.username).first()
				user.username = username
				db.session.add(user)
				db.session.commit()

				return render_template("edit_profile.html",  success1 = "Successfully updated username!",user=current_user)
			else:
				return render_template("edit_profile.html",  error2 = True, error_cu = "Incorrect password!",username = username,user=current_user)

		elif operation_type == "change_password":
			old_password = form["old-password"]
			new_password = form["new-password"]
			user = User.query.filter_by(username=current_user.username).first()
			if check_password_hash(user.password, old_password):
				user.password = generate_password_hash(new_password, method='sha256')
				db.session.add(user)
				db.session.commit()

				return render_template("edit_profile.html",  success2 = "Successfully updated password!",user=current_user)
			else:
				return render_template("edit_profile.html",  error3 = True, error_cp = "Incorrect password!", new_password = new_password,user=current_user)



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home",user=current_user))
