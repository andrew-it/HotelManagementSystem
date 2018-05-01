import datetime
import time

import os.path
import psycopg2
import psycopg2.extras
from flask import flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, bcrypt, login_manager
from app.db import AndrewDB
from .forms import CAdmin, CReceptionistForm, CRoomForm, CUHotelForm, DBookingForm, DReceptionistForm, InfoForm, \
    LoginForm, ProfileForm, RegisterForm, ReserveRoomForm, SearchForm, UDHotelForm, UDRoomForm, URoomForm
from .models import Customer, HotelAdmin, User

dictCursor = psycopg2.extras.DictCursor


def connectToDB():
    connection = "dbname=hms user=postgres password=postgres host='0.0.0.0'"
    try:
        return psycopg2.connect(connection)
    except Exception:
        print("Can't connect to database")


def searchOp(args):
    d = ['is_bathroom', 'is_tv', 'is_wifi', 'is_bathhub', 'is_airconditioniring']
    s = []
    for key in d:
        if args[key]:
            l = 'ro.' + key + '=%(' + key + ')s'
            s.append(l)
    s = ' AND '.join(s)
    return '(' + s + ')'


def imgName(filename):
    img_name = None
    if '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']:
        img_name = str(time.time()) + '.' + filename.rsplit('.', 1)[1]
    return img_name


def reverseDate(date):
    return '-'.join(date.split('-')[::-1])


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            search = form.data
            search['destination'] = '%' + search['destination'].lower() + '%'
            search['checkin'] = reverseDate(search['checkin'])
            search['checkout'] = reverseDate(search['checkout'])
            session['search'] = search
            return redirect(url_for('searchHotel'))
        else:
            flash('The required fields are not filled')
    return render_template('index.html', form=form)


@app.route('/search-hotel', methods=['GET', 'POST'])
def searchHotel():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = InfoForm()
    hotels = None
    search = session['search']
    if request.method == 'POST':
        if current_user.is_anonymous():
            flash("You must be authorized to reserve rooms")
            return redirect(url_for('login'))
        return redirect(url_for('moreInfo', hotel_id=form.hotel_id.data))
    query = "SELECT * FROM hotel h INNER JOIN country c ON (h.city=c.city) AND (lower(h.city) LIKE %(destination)s OR lower(c.country) LIKE %(destination)s OR lower(h.name) LIKE %(destination)s) AND EXISTS(SELECT r.hotel_id FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) WHERE r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date OR %(checkin)s >= b.checkout_date)) AND r.quantity >= %(quantity)s AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s)"
    if search['is_bathroom'] or search['is_tv'] or search['is_wifi'] or search['is_bathhub'] or search[
        'is_airconditioniring']:
        options = searchOp(search)
        query = "SELECT * FROM hotel h, country c WHERE h.city = c.city AND (lower(h.city) LIKE %(destination)s OR lower(c.country) LIKE %(destination)s OR lower(h.name) LIKE %(destination)s) AND EXISTS(SELECT r.hotel_id FROM room r, room_config rc, room_option ro WHERE r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date OR %(checkin)s >= b.checkout_date)) AND r.config_id=rc.config_id AND r.option_id=ro.option_id AND r.quantity >= %(quantity)s AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s) AND " + options
    if search['price_to'] != 0:
        query += " AND (%(price_from)s <= r.cost AND %(price_to)s >= r.cost)"
    query += ")"
    cur.execute(query, search)
    g.db.commit()
    hotels = cur.fetchall()
    return render_template('search_hotel.html', form=form, hotels=hotels)


