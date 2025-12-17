import mysql.connector
import streamlit as st
from datetime import datetime, date, timedelta

# --- RENK SABİTLERİ ---
PRIMARY_COLOR = "#007f9b"
WHITE = "#ffffff"

# --- CSS YÜKLEME ---
def load_css():
    st.markdown(f"""
    <style>
        /* --- 1. GENEL AYARLAR --- */
        .stApp {{
            background-color: {WHITE};
        }}

        /* --- 2. SIDEBAR AYARLARI (BEYAZ ZEMİN) --- */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid #e0e0e0;
        }}
        
        section[data-testid="stSidebar"] > div {{
            background-color: #FFFFFF !important;
        }}

        /* --- 3. SIDEBAR YAZILARI (MAVİ) --- */
        section[data-testid="stSidebar"] * {{
            color: {PRIMARY_COLOR} !important;
        }}
        
        section[data-testid="stSidebar"] button * {{
            color: white !important;
        }}

        /* --- 4. BUTONLAR (HATALI KISIM DÜZELTİLDİ) --- */
        div.stButton > button {{
            background-color: {PRIMARY_COLOR} !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
        }}

        /* Buton içindeki metni zorla BEYAZ yap */
        div.stButton > button p, 
        div.stButton > button div, 
        div.stButton > button span {{
            color: white !important;
            font-weight: bold !important;
        }}
        
        div.stButton > button:hover {{
            background-color: #005f7b !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }}

        /* Primary tipindeki butonlar için ekstra garanti */
        div.stButton > button[kind="primary"] p {{
            color: white !important;
        }}

        /* --- 5. DİĞER AYARLAR --- */
        iframe[title="streamlit_option_menu.option_menu"] {{
            background-color: transparent !important;
        }}

        .main-header {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #005f7b 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;
            text-align: center; 
        }}
        
        .main-header h1, .main-header h2, .main-header p {{
            color: white !important;
        }}

        .reservation-card, .classroom-card {{
            background: white; padding: 1.5rem; border-radius: 10px;
            margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            color: #333 !important;
        }}
        
        .reservation-card h4, .classroom-card h4 {{
            color: {PRIMARY_COLOR} !important;
        }}

        .reservation-card p, .classroom-card p {{
            color: #333 !important;
        }}

        /* --- 6. NOTİFİCATİON KARTLARI --- */
        .notification-card {{
            background-color: #f5f5f5;
            border-left: 4px solid #ddd;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            color: #333 !important;
        }}

        .notification-card strong {{
            color: {PRIMARY_COLOR} !important;
        }}

        .notification-card p {{
            color: #333 !important;
            margin: 0.3rem 0 !important;
        }}

        .notification-card small {{
            color: #666 !important;
        }}

        .notification-unread {{
            background-color: #e3f2fd !important;
            border-left-color: {PRIMARY_COLOR} !important;
        }}

        /* --- 7. STAT CARDS (ADMIN) --- */
        .stat-card {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #005f7b 100%);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            color: white !important;
        }}

        .stat-card h3 {{
            color: white !important;
            margin: 0 !important;
            font-size: 2.5rem !important;
        }}

        .stat-card p {{
            color: rgba(255,255,255,0.9) !important;
            margin: 0.5rem 0 0 0 !important;
        }}

        /* --- 8. TABS --- */
        .stTabs [data-baseweb="tab-list"] button {{
            color: {PRIMARY_COLOR} !important;
        }}

        .stTabs [role="tabpanel"] {{
            color: #333 !important;
        }}

        /* --- 9. FORM ELEMENTS --- */
        .stTextInput label,
        .stSelectbox label,
        .stNumberInput label,
        .stDateInput label {{
            color: #333 !important;
        }}

        .stTextInput input,
        .stSelectbox select,
        .stNumberInput input,
        .stDateInput input {{
            border: 1px solid #ddd !important;
            border-radius: 6px !important;
            color: #333 !important;
        }}

        /* --- 10. MARKDOWN --- */
        h1, h2, h3, h4, h5, h6 {{
            color: #333 !important;
        }}

        p {{
            color: #333 !important;
        }}

    </style>
    """, unsafe_allow_html=True)


