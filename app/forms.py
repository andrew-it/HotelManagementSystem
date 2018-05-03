from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, HiddenField, IntegerField, PasswordField, SelectField, StringField, \
    SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo

import logging

logger = logging.getLogger(__name__)


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')


class RegisterForm(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_confirmation = PasswordField(
        'password_confirmation', validators=[
            DataRequired(), EqualTo('password', message='Passwords must match.')])
    telephone = StringField('telephone', validators=[DataRequired()])


class ProfileForm(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    email = StringField('email')
    telephone = StringField('telephone', validators=[DataRequired()])
    credit_card = StringField('credit_card')


class UDHotelForm(FlaskForm):
    hotel_id = HiddenField('hotel_id')
    edit = SubmitField('edit')
    delete = SubmitField('delete')
    add_hotel = SubmitField('add_hotel')
    manage = SubmitField('manage')


class CUHotelForm(FlaskForm):
    img = FileField('img', validators=[DataRequired()])
    hotel_name = StringField('hotel_name', validators=[DataRequired()])
    country = StringField('country', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    stars = SelectField('stars', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                        validators=[DataRequired()])


class CReceptionistForm(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    telephone = StringField('telephone', validators=[DataRequired()])
    salary = IntegerField('salary', validators=[DataRequired()])
    save = SubmitField('save')


class CRoomForm(FlaskForm):
    is_bathroom = BooleanField('is_bathroom')
    is_tv = BooleanField('is_tv')
    is_wifi = BooleanField('is_wifi')
    is_bathhub = BooleanField('is_bathhub')
    is_aircond = BooleanField('is_aircond')
    sing_bed = StringField('is_sing_bed', validators=[DataRequired()])
    doub_bed = StringField('is_doub_bed', validators=[DataRequired()])
    sofa_bed = StringField('is_sofa', validators=[DataRequired()])
    quantity = StringField('quantity', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    cost = StringField('cost', validators=[DataRequired()])
    save = SubmitField('save')


class URoomForm(FlaskForm):
    room_id = HiddenField('room_id')
    is_bathroom = BooleanField('is_bathroom')
    is_tv = BooleanField('is_tv')
    is_wifi = BooleanField('is_wifi')
    is_bathhub = BooleanField('is_bathhub')
    is_aircond = BooleanField('is_aircond')
    sing_bed = StringField('is_sing_bed', validators=[DataRequired()])
    doub_bed = StringField('is_doub_bed', validators=[DataRequired()])
    sofa_bed = StringField('is_sofa', validators=[DataRequired()])
    quantity = StringField('quantity', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    cost = StringField('cost', validators=[DataRequired()])
    edit = SubmitField('edit')


class UDRoomForm(FlaskForm):
    room_id = HiddenField('room_id')
    delete = SubmitField('delete')


class DReceptionistForm(FlaskForm):
    user_id = HiddenField('user_id')
    del_rec = SubmitField('del_rec')


class SearchForm(FlaskForm):
    destination = StringField('destination', validators=[DataRequired()])
    checkin = StringField('checkin', validators=[DataRequired()])
    checkout = StringField('checkout', validators=[DataRequired()])
    is_bathroom = BooleanField('is_bathroom')
    is_tv = BooleanField('is_tv')
    is_wifi = BooleanField('is_wifi')
    is_bathhub = BooleanField('is_bathhub')
    is_airconditioniring = BooleanField('is_aircond')
    sleeps = IntegerField('sleeps', validators=[DataRequired()])
    price_from = IntegerField('pricefrom')
    price_to = IntegerField('priceto')
    quantity = IntegerField('quantity', validators=[DataRequired()])


class InfoForm(FlaskForm):
    hotel_id = HiddenField('hotel_id')
    info = SubmitField('info')


class DBookingForm(FlaskForm):
    transaction_id = HiddenField('booking_id')
    delete = SubmitField('delete')


class ReserveRoomForm(FlaskForm):
    room_id = HiddenField('room_id')
    quantity = HiddenField('quantity')
    amount = HiddenField('amount')
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    email = StringField('email')
    payment_info = StringField('payment_method')
    checkin = StringField('checkin')
    checkout = StringField('checkout')


class CAdmin(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    telephone = StringField('telephone', validators=[DataRequired()])
