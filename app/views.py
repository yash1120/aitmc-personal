from io import BytesIO

from matplotlib.pyplot import title
import base64
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from matplotlib.backend_bases import RendererBase
from .models import Photos, Post, User
from . import db

views = Blueprint("views", __name__)


def render_picture(data):

    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@views.route("/",methods=["GET","POST"])
@views.route("/home")
def home():
    if request.method=="POST":
        update_bio=request.form.get("update_bio")
        id=User.query.filter_by(id='1').first()
        id.bio = update_bio
        db.session.add(id)
        db.session.commit()

    id=User.query.filter_by(id='1').first()
    return render_template("index.html", user=current_user,id=id)


@views.route("/blogs", methods=['GET', 'POST'])
def blogs():
    posts = Post.query.all()
    return render_template('blogs.html',user=current_user, posts=posts
                           )


@views.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == "POST":
        pass
    return render_template("about.html", user=current_user)



@views.route('/contact')
def contact():
    return render_template("contact.html", user=current_user)


@views.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if request.method == "POST":
        image = request.files["photo"]
        data = image.read()
        render_file = render_picture(data)
        caption = request.form.get("captions")
        if not image:
            flash('Post cannot be empty', category='error')

        else:
            upload = Photos(image=data, rendered_image=render_file,caption =caption)
            db.session.add(upload)
            db.session.commit()
    images = Photos.query.all()
    return render_template('gallery.html', user=current_user, images=images)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('myTextarea')
        summary = request.form.get('summary')
        image = request.files["file"]
        data = image.read()
        render_file = render_picture(data)
        if not text or not title:
            flash('Post cannot be empty', category='error')

        else:
            upload = Post(title=title, text=text,summary=summary,
                          image=data, rendered_image=render_file, author=current_user.id)
            db.session.add(upload)
            db.session.commit()
        return redirect(url_for('views.blogs', user=current_user))

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.blogs', user=current_user))

@views.route("/posts/<post_id>")
@login_required
def update_post(post_id):
    post=Post.query.filter_by(id=post_id).first()
    if not post:
        flash('No post avilable', category='error')
        return redirect(url_for('views.blogs', user=current_user))
    return render_template("post_view.html", user=current_user, post=post)


@views.route("/update-post/<post_id>",methods=["GET","POST"])
@login_required
def posts(post_id):
    if request.method=="POST":
        update_title = request.form.get('update_title')
        update_text = request.form.get('update_myTextarea')
        update_summary = request.form.get('update_summary')
        image = request.files["file"]
        data = image.read()
        render_file = render_picture(data)
        post = Post.query.filter_by(id=post_id).first()
        post.title = update_title
        post.text = update_text
        post.summary = update_summary
        if image:
            post.image = data
            post.rendered_image = render_file
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('views.blogs', user=current_user))
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        flash('No post avilable', category='error')
        return redirect(url_for('views.blogs', user=current_user))
    return render_template("update_post.html", user=current_user, post=post)