@app.route('/more-info/<int:hotel_id>', methods=['GET', 'POST'])
def moreInfo(hotel_id):
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    form = ReserveRoomForm()
    search = session['search']
    search['hotel_id'] = hotel_id
    if request.method == 'POST':
        info = form.data
        info['customer_id'] = current_user.user_id
        checkin = datetime.datetime.strptime(search['checkin'], '%Y-%m-%d').date()
        checkout = datetime.datetime.strptime(search['checkout'], '%Y-%m-%d').date()
        nights = (checkout - checkin).days
        g.db = connectToDB()
        cur = g.db.cursor(cursor_factory=dictCursor)
        cur.execute("SELECT cost FROM room WHERE room_id=%s", (form.room_id.data,))
        cost = cur.fetchone()['cost']
        info['amount'] = int(form.quantity.data) * nights * int(cost)
        cur.execute(
            "INSERT INTO transaction VALUES (DEFAULT, %(customer_id)s, %(payment_info)s, %(amount)s) RETURNING transaction_id;",
            info)
        info['transaction_id'] = cur.fetchone()['transaction_id']
        cur.execute(
            "INSERT INTO booking VALUES (%(room_id)s, %(customer_id)s, %(transaction_id)s, %(quantity)s, %(checkin)s, %(checkout)s)",
            info)
        g.db.commit()
        flash('Room was reserved')
    cur.execute("SELECT * FROM vw_hotels WHERE hotel_id=%s", (hotel_id,))
    hotel = cur.fetchone()
    # query = "SELECT * FROM room r LEFT OUTER JOIN (SELECT coalesce(SUM(b.quantity), 0) AS occupied, b.room_id FROM booking b WHERE NOT (%(checkout)s <= b.checkin_date OR %(checkin)s >= b.checkout_date) GROUP BY (room_id)) AS oc ON (r.room_id=oc.room_id) NATURAL JOIN room_config rc NATURAL JOIN room_option ro WHERE hotel_id=%(hotel_id)s AND r.quantity > occupied AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s)"
    query = "SELECT * FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) INNER JOIN room_option ro ON (r.option_id=ro.option_id) WHERE r.hotel_id=%(hotel_id)s AND r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date OR %(checkin)s >= b.checkout_date)) AND r.quantity >= %(quantity)s AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s)"
    if search['is_bathroom'] or search['is_tv'] or search['is_wifi'] or search['is_bathhub'] or search[
        'is_airconditioniring']:
        options = searchOp(search)
        query += " AND " + options
    if search['price_to'] != 0:
        query += " AND (%(price_from)s <= r.cost AND %(price_to)s >= r.cost)"
    cur.execute(query, search)
    rooms = cur.fetchall()
    cur.execute("SELECT * FROM vw_customers WHERE person_id=%s", (current_user.user_id,))
    g.db.commit()
    cust_info = cur.fetchone()
    return render_template('booking.html', form=form, search=search, hotel=hotel, rooms=rooms, cust_info=cust_info)


