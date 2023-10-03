from dependencies.db import get_db
from queries import get_user_by_email, get_user_by_name
from starlette_wtf import StarletteForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)


class LoginForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    async def validate_username(self, username):
        db = await get_db()
        user = await get_user_by_name(username, db)
        if user is not None:
            raise ValidationError("Please use a different username.")

    async def validate_email(self, email):
        db = await get_db()
        user = await get_user_by_email(email, db)
        if user is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")
