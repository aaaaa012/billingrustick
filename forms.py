from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, DateField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError , Optional, NumberRange
from models import User  # Adjust the import based on your project structure

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    class PurchaseForm(FlaskForm):
     product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
     unit = StringField('Unit', validators=[DataRequired(), Length(min=1, max=50)])
     quantity = IntegerField('Purchase Quantity', validators=[DataRequired(), NumberRange(min=1)])
     purchase_date = DateField('Purchase Date', format='%Y-%m-%d', validators=[DataRequired()])
     vendor = StringField('Vendor', validators=[DataRequired(), Length(min=1, max=100)])
     per_unit_price = FloatField('Per Unit Price', validators=[DataRequired(), NumberRange(min=0)])
     purchase_price = FloatField('Total Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
     payment_mode = StringField('Payment Mode', validators=[DataRequired(), Length(min=1, max=50)])
     submit = SubmitField('Submit')

    def validate_product_name(self, product_name):
        if product_name.data[0].isdigit():
            raise ValidationError('Product name cannot begin with a number.')

    def validate_quantity(self, quantity):
        if quantity.data <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def validate_per_unit_price(self, per_unit_price):
        if per_unit_price.data <= 0:
            raise ValidationError('Per unit price must be a positive number.')

    def validate_purchase_price(self, purchase_price):
        if purchase_price.data <= 0:
            raise ValidationError('Total purchase price must be a positive number.')

class SalesForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    unit = StringField('Unit', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    sale_date = DateField('Sale Date', format='%Y-%m-%d', validators=[DataRequired()])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    total_price = FloatField('Total Sales Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

    def validate_product_name(self, product_name):
        if product_name.data[0].isdigit():
            raise ValidationError('Product name cannot begin with a number.')

    def validate_quantity(self, quantity):
        if quantity.data <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def validate_unit_price(self, unit_price):
        if unit_price.data <= 0:
            raise ValidationError('Unit price must be a positive number.')

    def validate_total_price(self, total_price):
        if total_price.data <= 0:
            raise ValidationError('Total sales price must be a positive number.')

class StockForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    unit = StringField('Unit', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Stock')

    def validate_product_name(self, product_name):
        if product_name.data[0].isdigit():
            raise ValidationError('Product name cannot begin with a number.')

    def validate_quantity(self, quantity):
        if quantity.data < 0:
            raise ValidationError('Quantity cannot be negative.')
