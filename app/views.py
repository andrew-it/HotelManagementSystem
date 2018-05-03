import datetime
import logging

import os.path
import psycopg2.extras
from flask import flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, bcrypt, login_manager
from app.db import AndrewDB
from .forms import CAdmin, CReceptionistForm, CRoomForm, CUHotelForm, DBookingForm, DReceptionistForm, InfoForm, \
    LoginForm, ProfileForm, RegisterForm, ReserveRoomForm, SearchForm, UDHotelForm, UDRoomForm, URoomForm
from .helpers import reverseDate, imgName, check_password
from .models import Customer, HotelAdmin, User

logger = logging.getLogger(__name__)

dictCursor = psycopg2.extras.DictCursor


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    logger.info("Got an index page request: %s" % request)
    form = SearchForm()
    form.csrf_enabled = False
    if request.method == 'POST':
        logger.info("Validating the search hotel form")
        if form.validate_on_submit():
            search = form.data
            search['destination'] = '%' + search['destination'].lower() + '%'
            search['checkin'] = reverseDate(search['checkin'])
            search['checkout'] = reverseDate(search['checkout'])
            session['search'] = search
            logger.info("The form is valid, redirecting to the Search hotel page")
            return redirect(url_for('searchHotel'))
        else:
            flash('The required fields are not filled')
            logger.info("The form is invalid - The required fields are not filled")
    logger.info("Rendering the index page")
    return render_template('index.html', form=form)


@app.route('/search-hotel', methods=['GET', 'POST'])
def searchHotel():
    logger.info("Got a search hotel page request: %s" % request)
    db = AndrewDB()
    form = InfoForm()
    form.csrf_enabled = False
    search = session['search']
    if request.method == 'POST':
        if current_user.is_anonymous():
            flash("You must be authorized to reserve rooms")
            logger.info("The user must be authorized to reserve rooms. Redirecting to login page")
            return redirect(url_for('login'))
        logger.info("Redirecting to More info page")
        return redirect(url_for('moreInfo', hotel_id=form.hotel_id.data))

    hotels = db.search_hotels_by_form(search)
    logger.info("Rendering the Search hotel page")
    return render_template('search_hotel.html', form=form, hotels=hotels)


@app.route('/more-info/<int:hotel_id>', methods=['GET', 'POST'])
def moreInfo(hotel_id):
    logger.info("Got a more info page request: %s" % request)
    db = AndrewDB()
    form = ReserveRoomForm()
    form.csrf_enabled = False
    search = session['search']
    search['hotel_id'] = hotel_id
    if request.method == 'POST':
        info = form.data
        info['customer_id'] = current_user.user_id
        checkin = datetime.datetime.strptime(search['checkin'], '%Y-%m-%d').date()
        checkout = datetime.datetime.strptime(search['checkout'], '%Y-%m-%d').date()
        nights = (checkout - checkin).days
        cost = db.get_cost_by_id(form.room_id.data)
        info['amount'] = int(form.quantity.data) * nights * int(cost)
        info['transaction_id'] = db.create_transaction_get_id(info)
        db.add_booking(info)
        flash('Room was reserved')
        logger.info("Room with ID=%s was reserved" % form.room_id.data)
    hotel = db.get_vw_hotel_by_id(hotel_id)
    rooms = db.search_get_rooms(search)
    cust_info = db.get_vw_customer_by_id(current_user.user_id)
    logger.info("Rendering the More info page")
    return render_template('booking.html', form=form, search=search, hotel=hotel, rooms=rooms, cust_info=cust_info)


