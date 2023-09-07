from starlette_wtf import StarletteForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from queries import get_user_by_name, get_user_by_email
from db import get_db


class LoginForm(StarletteForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(StarletteForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    async def validate_username(self, username):
        db = await get_db()
        user = await get_user_by_name(username, db)
        if user is not None:
            raise ValidationError('Please use a different username.')

    async def validate_email(self, email):
        db = await get_db()
        user = await get_user_by_email(email, db)
        if user is not None:
            raise ValidationError('Please use a different email address.')
