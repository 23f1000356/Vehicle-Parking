from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# Configure SQLAlchemy with SQLite using an absolute path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'parking.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    occupied_spots = db.Column(db.Integer, nullable=False, default=0)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String, nullable=False, default='A')  # 'A' for Available, 'O' for Occupied
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=False)
    vehicle_number = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False, default=3)
    vehicle_type = db.Column(db.String, nullable=False, default='Car')  # Added vehicle_type
    status = db.Column(db.String, nullable=False, default='Active')
    user = db.relationship('User', backref='reservations', lazy=True)

# Initialize the database and migrate initial data
try:
    print(f"Database path: {DB_PATH}")
    print("Starting database initialization...")
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully.")

        # Migrate admin user
        print("Migrating admin user...")
        if not User.query.filter_by(email='admin@gmail.com').first():
            admin_user = User(
                email='admin@gmail.com',
                password=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                fullname='Admin User',
                address='Admin Address',
                pincode='123456',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

        # Migrate default user
        print("Migrating default user...")
        default_user_data = {
            "email": "user@gmail.com",
            "password": "user123",
            "fullname": "Default User",
            "address": "123 Default St",
            "pincode": "123456"
        }
        if not User.query.filter_by(email=default_user_data['email']).first():
            user = User(
                email=default_user_data['email'],
                password=bcrypt.hashpw(default_user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                fullname=default_user_data['fullname'],
                address=default_user_data['address'],
                pincode=default_user_data['pincode'],
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            print("Default user created.")
        else:
            print("Default user already exists.")

        # Migrate parking lots
        print("Migrating parking lots...")
        for lot in [
            {"id": 1, "name": "Parking1", "spots": 15, "price": 3, "occupied": 3, "address": "45th Street", "pincode": "123456"},
            {"id": 2, "name": "Parking2", "spots": 10, "price": 4, "occupied": 4, "address": "Main Avenue", "pincode": "654321"}
        ]:
            if not ParkingLot.query.get(lot['id']):
                new_lot = ParkingLot(
                    id=lot['id'],
                    prime_location_name=lot['name'],
                    price=lot['price'],
                    address=lot['address'],
                    pincode=lot['pincode'],
                    maximum_number_of_spots=lot['spots'],
                    occupied_spots=lot['occupied']
                )
                db.session.add(new_lot)
                db.session.flush()
                for i in range(lot['spots']):
                    status = 'O' if i < lot['occupied'] else 'A'
                    spot = ParkingSpot(lot_id=new_lot.id, status=status)
                    db.session.add(spot)
                db.session.commit()
                print(f"Parking lot {lot['name']} created with {lot['spots']} spots.")
            else:
                print(f"Parking lot {lot['name']} already exists.")

        # Migrate reservations with vehicle_type and duration
        print("Migrating reservations...")
        for vehicle in [
            {
                "parking_lot_id": "parking1",
                "user_id": User.query.filter_by(email="user@gmail.com").first().id if User.query.filter_by(email="user@gmail.com").first() else None,
                "spot_id": 1,
                "address": "45th Street",
                "pincode": "123456",
                "vehicle_number": "ABC123",
                "vehicle_type": "Car",
                "duration": 3,
                "date_time": datetime.strptime("2025-05-28 01:00:00", '%Y-%m-%d %H:%M:%S'),
                "est_cost": 9.0,
                "status": "Active"
            },
            {
                "parking_lot_id": "parking2",
                "user_id": User.query.filter_by(email="user@gmail.com").first().id if User.query.filter_by(email="user@gmail.com").first() else None,
                "spot_id": 16,
                "address": "Main Avenue",
                "pincode": "654321",
                "vehicle_number": "XYZ789",
                "vehicle_type": "Bike",
                "duration": 3,
                "date_time": datetime.strptime("2025-05-27 15:30:00", '%Y-%m-%d %H:%M:%S'),
                "est_cost": 12.0,
                "status": "Completed"
            }
        ]:
            if vehicle['user_id']:
                lot_id = int(vehicle['parking_lot_id'].replace('parking', ''))
                spot = ParkingSpot.query.filter_by(lot_id=lot_id, id=vehicle['spot_id']).first()
                if spot and not Reservation.query.filter_by(spot_id=spot.id, parking_timestamp=vehicle['date_time']).first():
                    reservation = Reservation(
                        spot_id=spot.id,
                        user_id=vehicle['user_id'],
                        parking_timestamp=vehicle['date_time'],
                        parking_cost=vehicle['est_cost'],
                        vehicle_number=vehicle['vehicle_number'],
                        vehicle_type=vehicle['vehicle_type'],
                        duration=vehicle['duration'],
                        status=vehicle['status']
                    )
                    db.session.add(reservation)
                    db.session.commit()
                    print(f"Reservation created for spot {spot.id} in parking lot {lot_id}.")
                else:
                    print(f"Reservation for spot {vehicle['spot_id']} in parking lot {lot_id} already exists or spot not found.")

        # Update existing reservations with default vehicle_type and duration if null
        print("Updating existing reservations with default vehicle_type and duration...")
        reservations = Reservation.query.filter((Reservation.vehicle_type == None) | (Reservation.duration == None)).all()
        for res in reservations:
            if res.vehicle_type is None:
                res.vehicle_type = 'Car'
            if res.duration is None:
                res.duration = 3
        db.session.commit()
        print("Existing reservations updated with vehicle_type and duration.")

except Exception as e:
    print(f"Error during database initialization: {str(e)}")

# Routes
@app.route('/search', methods=['GET', 'POST'])
def search():
    vehicles = []
    if request.method == 'POST':
        parking_lot_id = request.form.get('parking_lot_id', '').strip()
        user_id = request.form.get('user_id', '').strip()
        address = request.form.get('address', '').strip()
        vehicle_type = request.form.get('vehicle_type', '').strip()

        query = db.session.query(Reservation, ParkingLot)\
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
            .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
            .filter(Reservation.status == 'Active')

        if parking_lot_id:
            try:
                query = query.filter(ParkingLot.id == int(parking_lot_id))
            except ValueError:
                flash("Please enter a valid numeric Parking Lot ID (e.g., 1 or 2).", "danger")
                return render_template('search.html', vehicles=vehicles)
        if user_id:
            try:
                query = query.filter(Reservation.user_id == int(user_id))
            except ValueError:
                flash("Please enter a valid numeric User ID.", "danger")
                return render_template('search.html', vehicles=vehicles)
        if address:
            query = query.filter(ParkingLot.address.ilike(f'%{address}%'))
        if vehicle_type:
            valid_vehicle_types = ['Car', 'Truck', 'Bike', 'Scooty', 'Cycle']
            if vehicle_type in valid_vehicle_types:
                query = query.filter(Reservation.vehicle_type == vehicle_type)
            else:
                flash("Please select a valid vehicle type.", "danger")
                return render_template('search.html', vehicles=vehicles)

        vehicles = [{
            'parking_lot_id': str(lot.id),
            'prime_location_name': lot.prime_location_name,
            'user_id': str(res.user_id),
            'spot_id': str(res.spot_id),
            'address': lot.address,
            'pincode': lot.pincode,
            'vehicle_number': res.vehicle_number,
            'vehicle_type': res.vehicle_type,
            'parking_timestamp': res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'parking_cost': res.parking_cost
        } for res, lot in query.all()]

        if not (parking_lot_id or user_id or address or vehicle_type):
            flash("Please enter at least one search criterion.", "warning")

    return render_template('search.html', vehicles=vehicles)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(email=email, role=role).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['logged_in'] = True
            session['role'] = role
            session['user_id'] = str(user.id)
            flash('Login successful!', 'success')
            if role == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/book')
def book():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    parking_lots = ParkingLot.query.all()
    return render_template('book.html', parking_lots=parking_lots)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/users')
def users():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    users = User.query.filter_by(role='user').all()
    for user in users:
        print(f"User ID: {user.id}, Full Name: {user.fullname}, Email: {user.email}")
    return render_template('users.html', users=users)

@app.route('/debug/users')
def debug_users():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    users = User.query.all()
    for user in users:
        print(f"Debug User ID: {user.id}, Full Name: {user.fullname}, Email: {user.email}")
    return render_template('users.html', users=users)

@app.route('/summary')
def summary():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('summary.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        fullname = request.form['fullname'].strip()
        address = request.form['address'].strip()
        pincode = request.form['pincode'].strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered! Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        max_id = db.session.query(db.func.max(User.id)).scalar() or 100
        user_id = max_id + 1
        new_user = User(
            id=user_id,
            email=email,
            password=hashed_password,
            fullname=fullname,
            address=address,
            pincode=pincode,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    parking_lots = ParkingLot.query.all()
    active_reservations = db.session.query(Reservation, ParkingLot)\
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
        .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
        .filter(Reservation.status == 'Active').all()
    parked_vehicles = [{
        'parking_lot_id': str(lot.id),
        'prime_location_name': lot.prime_location_name,
        'user_id': str(res.user_id),
        'spot_id': str(res.spot_id),
        'address': lot.address,
        'pincode': lot.pincode,
        'vehicle_number': res.vehicle_number,
        'vehicle_type': res.vehicle_type,
        'parking_timestamp': res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'parking_cost': res.parking_cost,
        'duration': res.duration,
        'reservation_id': res.id
    } for res, lot in active_reservations]
    return render_template('admin_dashboard.html', parking_lots=parking_lots, parked_vehicles=parked_vehicles)

@app.route('/user_dashboard')
def user_dashboard():
    if 'logged_in' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    user_id = int(session.get('user_id'))
    user = User.query.get_or_404(user_id)
    parking_lots_raw = ParkingLot.query.all()
    parking_lots = [{
        'id': lot.id,
        'prime_location_name': lot.prime_location_name,
        'address': lot.address,
        'pincode': lot.pincode,
        'price': lot.price,
        'total_spots': lot.maximum_number_of_spots,
        'available_spots': lot.maximum_number_of_spots - lot.occupied_spots
    } for lot in parking_lots_raw]
    
    bookings = db.session.query(Reservation, ParkingLot)\
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
        .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
        .filter(Reservation.user_id == user_id).all()
    user_bookings = [{
        'id': res.id,
        'user_id': str(res.user_id),
        'parking_lot_id': str(lot.id),
        'spot_id': str(res.spot_id),
        'lot_name': lot.prime_location_name,
        'vehicle_number': res.vehicle_number,
        'vehicle_type': res.vehicle_type,
        'booking_time': res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': res.duration,
        'est_cost': res.parking_cost,
        'status': res.status,
        'address': lot.address,
        'pincode': lot.pincode
    } for res, lot in bookings]

    selected_lot_id = request.args.get('selected_lot_id', type=int)
    selected_lot = None
    if selected_lot_id:
        lot = ParkingLot.query.get(selected_lot_id)
        if lot:
            selected_lot = {
                'id': lot.id,
                'prime_location_name': lot.prime_location_name,
                'address': lot.address,
                'total_spots': lot.maximum_number_of_spots,
                'available_spots': lot.maximum_number_of_spots - lot.occupied_spots
            }

    return render_template('user_dashboard.html', user=user, parking_lots=parking_lots, bookings=user_bookings, selected_lot=selected_lot)

@app.route('/add_lot', methods=['POST'])
def add_lot():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        name = request.form.get('name', '').strip()
        if not name:
            raise ValueError("Parking lot name cannot be empty.")
        
        spots_input = request.form.get('spots', '').strip()
        if not spots_input.isdigit() or int(spots_input) <= 0:
            raise ValueError("Total spots must be a positive integer.")
        spots = int(spots_input)
        
        price_input = request.form.get('price', '').strip()
        if not price_input.replace('.', '', 1).isdigit() or float(price_input) <= 0:
            raise ValueError("Price must be a positive number.")
        price = float(price_input)
        
        address = request.form.get('address', '').strip()
        if not address:
            raise ValueError("Address cannot be empty.")
        
        pincode = request.form.get('pincode', '').strip()
        if not pincode:
            raise ValueError("Pincode cannot be empty.")
        
        new_lot = ParkingLot(
            prime_location_name=name,
            price=price,
            address=address,
            pincode=pincode,
            maximum_number_of_spots=spots,
            occupied_spots=0
        )
        db.session.add(new_lot)
        db.session.flush()
        for _ in range(spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        flash(f'Parking lot "{name}" added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    except ValueError as e:
        db.session.rollback()
        flash(f"Invalid input: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/edit_lot/<int:lot_id>', methods=['POST'])
def edit_lot(lot_id):
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        name = request.form.get('name', '').strip()
        if not name:
            raise ValueError("Parking lot name cannot be empty.")
        
        spots = request.form.get('spots', '').strip()
        if not spots.isdigit() or int(spots) <= 0:
            raise ValueError("Total spots must be a positive integer.")
        new_spots = int(spots)
        
        if new_spots < lot.occupied_spots:
            raise ValueError(f"Cannot reduce maximum spots below the current occupied spots ({lot.occupied_spots}). Please free up spots first or enter a number greater than or equal to {lot.occupied_spots}.")
        
        price = request.form.get('price', '').strip()
        if not price.replace('.', '', 1).isdigit() or float(price) <= 0:
            raise ValueError("Price must be a positive number.")
        price = float(price)
        
        address = request.form.get('address', '').strip()
        if not address:
            raise ValueError("Address cannot be empty.")
        
        pincode = request.form.get('pincode', '').strip()
        if not pincode:
            raise ValueError("Pincode cannot be empty.")
        
        lot.prime_location_name = name
        lot.price = price
        lot.address = address
        lot.pincode = pincode
        
        current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
        if new_spots > current_spots:
            for _ in range(new_spots - current_spots):
                spot = ParkingSpot(lot_id=lot_id, status='A')
                db.session.add(spot)
        elif new_spots < current_spots:
            spots_to_remove = current_spots - new_spots
            available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').limit(spots_to_remove).all()
            for spot in available_spots:
                db.session.delete(spot)
            remaining_to_remove = spots_to_remove - len(available_spots)
            if remaining_to_remove > 0:
                occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').limit(remaining_to_remove).all()
                for spot in occupied_spots:
                    reservation = Reservation.query.filter_by(spot_id=spot.id, status='Active').first()
                    if reservation:
                        reservation.status = 'Cancelled'
                    db.session.delete(spot)
                lot.occupied_spots -= remaining_to_remove
        
        lot.maximum_number_of_spots = new_spots
        # Ensure occupied_spots does not exceed maximum_number_of_spots after update
        if lot.occupied_spots > lot.maximum_number_of_spots:
            lot.occupied_spots = lot.maximum_number_of_spots
        
        db.session.commit()
        flash(f'Parking lot "{lot.prime_location_name}" updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    except ValueError as e:
        db.session.rollback()
        flash(f"Invalid input: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        if lot.occupied_spots > 0:
            flash("Sorry, can't delete the lot. Spots are occupied.", "alert-danger")
            return redirect(url_for('dashboard'))
        name = lot.prime_location_name
        db.session.delete(lot)
        db.session.commit()
        flash(f'Parking lot "{name}" deleted successfully!', 'alert-success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting parking lot: {str(e)}", 'alert-danger')
    return redirect(url_for('dashboard'))

@app.route('/delete_spot/<int:lot_id>/<int:spot_id>')
def delete_spot(lot_id, spot_id):
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        spot = ParkingSpot.query.get_or_404(spot_id)
        if spot.lot_id != lot_id:
            raise ValueError("Spot does not belong to the specified parking lot.")
        
        if spot.status == 'O':
            lot.occupied_spots -= 1
            spot.status = 'A'
            reservation = Reservation.query.filter_by(spot_id=spot_id, status='Active').first()
            if reservation:
                reservation.status = 'Cancelled'
            flash(f'Spot {spot_id} in parking lot "{lot.prime_location_name}" has been freed.', 'success')
        else:
            flash(f'Spot {spot_id} in parking lot "{lot.prime_location_name}" is already unoccupied.', 'warning')
        
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"Error freeing spot: {str(e)}", 'danger')
    return redirect(url_for('dashboard'))

@app.route('/book_spot/<int:lot_id>', methods=['POST'])
def book_spot(lot_id):
    if 'logged_in' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            flash('No available spots in this parking lot.', 'danger')
            return redirect(url_for('user_dashboard'))

        vehicle_number = request.form.get('vehicle_number', '').strip()
        vehicle_type = request.form.get('vehicle_type', '').strip()
        duration = request.form.get('duration', type=int)

        # Validate inputs
        if not vehicle_number or len(vehicle_number) > 20:
            raise ValueError("Invalid vehicle number.")
        valid_vehicle_types = ['Car', 'Truck', 'Bike', 'Scooty', 'Cycle']
        if vehicle_type not in valid_vehicle_types:
            raise ValueError("Invalid vehicle type selected.")
        if not duration or duration < 1:
            raise ValueError("Duration must be at least 1 hour.")

        # Calculate cost: price per hour * duration
        price_per_hour = lot.price
        parking_cost = price_per_hour * duration

        # Create reservation
        reservation = Reservation(
            user_id=int(session['user_id']),
            spot_id=available_spot.id,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            parking_timestamp=datetime.utcnow(),
            parking_cost=parking_cost,
            duration=duration,
            status='Active'
        )

        # Update spot status and occupied_spots
        available_spot.status = 'O'
        lot.occupied_spots += 1  # Increment the counter

        db.session.add(reservation)
        db.session.commit()

        flash(f'Spot booked successfully for {duration} hours! Estimated cost: ${parking_cost:.2f}', 'success')
    except ValueError as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error booking spot: {str(e)}', 'danger')

    return redirect(url_for('user_dashboard'))

@app.route('/debug/database')
def debug_database():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    users = User.query.all()
    parking_lots = ParkingLot.query.all()
    parking_spots = ParkingSpot.query.all()
    reservations = [{
        'id': res.id,
        'spot_id': res.spot_id,
        'user_id': res.user_id,
        'parking_timestamp': res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'leaving_timestamp': res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else None,
        'parking_cost': res.parking_cost,
        'vehicle_number': res.vehicle_number,
        'vehicle_type': res.vehicle_type,
        'duration': res.duration,
        'status': res.status
    } for res in Reservation.query.all()]

    return render_template('debug_database.html', 
                         users=users, 
                         parking_lots=parking_lots, 
                         parking_spots=parking_spots, 
                         reservations=reservations)

@app.route('/end_reservation/<int:reservation_id>', methods=['POST'])
def end_reservation(reservation_id):
    if 'logged_in' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        if reservation.user_id != int(session.get('user_id')):
            flash('You can only end your own reservations.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        if reservation.status != 'Active':
            flash('This reservation is already completed or cancelled.', 'warning')
            return redirect(url_for('user_dashboard'))
        
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        reservation.leaving_timestamp = datetime.utcnow()
        reservation.status = 'Completed'
        duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
        reservation.parking_cost = lot.price * duration
        
        spot.status = 'A'
        lot.occupied_spots -= 1  # Decrement the counter
        
        db.session.commit()
        flash('Reservation ended successfully! Final cost calculated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error ending reservation: {str(e)}", 'danger')
    return redirect(url_for('user_dashboard'))

@app.route('/update_vehicle_type/<int:reservation_id>', methods=['POST'])
def update_vehicle_type(reservation_id):
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        vehicle_type = request.form.get('vehicle_type', '').strip()
        valid_vehicle_types = ['Car', 'Truck', 'Bike', 'Scooty', 'Cycle']
        if vehicle_type not in valid_vehicle_types:
            raise ValueError("Invalid vehicle type selected.")
        
        reservation.vehicle_type = vehicle_type
        db.session.commit()
        flash(f'Vehicle type updated to {vehicle_type} for reservation {reservation_id}.', 'success')
    except ValueError as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating vehicle type: {str(e)}", 'danger')
    return redirect(url_for('dashboard'))

# Updated API Endpoints for Summary Page
@app.route('/api/stats/availability', methods=['GET'])
def get_availability_stats():
    if 'logged_in' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        lots = ParkingLot.query.all()
        total_available = sum(lot.maximum_number_of_spots - lot.occupied_spots for lot in lots)
        total_occupied = sum(lot.occupied_spots for lot in lots)
        
        return jsonify({
            'labels': ['Available', 'Occupied'],
            'data': [total_available, total_occupied],
            'backgroundColor': ['#90EE90', '#1E90FF']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/revenue', methods=['GET'])
def get_revenue_stats():
    if 'logged_in' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        lots = ParkingLot.query.all()
        labels = []
        data = []
        
        for lot in lots:
            reservations = db.session.query(Reservation)\
                .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)\
                .filter(ParkingSpot.lot_id == lot.id)\
                .all()
            total_revenue = sum(res.parking_cost for res in reservations)
            if total_revenue > 0:
                labels.append(lot.prime_location_name)
                data.append(total_revenue)
        
        return jsonify({
            'labels': labels,
            'data': data,
            'backgroundColor': ['#1E90FF', '#FFD700', '#90EE90', '#FF6347', '#BA55D3']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/peak_hours', methods=['GET'])
def get_peak_hours_stats():
    if 'logged_in' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        hour_counts = {i: 0 for i in range(24)}
        reservations = Reservation.query.filter_by(status='Active').all()
        
        for res in reservations:
            hour = res.parking_timestamp.hour
            hour_counts[hour] += 1
        
        labels = [f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}" for h in range(0, 24, 4)]
        data = [hour_counts[h] for h in range(0, 24, 4)]
        
        return jsonify({
            'labels': labels,
            'data': data,
            'backgroundColor': '#1E90FF'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/vehicle_types', methods=['GET'])
def get_vehicle_types_stats():
    if 'logged_in' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        vehicle_counts = db.session.query(
            Reservation.vehicle_type,
            db.func.count(Reservation.vehicle_type)
        ).filter(Reservation.status == 'Active')\
         .group_by(Reservation.vehicle_type).all()
        
        labels = []
        data = []
        colors = ['#FF6F61', '#6B7280', '#10B981', '#FBBF24', '#3B82F6']
        
        for vehicle_type, count in vehicle_counts:
            if count > 0:
                labels.append(vehicle_type)
                data.append(count)
        
        if not labels:
            labels = ['No Data']
            data = [0]
            colors = ['#FF6F61']
        
        return jsonify({
            'labels': labels,
            'data': data,
            'backgroundColor': colors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)