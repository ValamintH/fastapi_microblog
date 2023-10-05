from queries import get_user_by_email, get_user_by_name
from starlette_wtf import StarletteForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class LoginForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def __init__(self, request, db, *args, **kwargs):
        super(RegistrationForm, self).__init__(request, *args, **kwargs)
        self.db = db

    async def async_validate_username(self, username):
        user = await get_user_by_name(username.data, self.db)
        if user is not None:
            raise ValidationError("Please use a different username.")

    async def async_validate_email(self, email):
        user = await get_user_by_email(email.data, self.db)
        if user is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(StarletteForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, request, original_username, db, *args, **kwargs):
        super(EditProfileForm, self).__init__(request, *args, **kwargs)
        self.original_username = original_username
        self.db = db

    async def async_validate_username(self, username):
        if username.data != self.original_username:
            user = await get_user_by_name(username=self.username.data, db=self.db)
            if user:
                raise ValidationError("Please use a different username.")
