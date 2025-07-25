# view_db.py
from app import app, db, User, ParkingLot, ParkingSpot, Reservation  # Import the app and db from app.py

# Use the Flask app context to access the database
with app.app_context():
    print("Users:")
    for user in User.query.all():
        print(user.id, user.email, user.fullname, user.address, user.pincode, user.role)

    print("\nParking Lots:")
    for lot in ParkingLot.query.all():
        print(lot.id, lot.prime_location_name, lot.price, lot.address, lot.pincode, lot.maximum_number_of_spots, lot.occupied_spots)

    print("\nParking Spots:")
    for spot in ParkingSpot.query.all():
        print(spot.id, spot.lot_id, spot.status)

    print("\nReservations:")
    for res in Reservation.query.all():
        leaving_timestamp = res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else 'N/A'
        print(res.id, res.spot_id, res.user_id, res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'), leaving_timestamp, res.parking_cost, res.vehicle_number, res.status)