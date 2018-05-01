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
    db = AndrewDB()
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
        cost = db.get_cost_by_id(form.room_id.data)
        info['amount'] = int(form.quantity.data) * nights * int(cost)
        info['transaction_id'] = db.create_transaction_get_id(info)
        db.add_booking(info)
        flash('Room was reserved')
    hotel = db.get_vw_hotel_by_id(hotel_id)
    rooms = db.search_get_rooms(search)
    cust_info = db.get_vw_customer_by_id(current_user.user_id)
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
    db = AndrewDB()
    form = LoginForm()
    if form.validate_on_submit():
        sys_user = db.get_sys_user_by_email(form.email.data)
        if not sys_user or not bcrypt.check_password_hash(sys_user['password'], form.password.data):
            flash('Email Address or Password is invalid')
            return redirect(url_for('login'))
        user = User(sys_user['user_id'], sys_user['email'], sys_user['password'], sys_user['role'])
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
    db = AndrewDB()
    form = CUHotelForm()
    if current_user.is_hotel_admin():
        if form.validate_on_submit():
            img_name = imgName(form.img.data.filename)
            if img_name:
                img_path = '/static/img/hotels/' + img_name
                try:
                    db.insert_location_if_not_exists(form.country.data, form.city.data)
                    db.add_hotel(form.city.data, form.address.data, form.hotel_name.data, form.stars.data,
                                 form.description.data,
                                 current_user.user_id, img_path)
                except Exception as e:
                    print(e)
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
    db = AndrewDB()
    form = CUHotelForm()
    if current_user.is_hotel_admin():
        if form.validate_on_submit():
            img_name = imgName(form.img.data.filename)
            if img_name:
                res = db.get_city(form.country.data, form.city.data)
                if not res:
                    db.add_city(form.country.data, form.city.data)

                old_img = db.get_image_name_by_hotel_id(hotel_id)
                img_path = '/static/img/hotels/' + img_name
                db.update_hotel_by_id(hotel_id, form.city.data, form.address.data, form.hotel_name.data, form.stars.data, form.description.data, img_path)
                form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                os.remove(os.path.abspath('app' + old_img))
                return redirect(url_for('myHotels'))
        res = db.get_hotel_and_address_by_id(hotel_id)
        return render_template('edit_hotel.html', form=form, hotel=res)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/manage-hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def manageHotel(hotel_id):
    db = AndrewDB()
    g.role = 'receptionist'
    recForm = CReceptionistForm()
    roomForm = CRoomForm()
    form = UDRoomForm()
    form2 = URoomForm()
    form3 = DReceptionistForm()
    if current_user.is_hotel_admin():
        if form.delete.data:
            if db.delete_room_by_id(form.room_id.data):
                flash('Room was removed')
            return redirect(url_for('manageHotel', hotel_id=hotel_id))

        if form2.edit.data:
            if form2.validate_on_submit():
                option_id = None
                config_id = None
                res = db.get_option_by_params(form2.is_bathroom.data, form2.is_tv.data, form2.is_wifi.data,
                                              form2.is_bathhub.data, form2.is_aircond.data)
                if not res:
                    option_id = db.insert_option(form2.is_bathroom.data, form2.is_tv.data, form2.is_wifi.data,
                                                 form2.is_bathhub.data, form2.is_aircond.data)
                else:
                    option_id = res['option_id']
                res = db.select_config(form2.sing_bed.data, form2.doub_bed.data, form2.sofa_bed.data)
                if not res:
                    config_id = db.insert_config(form2.sing_bed.data, form2.doub_bed.data, form2.sofa_bed.data)
                else:
                    config_id = res['config_id']
                db.set_up_room_by_id(config_id, option_id, form2.quantity.data, form2.title.data,
                                     form2.description.data, form2.cost.data, form2.room_id.data)

        if form3.del_rec.data:
            if db.delete_receptionist_by_id(form3.user_id.data):
                flash("Receptionist was removed")

        if recForm.save.data:
            if recForm.validate_on_submit():
                hash_password = bcrypt.generate_password_hash(recForm.password.data).decode('utf-8')
                user_id = db.insert_user(recForm.email.data, hash_password, g.role)
                if user_id:
                    flash('User with this email already registered')
                else:
                    redirect(url_for('manageHotel', hotel_id=hotel_id))
                if db.add_new_receptionist(user_id, hotel_id, recForm.first_name.data, recForm.last_name.data,
                                           recForm.telephone.data, recForm.salary.data):
                    flash("Receptionist was added")
                return redirect(url_for('manageHotel', hotel_id=hotel_id))

        if roomForm.save.data:
            if roomForm.validate_on_submit():
                option_id = None
                config_id = None

                res = db.get_option_by_params(roomForm.is_bathroom.data, roomForm.is_tv.data, roomForm.is_wifi.data,
                                              roomForm.is_bathhub.data, roomForm.is_aircond.data)
                if not res:
                    option_id = db.insert_option(roomForm.is_bathroom.data, roomForm.is_tv.data, roomForm.is_wifi.data,
                                                 roomForm.is_bathhub.data, roomForm.is_aircond.data)
                else:
                    option_id = res['option_id']

                res = db.select_config(roomForm.sing_bed.data, roomForm.doub_bed.data, roomForm.sofa_bed.data)
                if not res:
                    config_id = db.insert_config(roomForm.sing_bed.data, roomForm.doub_bed.data, roomForm.sofa_bed.data)
                else:
                    config_id = res['config_id']
                db.add_new_room(hotel_id, config_id, option_id, roomForm.quantity.data, roomForm.title.data,
                                roomForm.description.data, roomForm.cost.data)
                flash('Room was added')
                return redirect(url_for('manageHotel', hotel_id=hotel_id))
        hotel = db.get_hotel_by_id(hotel_id)
        rooms = db.get_rooms_with_settings_by_id(hotel_id)
        recep = db.get_receptionists_by_hotel_id(hotel_id)

        return render_template('manage_hotel.html', recForm=recForm, roomForm=roomForm, form=form, form2=form2,
                               form3=form3, hotel=hotel, rooms=rooms, recep=recep)
    else:
        flash("Access error")
        return redirect(url_for('login'))


@app.route('/my-booking', methods=['GET', 'POST'])
@login_required
def myBooking():
    db = AndrewDB()
    form = DBookingForm()
    today = datetime.datetime.now().date()
    if form.validate_on_submit():
        if not db.delete_transaction(form.transaction_id.data):
            flash("Reservation has been cancelled")
    info = db.get_some_info_by_user_id(current_user.get_id())
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
    g.role = 'admin'
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
