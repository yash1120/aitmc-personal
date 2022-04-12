from io import BytesIO
import base64
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from matplotlib.backend_bases import RendererBase
from .models import Post, User, Comment, Like
from . import db

views = Blueprint("views", __name__)


def render_picture(data):
    
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic
@views.route("/")
@views.route("/home")
def home():
    posts = Post.query.all()
    return render_template("index.html", user=current_user, posts=posts)


@views.route("/blogs", methods=['GET', 'POST'])
def blogs():
    posts = Post.query.all()
    return render_template('blogs.html', user=current_user, posts=posts)


@views.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == "POST":
        pass
    return render_template("about.html", user=current_user)


@views.route("/team")
def team():
    return render_template("team.html", user=current_user)


@views.route('/contact')
def contact():
    return render_template("contact.html", user=current_user)


@views.route('/gallery', methods=['GET', 'POST'])
def gallery():
    return render_template('gallery.html', user=current_user)


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('myTextarea')
        image = request.files["file"]
        data = image.read()
        render_file = render_picture(data)
        if not text or not title:
            flash('Post cannot be empty', category='error')

        else:
            upload = Post(title=title, text=text,
                          image=data,rendered_image=render_file, author=current_user.id)
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
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home', user=current_user))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home', user=current_user))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home', user=current_user))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home', user=current_user))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
