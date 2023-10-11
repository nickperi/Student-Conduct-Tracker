from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from App.controllers import User
from App.database import db
from flask_jwt import JWT

from App.controllers.auth import (
    authenticate
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


login_manager = LoginManager()
login_manager.init_app(auth_views)

@auth_views.route('/login/<string:user_id>', methods=['GET'])
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

#Define route for Login 
@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']

        user = authenticate(firstname, lastname, password)

        if user:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('/reviews'))
        else:
            flash('Login failed. Please check your name and password.', 'danger')

    return render_template('/index.html')

# Define route for logout
@auth_views.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('/login'))

