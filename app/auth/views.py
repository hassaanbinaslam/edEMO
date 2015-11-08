from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, login_required, logout_user, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from ..models import User
from ..email import send_mail
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('main.home'))
        flash('Invalid username or password.', 'error')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        new_user = User(
            email=form.email.data,
            name=form.name.data,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        # Send confirmation email to user.
        token = new_user.generate_confirmation_token()
        send_mail(new_user.email, 'Confirm Your Account', 'auth/email/confirm', user=new_user, token=token)

        flash('You are now registered. Please check your inbox for confirmation email.', 'success')
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        flash('Your account has been confirmed.', 'success')
        return redirect(url_for('main.home'))
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.home'))


@auth.before_app_request
def before_request():
    if not current_user.is_anonymous and current_user.is_authenticated and not current_user.confirmed:
        if request.endpoint and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.home')
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.', 'info')
    return redirect(url_for('auth.unconfirmed'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_mail(user.email, 'Reset Your Password', 'auth/email/password_reset', user=user,
                      token=token)
            flash('An email with instructions to reset your password has been sent to you.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Provided email address is not registered.', 'error')
    return render_template('auth/password_reset_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Something went wrong and your password could not be reset!', 'error')
    return render_template('auth/password_reset.html', form=form)