# --- SESSION STATE ---
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""
    
    if "users" not in st.session_state:
        st.session_state.users = [
            {"email": "admin@isures.edu", "password": "admin123", "name": "System Administrator", "role": "admin"},
            {"email": "academician@isures.edu", "password": "academician123", "name": "Dr. John Smith", "role": "academician"},
            {"email": "student@isures.edu", "password": "student123", "name": "Jane Doe", "role": "student"},
        ]
    
    if "classrooms" not in st.session_state:
        st.session_state.classrooms = [
            {"id": 1, "name": "Room A101", "capacity": 30, "building": "Building A", "floor": "1st Floor", "is_active": True},
            {"id": 2, "name": "Room A102", "capacity": 25, "building": "Building A", "floor": "1st Floor", "is_active": True},
            {"id": 3, "name": "Room B201", "capacity": 40, "building": "Building B", "floor": "2nd Floor", "is_active": True},
            {"id": 4, "name": "Room B202", "capacity": 35, "building": "Building B", "floor": "2nd Floor", "is_active": True},
            {"id": 5, "name": "Lab C101", "capacity": 20, "building": "Building C", "floor": "1st Floor", "is_active": True},
            {"id": 6, "name": "Conference Room D", "capacity": 15, "building": "Building D", "floor": "Ground Floor", "is_active": False},
        ]
    
    if "reservations" not in st.session_state:
        st.session_state.reservations = []
    
    if "notifications" not in st.session_state:
        st.session_state.notifications = []

# --- VERİTABANI BAĞLANTISI ---
def get_db_connection():
    return mysql.connector.connect(
        user="root", 
        password="", 
        host="localhost", 
        database="Libapp"
    )

# --- YARDIMCI FONKSİYONLAR ---
def get_all_rooms():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms WHERE is_active = 1")
    rooms = cursor.fetchall()
    cursor.close()
    db.close()
    return rooms

def add_notification(title, message):
    st.session_state.notifications.insert(0, {
        "id": len(st.session_state.notifications) + 1,
        "user_email": st.session_state.user_email,
        "title": title,
        "message": message,
        "is_read": False,
        "created_at": datetime.now()
    })

def get_time_slots():
    return [
        {"label": "08:00 - 11:00", "start": "08:00", "end": "11:00"},
        {"label": "11:00 - 14:00", "start": "11:00", "end": "14:00"},
        {"label": "14:00 - 17:00", "start": "14:00", "end": "17:00"},
        {"label": "17:00 - 20:00", "start": "17:00", "end": "20:00"},
    ]

def get_reservations_by_user(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT R.reserv_id, R.reserv_date, R.start_time, R.end_time, 
               R.status, R.check_in_time, RM.room_name 
        FROM Reservations R
        JOIN Rooms RM ON R.room_id = RM.room_id
        WHERE R.user_id = %s
        ORDER BY R.reserv_date DESC, R.start_time DESC
    """
    cursor.execute(query, (user_id,))
    reservs = cursor.fetchall()
    cursor.close()
    db.close()
    return reservs

def get_all_users():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, first_name, last_name, school_mail, role FROM Users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users

def check_penalty_status(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
            SELECT reserv_date, start_time
            FROM Reservations
            WHERE user_id = %s 
              AND status = 'No-Show'
            ORDER BY reserv_date DESC, start_time DESC LIMIT 1
            """
    cursor.execute(query, (user_id,))
    last_no_show = cursor.fetchone()

    cursor.close()
    db.close()

    if last_no_show:
        today = datetime.now().date()
        penalty_date = last_no_show['reserv_date']
        diff = today - penalty_date

        if diff.days < 1:
            return True, "You are restricted from making new reservations for 24 hours due to a previous No-Show."

    return False, None

def can_check_in(reservation):
    if reservation["date"] != date.today():
        return False, "Check-in is only available on the reservation date"
    
    now = datetime.now()
    start_hour = int(reservation["start_time"].split(":")[0])
    
    check_in_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0) - timedelta(minutes=5)
    check_in_end = now.replace(hour=start_hour, minute=15, second=0, microsecond=0)
    
    if now < check_in_start:
        return False, f"Check-in opens at {check_in_start.strftime('%H:%M')}"
    elif now > check_in_end:
        return False, "Check-in window has expired"
    else:
        return True, "You can check in now"