@login_manager.user_loader
def load_user(user_id):
    logger.info("Loading a user: ID=%s" % user_id)
    db = AndrewDB()
    res = db.get_user_by_id(user_id)
    if not res:
        logger.warning("User not found: ID=%s" % user_id)
        return None
    return User(res['user_id'], res['email'], res['password'], res['role'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Got a login page request: %s" % request)
    db = AndrewDB()
    form = LoginForm()
    logger.info("Validating the login form")
    form.csrf_enabled = False
    if form.validate_on_submit():
        sys_user = db.get_sys_user_by_email(form.email.data)
        if not sys_user or not check_password(sys_user['password'], form.password.data):
            flash('Email Address or Password is invalid')
            logger.info("Email address or password is invalid, redirecting to the login page")
            return redirect(url_for('login'))
        user = User(sys_user['user_id'], sys_user['email'], sys_user['password'], sys_user['role'])
        if form.remember_me.data:
            login_user(user, remember=True)
        else:
            login_user(user)
        flash('Logged in successfully')
        logger.info("Logged in successfully: ID = %s" % user.get_id())
        if user.is_receptionist():
            logger.info("Redirecting to Manage booking page")
            return redirect(url_for('manageBooking'))
        if user.is_hotel_admin():
            logger.info("Redirecting to My hotels page")
            return redirect(url_for('myHotels'))
        if user.is_admin():
            logger.info("Redirecting to admin page")
            return redirect(url_for('admin'))
        logger.info("Redirecting to index page")
        return redirect(url_for('index'))
    logger.info("Rendering the login page")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logger.info("Got a logout page request: %s" % request)
    logout_user()
    flash('You were logged out.')
    logger.info("Logout successful, redirecting to the index page")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    logger.info("Got a register page request: %s" % request)
    g.role = 'customer'
    db = AndrewDB()
    form = RegisterForm()
    logger.info("Validating the register form")
    form.csrf_enabled = False
    if form.validate_on_submit():
        if not form.password.data == form.password_confirmation.data:
            logger.info("Password confirmation failed, Redirecting to register page")
            return redirect(url_for('register'))

        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        res = db.insert_sys_user(form.email.data, hash_password, g.role)
        if not res:
            flash('User with this email already registered')
            logger.info("User with this email (%s) alredy registered, redirecting to register page" % form.email.data)
            return redirect(url_for('register'))

        user_id = res[0].strip('()').split(',')[0]
        db.add_customer(user_id, form.first_name.data, form.last_name.data, form.telephone.data)

        user = User(user_id, form.email.data, hash_password, g.role)
        login_user(user)
        flash('User successfully registered')
        logger.info("User (ID = %s) successfully registered, redirecting to index page" % user.get_id())
        return redirect(url_for('index'))
    logger.info("Rendering the register page")
    return render_template('register.html', form=form)


@app.route('/add-property', methods=['GET', 'POST'])
def addProperty():
    logger.info("Got an Add property page request: %s" % request)
    g.role = 'hotel_admin'
    db = AndrewDB()
    form = RegisterForm()
    logger.info("Validating the register form")
    form.csrf_enabled = False
    if form.validate_on_submit():
        if not form.password.data == form.password_confirmation.data:
            logger.info("Password confirmation failed, Redirecting to add property page")
            return redirect(url_for('addProperty'))
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        res = db.insert_sys_user(form.email.data, hash_password, g.role)
        if res is None:
            flash('User with this email already registered')
            logger.info("User with this email (%s) alredy registered, "
                        "redirecting to add property page" % form.email.data)
            return redirect(url_for('addProperty'))
        user_id = res[0].strip('()').split(',')[0]
        db.insert_hotel_admin(str(user_id), str(form.first_name.data),
                              str(form.last_name.data), str(form.telephone.data))
        print(user_id)
        user = User(user_id, form.email.data, hash_password, g.role)
        login_user(user)
        flash('User successfully registered')
        logger.info("User (ID = %s) successfully registered, redirecting to My hotels page" % user.get_id())
        return redirect(url_for('myHotels'))
    logger.info("Rendering the Add property page")
    return render_template('property.html', form=form)


@app.route('/profile', methods=['GET'])
@login_required
def get_profile():
    logger.info("Got a profile page request: %s" % request)
    db = AndrewDB()
    form = ProfileForm()
    user = current_user
    user_info = None
    form.csrf_enabled = False
    if user.is_customer():
        res = db.get_customer_by_id(user.user_id)
        user_info = Customer(res['first_name'],
                             res['last_name'],
                             user.email,
                             res['phone_number'],
                             res['payment_info'])
    elif user.is_hotel_admin():
        res = db.get_hotel_admin_by_id(user.user_id)
        if res:
            user_info = HotelAdmin(res['first_name'], res['last_name'], user.email, res['phone_number'])
        else:
            flash("Unable to find a hotel admin entry")
            logger.info("Unable to find a hotel admin entry, Redirecting to index page")
            return redirect(url_for('index'))
    elif user.is_receptionist():
        user_info = db.get_receptionist_by_id(user.user_id)
        user_info['email'] = user.email
    elif user.is_admin():
        db.get_admin_by_id(user.user_id)
        user_info['email'] = user.email
    logger.info("Rendering the Profile page")
    return render_template('profile.html', form=form, user=user_info)


@app.route('/profile', methods=['POST'])
@login_required
def update_profile():
    logger.info("Got a profile page request: %s" % request)
    db = AndrewDB()
    form = ProfileForm()
    user = current_user
    logger.info("Validating the profile form")
    form.csrf_enabled = False
    if form.validate_on_submit():
        if user.is_customer():
            db.update_customer(user.user_id, form.first_name.data, form.last_name.data, form.telephone.data,
                               form.credit_card.data)
            logger.info("Redirecting to index page")
            return redirect(url_for('index'))
        elif user.is_hotel_admin():
            db.update_hotel_admin(user.user_id, form.first_name.data, form.last_name.data, form.telephone.data)
            logger.info("Redirecting to index page")
            return redirect(url_for('index'))
        elif user.is_admin():
            db.update_admin(user.user_id, form.first_name.data, form.last_name.data, form.telephone.data)
            logger.info("Redirecting to admin page")
            return redirect(url_for('admin'))

    flash("Invalid form")
    logger.info("Invalid profile form, Redirecting to add property page")
    return redirect(url_for('index'))


@app.route('/my-hotel', methods=['GET', 'POST'])
@login_required
def myHotels():
    logger.info("Got a My hotels page request: %s" % request)
    db = AndrewDB()
    form = UDHotelForm()
    form.csrf_enabled = False
    if current_user.is_hotel_admin():
        logger.info("Validating the Update or Delete hotel form")
        if form.validate_on_submit():
            if form.edit.data:
                logger.info("Redirecting to Edit hotel page")
                return redirect(url_for('editHotel', hotel_id=form.hotel_id.data))
            if form.delete.data:
                img = db.remove_hotel_by_id(form.hotel_id.data)
                os.remove(os.path.abspath('app' + img))
                flash('Hotel was removed')
                logger.info("Hotel (ID=%s) was removed, Redirecting to My Hotels page" % form.hotel_id.data)
                return redirect(url_for('myHotels'))
            if form.manage.data:
                logger.info("Redirecting to manage hotel page")
                return redirect(url_for('manageHotel', hotel_id=form.hotel_id.data))
            if form.add_hotel.data:
                logger.info("Redirecting to Add hotel page")
                return redirect(url_for('addHotel'))
        hotels = db.get_hotels_by_admin_id(current_user.get_id())
        logger.info("Rendering the My hotels page")
        return render_template('my_hotel.html', form=form, hotels=hotels)
    else:
        flash("Access error")
        logger.info("Access error, Redirecting to login page")
        return redirect(url_for('login'))


@app.route('/add-hotel', methods=['GET', 'POST'])
@login_required
def addHotel():
    logger.info("Got an Add hotel page request: %s" % request)
    db = AndrewDB()
    form = CUHotelForm()
    form.csrf_enabled = False
    if current_user.is_hotel_admin():
        logger.info("Validating the Create and Update hotel form")
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
                    logger.exception("Unable to add Hotel")
                    print(e)
                    logger.info("Redirecting to My hotels page")
                    return redirect(url_for('myHotels'))
                form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                flash('Hotel was added')
                logger.info("Hotel was added, Redirecting to My hotels page")
                return redirect(url_for('myHotels'))
        logger.info("Rendering the Edit hotel page")
        return render_template('edit_hotel.html', form=form, hotel=None)
    else:
        flash("Access error")
        logger.info("Access error, Redirecting to login page")
        return redirect(url_for('login'))


@app.route('/edit-hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def editHotel(hotel_id):
    logger.info("Got an Edit hotel page request: %s" % request)
    db = AndrewDB()
    form = CUHotelForm()
    form.csrf_enabled = False
    if current_user.is_hotel_admin():
        logger.info("Validating the Create and Update hotel form")
        if form.validate_on_submit():
            img_name = imgName(form.img.data.filename)
            if img_name:
                db.insert_location_if_not_exists(form.country.data, form.city.data)

                old_img = db.get_image_name_by_hotel_id(hotel_id)
                img_path = '/static/img/hotels/' + img_name
                db.update_hotel_by_id(hotel_id, form.city.data, form.address.data, form.hotel_name.data,
                                      form.stars.data, form.description.data, img_path)
                form.img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                os.remove(os.path.abspath('app' + old_img))
                return redirect(url_for('myHotels'))
        res = db.get_hotel_and_address_by_id(hotel_id)
        logger.info("Rendering the Edit hotel page")
        return render_template('edit_hotel.html', form=form, hotel=res)
    else:
        flash("Access error")
        logger.info("Access error, Redirecting to login page")
        return redirect(url_for('login'))


@app.route('/manage-hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def manageHotel(hotel_id):
    logger.info("Got a manage hotel page request: %s" % request)
    db = AndrewDB()
    g.role = 'receptionist'
    recForm = CReceptionistForm()
    roomForm = CRoomForm()
    form = UDRoomForm()
    form2 = URoomForm()
    form3 = DReceptionistForm()
    form.csrf_enabled = False
    form2.csrf_enabled = False
    form3.csrf_enabled = False
    if current_user.is_hotel_admin():
        if form.delete.data:
            if db.delete_room_by_id(form.room_id.data):
                flash('Room was removed')
                logger.info("Room was removed: ID = %s" % form.room_id.data)
            logger.info("Redirecting to manage hotel page")
            return redirect(url_for('manageHotel', hotel_id=hotel_id))

        if form2.edit.data:
            logger.info("Validating the Update room form")
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
                logger.info("Receptionist was removed: ID = %s" % form3.user_id.data)

        if recForm.save.data:
            logger.info("Validating the Create receptionist form")
            if recForm.validate_on_submit():
                hash_password = bcrypt.generate_password_hash(recForm.password.data).decode('utf-8')
                user_id = db.insert_sys_user_get_id(recForm.email.data, hash_password, g.role)
                if user_id:
                    flash('User with this email already registered')
                else:
                    logger.info("Redirecting to manage hotel page")
                    redirect(url_for('manageHotel', hotel_id=hotel_id))
                if db.add_new_receptionist(user_id, hotel_id, recForm.first_name.data, recForm.last_name.data,
                                           recForm.telephone.data, recForm.salary.data):
                    flash("Receptionist was added")
                    logger.info("Receptionist was added: ID = %s" % recForm.user_id.data)
                logger.info("Redirecting to manage hotel page")
                return redirect(url_for('manageHotel', hotel_id=hotel_id))

        if roomForm.save.data:
            logger.info("Validating the Create room form")
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
                logger.info("Receptionist was added (ID = %s), Redirecting to manage hotel page"
                            % roomForm.user_id.data)
                return redirect(url_for('manageHotel', hotel_id=hotel_id))
        hotel = db.get_hotel_by_id(hotel_id)
        rooms = db.get_rooms_with_settings_by_id(hotel_id)
        recep = db.get_receptionists_by_hotel_id(hotel_id)
        logger.info("Rendering the Manage hotel page")
        return render_template('manage_hotel.html', recForm=recForm, roomForm=roomForm, form=form, form2=form2,
                               form3=form3, hotel=hotel, rooms=rooms, recep=recep)
    else:
        flash("Access error")
        logger.info("Access error, Redirecting to login page")
        return redirect(url_for('login'))


@app.route('/my-booking', methods=['GET', 'POST'])
@login_required
def myBooking():
    logger.info("Got a My booking page request: %s" % request)
    db = AndrewDB()
    form = DBookingForm()
    today = datetime.datetime.now().date()
    logger.info("Validating the Delete booking form")
    form.csrf_enabled = False
    if form.validate_on_submit():
        if not db.delete_transaction(form.transaction_id.data):
            flash("Reservation has been cancelled")
            logger.info("Reservation was cancelled: ID = %s" % form.transaction_id.data)
    info = db.get_some_info_by_user_id(current_user.get_id())
    logger.info("Rendering the My booking page")
    return render_template('my_booking.html', form=form, info=info, today=today)


@app.route('/manage-booking', methods=['GET', 'POST'])
@login_required
def manageBooking():
    logger.info("Got a Manage booking page request: %s" % request)
    db = AndrewDB()
    if 'recep' not in session:
        session['recep'] = db.get_all_receptionists(current_user.user_id)
    if 'hotel' not in session:
        session['hotel'] = db.get_vw_hotel_by_id(session['recep']['hotel_id'])
    recep = session['recep']
    hotel = session['hotel']
    bookings = db.get_booked_rooms_by_hotel_id(recep['hotel_id'])
    logger.info("Rendering the Booked rooms page")
    return render_template('booked_rooms.html', bookings=bookings, hotel=hotel)


@app.route('/new-booking', methods=['GET', 'POST'])
@login_required
def newBooking():
    logger.info("Got a New booking page request: %s" % request)
    db = AndrewDB()
    recep = session['recep']
    hotel = session['hotel']
    today = datetime.datetime.now().date().strftime("%Y-%m-%d")
    rooms = db.get_rooms_by_params(recep['hotel_id'], today, today)
    logger.info("Rendering the New booking page")
    return render_template('new_booking.html', rooms=rooms, hotel=hotel)


@app.route('/admin-panel', methods=['GET', 'POST'])
@login_required
def admin():
    logger.info("Got an admin panel page request: %s" % request)
    form = CAdmin()
    db = AndrewDB()
    g.role = 'admin'
    logger.info("Validating the Create admin form")
    form.csrf_enabled = False
    if request.method == 'POST' and form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = db.insert_sys_user_get_id(form.email.data, hash_password)
        if user_id is None:
            flash('User with this email already registered')
            logger.info("User with this email already registered, Redirecting to admin page")
            return redirect(url_for('admin-panel'))
        db.insert_admin(str(user_id), form.first_name.data, form.last_name.data, form.telephone.data)
        flash("Admin was added")
        logger.info("Admin was added, Redirecting to admin page")
        return redirect(url_for('admin-panel'))
    hotels = db.get_all_hotels()
    users = db.get_all_system_users()
    db_stat = db.get_db_statistics()
    admins = db.get_all_admins()
    g.db.commit()
    logger.info("Rendering the admin_panel page")
    return render_template('admin_panel.html', hotels=hotels, users=users, db_stat=db_stat, form=form, admins=admins)
