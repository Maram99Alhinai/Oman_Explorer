from app.services.db_service import db, User, Preference, TravelDestination
from sqlalchemy.exc import IntegrityError, OperationalError




def save_user_info(wa_id, name=None, age=None, gender=None, state=None, travel_style=None):
    """
    Save or update user information in the database.
    
    Args:
    wa_id (str): WhatsApp ID of the user (required).
    name (str): Name of the user (optional).
    age (int): Age of the user (optional).
    gender (str): Gender of the user (optional).
    state (str): State of residence (optional).
    travel_style (str): Travel style preference (optional).
    
    Returns:
    bool: True if successful, False otherwise.
    """
    print("Save or update user information in the database.")
    try:
        user = User.query.get(wa_id)
        
        if user is None:
            user = User(phone_number=wa_id)
            db.session.add(user)
        
        if name:
            user.name = name
        else:
            user.name = None
        
        if age:
            user.age = age
        else:
            user.age = None
        
        if gender:
            user.gender = gender
        else:
            user.gender = None
        
        if state:
            user.state = state
        else:
            user.state = None
        
        if travel_style:
            user.travel_style = travel_style
        else:
            user.travel_style = None
        
        db.session.commit()
        return True
    
    except IntegrityError as e:
        print(f"IntegrityError: {e}")
        db.session.rollback()
        return False
    
    except OperationalError as e:
        print(f"OperationalError: {e}")
        db.session.rollback()
        return False
    
    except Exception as e:
        print(f"Unexpected Error: {e}")
        db.session.rollback()
        return False

def save_user_preference(wa_id, destination_name, style, tags):
    user = User.query.get(wa_id)
    if user is None:
        return  # Handle error: user not found

    destination = TravelDestination.query.filter_by(destination_name=destination_name).first()
    if destination is None:
        destination = TravelDestination(destination_name=destination_name, location="Unknown", style=style, tags=tags)
        db.session.add(destination)
        db.session.flush()  # This will assign an ID to the new destination

    preference = Preference.query.filter_by(user_id=wa_id, destination_id=destination.destination_id).first()
    if preference is None:
        preference = Preference(user_id=wa_id, destination_id=destination.destination_id, style=style, tags=tags)
        db.session.add(preference)
    else:
        preference.style = style
        preference.tags = tags

    db.session.commit()