def check_and_create_reminders():
    now = datetime.now()
    for reservation in st.session_state.reservations:
        if reservation["status"] == "active" and reservation["date"] == date.today():
            start_hour = int(reservation["start_time"].split(":")[0])
            reservation_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            time_until_start = (reservation_start - now).total_seconds() / 60
            
            reminder_key = f"reminder_{reservation['id']}"
            if 55 <= time_until_start <= 65 and reminder_key not in st.session_state:
                st.session_state[reminder_key] = True
                add_notification(
                    "Reservation Reminder",
                    f"Reminder: Your reservation for {reservation['classroom_name']} starts in 1 hour at {reservation['start_time']}. Don't forget to check in!"
                )

def auto_cancel_expired_reservations():
    now = datetime.now()
    for reservation in st.session_state.reservations:
        if reservation["status"] == "active" and reservation["date"] == date.today():
            if not reservation.get("checked_in", False):
                start_hour = int(reservation["start_time"].split(":")[0])
                start_minute = int(reservation["start_time"].split(":")[1])
                reservation_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                check_in_deadline = reservation_start + timedelta(minutes=15)
                
                if now >= reservation_start and now > check_in_deadline:
                    cancel_key = f"auto_cancelled_{reservation['id']}"
                    if cancel_key not in st.session_state:
                        st.session_state[cancel_key] = True
                        reservation["status"] = "auto_cancelled"
                        add_notification(
                            "Reservation Auto-Cancelled",
                            f"Your reservation for {reservation['classroom_name']} at {reservation['start_time']} was cancelled because you did not check in within 15 minutes."
                        )

# --- KULLANICI İŞLEMLERİ ---
def login_check(input_email, input_password):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM Users U WHERE U.school_mail=%s AND U.password=%s"
    cursor.execute(query, (input_email, input_password))
    user = cursor.fetchone()
    
    cursor.close()
    db.close()
    return user 

def get_username(target_user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    query = """
            SELECT
                U.first_name,
                U.last_name
            FROM Users AS U WHERE user_id = %s
            """
    cursor.execute(query, (target_user_id,))
    result = cursor.fetchone()

    cursor.close()
    db.close()

    if result:
        full_name = f"{result['first_name']} {result['last_name']}"
        return full_name
    else:
        return "Unknown User"

def get_mail_address(target_user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT U.school_mail FROM Users AS U WHERE U.user_id=%s"
    cursor.execute(query, (target_user_id,))
    result_mail = cursor.fetchone()
    
    cursor.close()
    db.close()

    if result_mail:
        return result_mail
    else:
        return "No email addresses found"

def password_change(user_id, old_password, new_password):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    check_query = "SELECT U.password FROM Users AS U WHERE U.user_id=%s"
    cursor.execute(check_query, (user_id,))
    current_password_data = cursor.fetchone()

    if not current_password_data or current_password_data['password'] != old_password:
        cursor.close()
        db.close()
        return False, "You entered your old password incorrectly!"

    update_query = "UPDATE Users SET password = %s WHERE user_id = %s"
    cursor.execute(update_query, (new_password, user_id))
    db.commit()
    
    db.close()
    return True, "Your password changed successfully."

# --- REZERVASYON İŞLEMLERİ ---
def cancel_reservation(reservation_id, user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT start_time, reserv_date, status FROM Reservations WHERE reserv_id=%s AND user_id=%s"
    cursor.execute(query, (reservation_id, user_id))
    rezerv = cursor.fetchone()

    if not rezerv:
        cursor.close()
        db.close()
        return False, "Reservation not found or unauthorized."

    now = datetime.now()
    rezerv_start = datetime.combine(rezerv['reserv_date'], (datetime.min + rezerv['start_time']).time())
    
    if now >= rezerv_start:
        cursor.close()
        db.close()
        return False, "You cannot cancel a reservation that has already started."

    try:
        update_q = "UPDATE Reservations SET status='Cancelled', cancellation_reason='User Request' WHERE reserv_id=%s"
        cursor.execute(update_q, (reservation_id,))
        db.commit()
        msg = "Reservation cancelled successfully."
        success = True
    except Exception as e:
        msg = f"Error: {e}"
        success = False

    cursor.close()
    db.close()
    return success, msg
