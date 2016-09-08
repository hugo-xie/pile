from flask import render_template
from .. import app


@app.route('/register')
def user_register():
    return render_template('user_register.html')


@app.route('/login')
def user_login():
    return render_template('user_login.html')


@app.route('/user/<token>')
def user_info(token):
    return render_template('user_info.html', token=token)


@app.route('/pile/search')
def pile_search():
    return render_template('pile_search.html')