@login_manager.user_loader
def load_user(user_id):
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    try:
        cur.execute("SELECT * FROM sys_user WHERE user_id=%s;", (user_id,))
    except Exception as e:
        print(e)
    res = cur.fetchone()
    g.db.commit()
    if not res:
        return None
    return User(res['user_id'], res['email'], res['password'], res['role'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = LoginForm()
    if form.validate_on_submit():
        try:
            cur.execute("SELECT * FROM sys_user WHERE email=%s;",
                        (form.email.data,))
            g.db.commit()
        except Exception as e:
            print(e)
        res = cur.fetchone()
        if not res or not bcrypt.check_password_hash(res['password'], form.password.data):
            flash('Email Address or Password is invalid')
            return redirect(url_for('login'))
        user = User(res['user_id'], res['email'], res['password'], res['role'])
        if form.remember_me.data:
            login_user(user, remember=True)
        else:
            login_user(user)
        flash('Logged in successfully')
        if user.is_receptionist():
            return redirect(url_for('manageBooking'))
        if user.is_hotel_admin():
            return redirect(url_for('myHotels'))
        if user.is_admin():
            return redirect(url_for('admin'))
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    g.role = 'customer'
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.password.data == form.password_confirmation.data:
            return redirect(url_for('register'))
        try:
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING *;",
                        (form.email.data, hash_password, g.role))
        except psycopg2.IntegrityError:
            g.db.rollback()
            flash('User with this email already registered')
            return redirect(url_for('register'))
        res = cur.fetchone()
        user = User(res['user_id'], res['email'], res['password'], res['role'])
        try:
            cur.execute(
                "INSERT INTO customer (person_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s);",
                (res['user_id'], form.first_name.data, form.last_name.data, form.telephone.data))
            g.db.commit()
        except Exception as e:
            print(e)
        login_user(user)
        flash('User successfully registered')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/add-property', methods=['GET', 'POST'])
def addProperty():
    g.role = 'hotel_admin'
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.password.data == form.password_confirmation.data:
            return redirect(url_for('addProperty'))
        try:
            hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING *;",
                        (form.email.data, hash_password, g.role))
        except psycopg2.IntegrityError:
            g.db.rollback()
            flash('User with this email already registered')
            return redirect(url_for('addProperty'))
        res = cur.fetchone()
        user = User(res['user_id'], res['email'], res['password'], res['role'])
        try:
            cur.execute(
                "INSERT INTO hotel_admin (person_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s);",
                (res['user_id'], form.first_name.data, form.last_name.data, form.telephone.data))
            g.db.commit()
        except Exception as e:
            print(e)
        login_user(user)
        flash('User successfully registered')
        return redirect(url_for('myHotels'))
    return render_template('property.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = ProfileForm()
    user = current_user
    user_info = None
    if form.validate_on_submit():
        if user.is_customer():
            try:
                cur.execute(
                    "UPDATE customer SET (first_name, last_name, phone_number, payment_info)=(%s, %s, %s, %s) WHERE person_id=%s;",
                    (form.first_name.data, form.last_name.data, form.telephone.data, form.credit_card.data,
                     user.user_id))
                g.db.commit()
            except Exception as e:
                print(e)
            return redirect(url_for('index'))
        elif user.is_hotel_admin():
            try:
                cur.execute(
                    "UPDATE hotel_admin SET (first_name, last_name, phone_number)=(%s, %s, %s) WHERE person_id=%s;",
                    (form.first_name.data, form.last_name.data, form.telephone.data, user.user_id))
                g.db.commit()
            except Exception as e:
                print(e)
            return redirect(url_for('index'))
        elif user.is_admin():
            try:
                cur.execute("UPDATE admin SET (first_name, last_name, phone_number)=(%s, %s, %s) WHERE person_id=%s;",
                            (form.first_name.data, form.last_name.data, form.telephone.data, user.user_id))
                g.db.commit()
            except Exception as e:
                print(e)
            return redirect(url_for('admin'))
    if user.is_customer():
        try:
            cur.execute("SELECT * FROM customer WHERE person_id=%s;", (user.user_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        res = cur.fetchone()
        user_info = Customer(res['first_name'],
                             res['last_name'],
                             user.email,
                             res['phone_number'],
                             res['payment_info'])
    elif user.is_hotel_admin():
        try:
            cur.execute("SELECT * FROM hotel_admin WHERE person_id=%s;", (user.user_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        res = cur.fetchone()
        user_info = HotelAdmin(res['first_name'], res['last_name'], user.email, res['phone_number'])
    elif user.is_receptionist():
        cur.execute("SELECT * FROM receptionist WHERE person_id=%s;", (user.user_id,))
        g.db.commit()
        user_info = dict(cur.fetchone())
        user_info['email'] = user.email
    elif user.is_admin():
        cur.execute("SELECT * FROM admin WHERE person_id=%s;", (user.user_id,))
        g.db.commit()
        user_info = dict(cur.fetchone())
        user_info['email'] = user.email
    return render_template('profile.html', form=form, user=user_info)


@app.route('/my-hotel', methods=['GET', 'POST'])
@login_required
def myHotels():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = UDHotelForm()
    if current_user.is_hotel_admin():
        if form.validate_on_submit():
            if form.edit.data:
                return redirect(url_for('editHotel', hotel_id=form.hotel_id.data))
            if form.delete.data:
                try:
                    cur.execute("DELETE FROM hotel WHERE hotel_id=%s RETURNING img;", (form.hotel_id.data,))
                    g.db.commit()
                except Exception as e:
                    print(e)
                img = cur.fetchone()['img']
                os.remove(os.path.abspath('app' + img))
                flash('Hotel was removed')
                return redirect(url_for('myHotels'))
            if form.manage.data:
                return redirect(url_for('manageHotel', hotel_id=form.hotel_id.data))
            if form.add_hotel.data:
                return redirect(url_for('addHotel'))
        try:
            cur.execute("SELECT * FROM hotel h, country c WHERE owner_id=%s AND h.city=c.city;",
                        (current_user.get_id(),))
            g.db.commit()
        except Exception as e:
            print(e)
        hotels = cur.fetchall()
        return render_template('my_hotel.html', form=form, hotels=hotels)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/add-hotel', methods=['GET', 'POST'])
@login_required
def addHotel():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = CUHotelForm()
    if current_user.is_hotel_admin():
        if form.validate_on_submit():
            img_name = imgName(form.img.data.filename)
            if img_name:
                try:
                    cur.execute("SELECT * FROM country WHERE country=%s AND city=%s;",
                                (form.country.data, form.city.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute("INSERT INTO country (country, city) VALUES (%s, %s);",
                                    (form.country.data, form.city.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                img_path = '/static/img/hotels/' + img_name
                try:
                    cur.execute(
                        "INSERT INTO hotel (city, address, name, stars, description, owner_id, img) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (
                            form.city.data, form.address.data, form.hotel_name.data, form.stars.data,
                            form.description.data,
                            current_user.user_id, img_path))
                    g.db.commit()
                except Exception as e:
                    print(e)
                print()
                form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                flash('Hotel was added')
                return redirect(url_for('myHotels'))
        return render_template('edit_hotel.html', form=form, hotel=None)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/edit-hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def editHotel(hotel_id):
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = CUHotelForm()
    if current_user.is_hotel_admin():
        if form.validate_on_submit():
            img_name = imgName(form.img.data.filename)
            if img_name:
                try:
                    cur.execute("SELECT * FROM country WHERE country=%s AND city=%s;",
                                (form.country.data, form.city.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute("INSERT INTO country (country, city) VALUES (%s, %s);",
                                    (form.country.data, form.city.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                try:
                    cur.execute("SELECT img FROM hotel WHERE hotel_id=%s;", (hotel_id,))
                    g.db.commit()
                except Exception as e:
                    print(e)
                old_img = cur.fetchone()['img']
                img_path = '/static/img/hotels/' + img_name
                try:
                    cur.execute(
                        "UPDATE hotel SET (city, address, name, stars, description, img)=(%s, %s, %s, %s, %s, %s) WHERE hotel_id=%s;",
                        (
                            form.city.data, form.address.data, form.hotel_name.data, form.stars.data,
                            form.description.data,
                            img_path, hotel_id))
                    g.db.commit()
                except Exception as e:
                    print(e)
                form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                os.remove(os.path.abspath('app' + old_img))
                return redirect(url_for('myHotels'))
        try:
            cur.execute("SELECT * FROM hotel h, country c WHERE hotel_id=%s AND h.city=c.city;", (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        res = cur.fetchone()
        return render_template('edit_hotel.html', form=form, hotel=res)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/manage-hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def manageHotel(hotel_id):
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    g.role = 'receptionist'
    recForm = CReceptionistForm()
    roomForm = CRoomForm()
    form = UDRoomForm()
    form2 = URoomForm()
    form3 = DReceptionistForm()
    if current_user.is_hotel_admin():
        if form.delete.data:
            try:
                cur.execute("DELETE FROM room WHERE room_id=%s;", (form.room_id.data,))
                g.db.commit()
            except Exception as e:
                print(e)
            flash('Room was removed')
            return redirect(url_for('manageHotel', hotel_id=hotel_id))
        if form2.edit.data:
            if form2.validate_on_submit():
                option_id = None
                config_id = None
                try:
                    cur.execute(
                        "SELECT option_id FROM room_option WHERE is_bathroom=%s AND is_tv=%s AND is_wifi=%s AND is_bathhub=%s AND is_airconditioniring=%s;",
                        (form2.is_bathroom.data, form2.is_tv.data, form2.is_wifi.data, form2.is_bathhub.data,
                         form2.is_aircond.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute(
                            "INSERT INTO room_option (is_bathroom, is_tv, is_wifi, is_bathhub, is_airconditioniring) VALUES (%s, %s, %s, %s, %s) RETURNING option_id;",
                            (form2.is_bathroom.data, form2.is_tv.data, form2.is_wifi.data, form2.is_bathhub.data,
                             form2.is_aircond.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                    option_id = cur.fetchone()['option_id']
                else:
                    option_id = res['option_id']
                try:
                    cur.execute(
                        "SELECT config_id FROM room_config WHERE single_bed=%s AND double_bed=%s AND sofa_bed=%s;",
                        (form2.sing_bed.data, form2.doub_bed.data, form2.sofa_bed.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute(
                            "INSERT INTO room_config (single_bed, double_bed, sofa_bed) VALUES (%s, %s, %s) RETURNING config_id;",
                            (form2.sing_bed.data, form2.doub_bed.data, form2.sofa_bed.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                    config_id = cur.fetchone()['config_id']
                else:
                    config_id = res['config_id']
                try:
                    cur.execute(
                        "UPDATE room SET (config_id, option_id, quantity, title, description, cost)=(%s, %s, %s, %s, %s, %s) WHERE room_id=%s;",
                        (config_id, option_id, form2.quantity.data, form2.title.data, form2.description.data,
                         form2.cost.data, form2.room_id.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
        if form3.del_rec.data:
            try:
                cur.execute("DELETE FROM sys_user WHERE user_id=%s;", (form3.user_id.data,))
                g.db.commit()
            except Exception as e:
                print(e)
            flash("Receptionist was removed")
        if recForm.save.data:
            if recForm.validate_on_submit():
                try:
                    hash_password = bcrypt.generate_password_hash(recForm.password.data).decode('utf-8')
                    cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING user_id;",
                                (recForm.email.data, hash_password, g.role))
                    g.db.commit()
                except psycopg2.IntegrityError:
                    g.db.rollback()
                    flash('User with this email already registered')
                    return redirect(url_for('manageHotel', hotel_id=hotel_id))
                user_id = cur.fetchone()['user_id']
                try:
                    cur.execute(
                        "INSERT INTO receptionist (person_id, hotel_id, first_name, last_name, phone_number, salary) VALUES (%s, %s, %s, %s, %s, %s);",
                        (user_id, hotel_id, recForm.first_name.data, recForm.last_name.data, recForm.telephone.data,
                         recForm.salary.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                flash("Receptionist was added")
                return redirect(url_for('manageHotel', hotel_id=hotel_id))
        if roomForm.save.data:
            if roomForm.validate_on_submit():
                option_id = None
                config_id = None
                try:
                    cur.execute(
                        "SELECT option_id FROM room_option WHERE is_bathroom=%s AND is_tv=%s AND is_wifi=%s AND is_bathhub=%s AND is_airconditioniring=%s;",
                        (
                            roomForm.is_bathroom.data, roomForm.is_tv.data, roomForm.is_wifi.data,
                            roomForm.is_bathhub.data,
                            roomForm.is_aircond.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute(
                            "INSERT INTO room_option (is_bathroom, is_tv, is_wifi, is_bathhub, is_airconditioniring) VALUES (%s, %s, %s, %s, %s) RETURNING option_id;",
                            (roomForm.is_bathroom.data, roomForm.is_tv.data, roomForm.is_wifi.data,
                             roomForm.is_bathhub.data, roomForm.is_aircond.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                    option_id = cur.fetchone()['option_id']
                else:
                    option_id = res['option_id']
                try:
                    cur.execute(
                        "SELECT config_id FROM room_config WHERE single_bed=%s AND double_bed=%s AND sofa_bed=%s;",
                        (roomForm.sing_bed.data, roomForm.doub_bed.data, roomForm.sofa_bed.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                res = cur.fetchone()
                if not res:
                    try:
                        cur.execute(
                            "INSERT INTO room_config (single_bed, double_bed, sofa_bed) VALUES (%s, %s, %s) RETURNING config_id;",
                            (roomForm.sing_bed.data, roomForm.doub_bed.data, roomForm.sofa_bed.data))
                        g.db.commit()
                    except Exception as e:
                        print(e)
                    config_id = cur.fetchone()['config_id']
                else:
                    config_id = res['config_id']
                try:
                    cur.execute(
                        "INSERT INTO room (hotel_id, config_id, option_id, quantity, title, description, cost) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (hotel_id, config_id, option_id, roomForm.quantity.data, roomForm.title.data,
                         roomForm.description.data, roomForm.cost.data))
                    g.db.commit()
                except Exception as e:
                    print(e)
                flash('Room was added')
                return redirect(url_for('manageHotel', hotel_id=hotel_id))
        try:
            cur.execute("SELECT * FROM hotel WHERE hotel_id=%s;", (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        hotel = cur.fetchone()
        try:
            cur.execute(
                "SELECT * FROM room r, room_config rc, room_option ro WHERE r.hotel_id=%s AND r.config_id=rc.config_id AND r.option_id=ro.option_id;",
                (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        rooms = cur.fetchall()
        try:
            cur.execute("SELECT * FROM sys_user u, receptionist r WHERE u.user_id=r.person_id AND r.hotel_id=%s;",
                        (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        recep = cur.fetchall()
        return render_template('manage_hotel.html', recForm=recForm, roomForm=roomForm, form=form, form2=form2,
                               form3=form3, hotel=hotel, rooms=rooms, recep=recep)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/my-booking', methods=['GET', 'POST'])
@login_required
def myBooking():
    g.db = connectToDB()
    cur = g.db.cursor(cursor_factory=dictCursor)
    form = DBookingForm()
    today = datetime.datetime.now().date()
    if form.validate_on_submit():
        try:
            cur.execute("DELETE FROM transaction WHERE transaction_id=%s", (form.transaction_id.data,))
            g.db.commit()
        except Exception as e:
            print(e)
        flash("Reservation has been cancelled")
    try:
        cur.execute(
            "SELECT *, b.quantity as booked FROM booking b INNER JOIN transaction t ON (b.transaction_id=t.transaction_id) INNER JOIN room r ON (b.room_id=r.room_id) INNER JOIN room_option ro ON (r.option_id=ro.option_id) INNER JOIN hotel h ON (h.hotel_id=r.hotel_id) INNER JOIN country c ON (h.city=c.city) WHERE b.customer_id=%s",
            (current_user.get_id(),))
        g.db.commit()
    except Exception as e:
        print(e)
    info = cur.fetchall()
    return render_template('my_booking.html', form=form, info=info, today=today)


@app.route('/manage-booking', methods=['GET', 'POST'])
def manageBooking():
    db = AndrewDB()
    if 'recep' not in session:
        session['recep'] = db.get_all_receptionists(current_user.user_id)
    if 'hotel' not in session:
        session['hotel'] = db.get_vw_hotel_by_id(session['recep']['hotel_id'])
    recep = session['recep']
    hotel = session['hotel']
    bookings = db.get_booked_rooms_by_hotel_id(recep['hotel_id'])
    return render_template('booked_rooms.html', bookings=bookings, hotel=hotel)


@app.route('/new-booking', methods=['GET', 'POST'])
@login_required
def newBooking():
    db = AndrewDB()
    recep = session['recep']
    hotel = session['hotel']
    today = datetime.datetime.now().date().strftime("%Y-%m-%d")
    rooms = db.get_rooms_by_params(recep['hotel_id'], today, today)
    return render_template('new_booking.html', rooms=rooms, hotel=hotel)


@app.route('/admin-panel', methods=['GET', 'POST'])
@login_required
def admin():
    form = CAdmin()
    db = AndrewDB()
    if request.method == 'POST' and form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = db.insert_sys_user(form.email.data, hash_password)
        if user_id is None:
            flash('User with this email already registered')
            return redirect(url_for('admin'))
        db.insert_admin(user_id, form.first_name.data, form.last_name.data, form.telephone.data)
        flash("Admin was added")
        return redirect(url_for('admin'))
    hotels = db.get_all_hotels()
    users = db.get_all_system_users()
    db_stat = db.get_db_statistics()
    admins = db.get_all_admins()
    g.db.commit()
    return render_template('admin_panel.html', hotels=hotels, users=users, db_stat=db_stat, form=form, admins=admins)
