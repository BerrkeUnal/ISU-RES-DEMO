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
        
        /* Sidebar içindeki tüm containerları beyaz yap */
        section[data-testid="stSidebar"] > div {{
            background-color: #FFFFFF !important;
        }}

        /* --- 3. SIDEBAR YAZILARI (MAVİ) --- */
        /* Sidebar içindeki her şeyi (p, h1, span, div) maviye boya */
        section[data-testid="stSidebar"] * {{
            color: {PRIMARY_COLOR} !important;
        }}
        
        /* Ama Buton içindeki yazılar BEYAZ kalsın (Yukarıdaki kuralı eziyoruz) */
        section[data-testid="stSidebar"] button * {{
            color: white !important;
        }}

        /* --- 4. BUTONLAR (KESİN ÇÖZÜM) --- */
        /* Hem Sidebar'daki Logout hem de Ana Ekrandaki butonlar */
        div.stButton > button {{
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }}
        
        /* Buton üzerine gelince */
        div.stButton > button:hover {{
            background-color: #005f7b !important; /* Daha koyu mavi */
            color: white !important;
        }}
        
        /* Butona tıklandığında (active) */
        div.stButton > button:active {{
            background-color: #004a61 !important;
            color: white !important;
        }}

        /* --- 5. DİĞER DÜZELTMELER --- */
        /* Option Menu arka planını temizle */
        iframe[title="streamlit_option_menu.option_menu"] {{
            background-color: transparent !important;
        }}

        .main-header {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #005f7b 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;
            text-align: center; 
        }}
        
        /* Header içindeki yazıları beyaz yap */
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
            {"id": 1, "name": "Room A101", "capacity": 30, "building": "Building A", "floor": "1st Floor"},
            {"id": 2, "name": "Room A102", "capacity": 25, "building": "Building A", "floor": "1st Floor"},
            {"id": 3, "name": "Room B201", "capacity": 40, "building": "Building B", "floor": "2nd Floor"},
            {"id": 4, "name": "Room B202", "capacity": 35, "building": "Building B", "floor": "2nd Floor"},
            {"id": 5, "name": "Lab C101", "capacity": 20, "building": "Building C", "floor": "1st Floor"},
            {"id": 6, "name": "Conference Room D", "capacity": 15, "building": "Building D", "floor": "Ground Floor"},
        ]
    
    if "reservations" not in st.session_state:
        st.session_state.reservations = []
    
    if "notifications" not in st.session_state:
        st.session_state.notifications = []

# --- VERİTABANI BAĞLANTISI ---

def get_db_connection():
   # Veritabanı bağlantısını kurar ve döner.
   # Tüm fonksiyonlar bu bağlantıyı kullanmalıdır.

    return mysql.connector.connect(
        user="root", 
        password="", 
        host="localhost", 
        database="Libapp" # SQL dosyasındaki DB ismi
    )

# --- YARDIMCI FONKSİYONLAR ---
def get_all_rooms():
    #Tüm odaları listeler (UI Classrooms sayfası için)
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
    #Belirli bir kullanıcının rezervasyonlarını getirir
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
    #Admin paneli için tüm kullanıcıları çeker
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, first_name, last_name, school_mail, role FROM Users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users

def check_penalty_status(user_id):

    # Kullanıcının son 24 saat içinde 'No-Show' (Gelmedi) cezası olup olmadığını kontrol eder.
    # Create reservation işleminden önce çağrılır.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Kullanıcının durumu 'No-Show' olan en son rezervasyonunu getir
    # SQL tablosuna uygun olarak 'Reservations', 'reserv_date' kullanıldı

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

        # Tarih farkını hesapla
        diff = today - penalty_date

        # Eğer fark 1 günden azsa (Dün veya bugün ceza almışsa)
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

    #Kullanıcı girişini doğrular.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Tablo adı SQL'de 'Users'
    query = "SELECT * FROM Users U WHERE U.school_mail=%s AND U.password=%s"
    cursor.execute(query, (input_email, input_password))
    user = cursor.fetchone()
    
    cursor.close()
    db.close()
    return user 

def get_username(target_user_id):

    # ID'si verilen kullanıcının adını ve soyadını getirir.

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

    # ID'si verilen kullanıcının mail adresini getirir.

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

   # Kullanıcının şifresini değiştirir.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Önce eski şifreyi kontrol et
    check_query = "SELECT U.password FROM Users AS U WHERE U.user_id=%s"
    cursor.execute(check_query, (user_id,))
    current_password_data = cursor.fetchone()

    # Şifre yanlışsa veya kullanıcı yoksa
    if not current_password_data or current_password_data['password'] != old_password:
        cursor.close()
        db.close()
        return False, "You entered your old password incorrectly!"

    # Yeni şifreyi güncelle
    update_query = "UPDATE Users SET password = %s WHERE user_id = %s"
    cursor.execute(update_query, (new_password, user_id))
    db.commit() # Değişikliği kaydet
    
    db.close()
    return True, "Your password changed successfully."

# --- REZERVASYON İŞLEMLERİ ---

def get_empty_slots_range(room_id, start_date, end_date):

    # Belirli bir tarih aralığı için odanın müsait saatlerini hesaplar.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 1. Oda aktif mi kontrolü
    status_query = "SELECT is_active, room_name FROM Rooms AS R WHERE room_id=%s"
    cursor.execute(status_query, (room_id,))
    room = cursor.fetchone()
    
    # Oda bulunamadıysa veya pasifse
    if not room:
        return "Room not found", None
    if not room['is_active']: # SQL'de boolean/tinyint döner (1 veya 0)
        return "Room is not active", room['room_name']
    
    # 2. Dolu saatleri çek (Tablo: Reservations, Sütun: reserv_date)
    busy_slots_query = """
        SELECT reserv_date, start_time, end_time 
        FROM Reservations 
        WHERE room_id=%s AND reserv_date BETWEEN %s AND %s
    """
    cursor.execute(busy_slots_query, (room_id, start_date, end_date))
    busy_appointments = cursor.fetchall()
    db.close()

    available_slots = []
    opening_hour = 7
    closing_hour = 20

    current_day = start_date
    while current_day <= end_date:
        daily_busy_hours = set()
        # O güne ait randevuları filtrele
        appointments_of_day = [r for r in busy_appointments if r['reserv_date'] == current_day]

        for appointment in appointments_of_day:
            start_seconds = appointment['start_time'].total_seconds()
            end_seconds = appointment['end_time'].total_seconds()

            # Saat aralığını doldur
            while start_seconds < end_seconds:
                hour_str = f"{int(start_seconds // 3600):02d}:00"
                daily_busy_hours.add(hour_str)
                start_seconds += 3600
                
        # Günün tüm saatlerini kontrol et, dolu değilse listeye ekle
        for hour_num in range(opening_hour, closing_hour):
            check_time = f"{hour_num:02d}:00"
            if check_time not in daily_busy_hours:
                available_slots.append({
                    "date": current_day,      
                    "time": check_time     
                })

        current_day += timedelta(days=1)
        
    return available_slots, room['room_name']

def create_reservation(user_id, room_id, reservation_date, start_time_str, end_time_str):

   # Yeni rezervasyon oluşturur. 
   # Ceza, Oda Durumu, Zaman ve Çakışma kontrolü yapar.

    
    # 1. Ceza Kontrolü (Penalty Check)
    is_penalized, penalty_msg = check_penalty_status(user_id)
    if is_penalized:
        return False, penalty_msg

    # 2. Zaman Formatı ve Mantık Kontrolü (Time Logic)
    time_format = "%H:%M"
    try:
        t1 = datetime.strptime(start_time_str, time_format)
        t2 = datetime.strptime(end_time_str, time_format)
    except ValueError:
        return False, "Invalid time format. Use HH:MM."

    # Bitiş saati başlangıçtan önce olamaz
    if t2 <= t1:
        return False, "End time must be later than start time."

    # Süre hesaplama (Maksimum 3 saat kuralı)
    duration = t2 - t1
    total_seconds = duration.total_seconds()

    if total_seconds > (3 * 3600):
        return False, "Reservation duration cannot exceed 3 hours."

    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 3. Oda Aktif mi?
        room_query = "SELECT is_active FROM Rooms WHERE room_id = %s"
        cursor.execute(room_query, (room_id,))
        room_data = cursor.fetchone()

        if not room_data:
            return False, "Room not found."
        # SQL dosyasında default true tanımlı, boolean kontrolü
        if not room_data['is_active']: 
            return False, "This room is currently out of service."

        # 4. Çakışma Kontrolü (Conflict Check)
        # Tablo: Reservations. İptal (Cancelled) veya Gelmedi (No-Show) ise çakışma sayılmaz.
        conflict_query = """
            SELECT COUNT(*) AS count
            FROM Reservations
            WHERE room_id = %s
              AND reserv_date = %s
              AND status NOT IN ('Cancelled', 'No-Show') 
              AND (
                  (start_time < %s AND end_time > %s)
              )
        """
        # Mantık: Yeni randevu mevcut randevunun içine düşüyor mu?
        cursor.execute(conflict_query, (room_id, reservation_date, end_time_str, start_time_str))
        result = cursor.fetchone()

        if result['count'] > 0:
            return False, "The selected time slot is already booked."

        # 5. Veritabanına Kayıt (Insert Data)
        # SQL tablosuna uygun sütun isimleri: reserv_date, check_in_time vs.
        insert_query = """
            INSERT INTO Reservations 
            (user_id, room_id, reserv_date, start_time, end_time, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'Confirmed', NOW())
        """
        # Not: is_checked_in sütunu SQL dosyasında yoktu, bunun yerine check_in_time null kontrolü yapılır.
        # Bu yüzden check_in_time'ı null bırakıyoruz, kullanıcı gelince dolacak.
        
        cursor.execute(insert_query, (user_id, room_id, reservation_date, start_time_str, end_time_str))
        db.commit()
        
        return True, "Your reservation has been successfully created."

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False, "A database error occurred. Please try again later."
        
    except Exception as e:
        print(f"General Error: {e}")
        return False, f"An error occurred: {str(e)}"

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def check_in_reservation(reservation_id):

    # Kullanıcı 'Check-in' butonuna basınca çalışır.
    # Zaman kısıtlaması: Başlangıçtan 5 dk önce ile 15 dk sonra arası.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Tablo: Reservations, ID: reserv_id
    query = "SELECT reserv_date, start_time, status FROM Reservations WHERE reserv_id = %s"
    cursor.execute(query, (reservation_id,))
    reservation = cursor.fetchone()

    if not reservation:
        cursor.close()
        db.close()
        return False, "Reservation not found."

    # --- Zaman Hesaplaması ---
    now = datetime.now()
    today_date = now.date()

    if reservation['reserv_date'] != today_date:
        cursor.close()
        db.close()
        return False, "You can only check-in on the actual reservation day."

    start_time_db = reservation['start_time']

    if isinstance(start_time_db, timedelta):
        start_datetime = datetime.combine(today_date, (datetime.min + start_time_db).time())
    else:
        start_datetime = datetime.combine(today_date, start_time_db)

    allowed_start = start_datetime - timedelta(minutes=5)
    allowed_end = start_datetime + timedelta(minutes=15)

    if not (allowed_start <= now <= allowed_end):
        time_format = "%H:%M"
        cursor.close()
        db.close()
        return False, f"Check-in only available between {allowed_start.strftime(time_format)} and {allowed_end.strftime(time_format)}."

    # Güncelleme: check_in_time sütununa şu anki zamanı basıyoruz
    try:
        update_query = "UPDATE Reservations SET check_in_time = NOW() WHERE reserv_id = %s"
        cursor.execute(update_query, (reservation_id,))
        db.commit()
        success = True
        message = "Check-in successful! Have a good study session."
    except Exception as e:
        success = False
        message = f"Error: {e}"

    cursor.close()
    db.close()
    return success, message

def update_noshow_status():

   # Süresi geçmiş ve Check-in yapılmamış rezervasyonları 'No-Show' olarak işaretler.
   # Arka planda çalışması gereken sistem fonksiyonu.

    db = get_db_connection()
    cursor = db.cursor()
    
    # check_in_time IS NULL ise kullanıcı gelmemiştir.
    query = """
            UPDATE Reservations 
            SET status = 'No-Show' 
            WHERE status = 'Confirmed' 
              AND check_in_time IS NULL 
              AND start_time < (NOW() - INTERVAL 15 MINUTE) 
              AND reserv_date <= CURDATE()
            """
            
    cursor.execute(query)
    db.commit()
    
    affected_rows = cursor.rowcount
    cursor.close()
    db.close()
    return affected_rows

def cancel_reservation(reservation_id, user_id):

    # Kullanıcının kendi rezervasyonunu iptal etmesini sağlar.
    # Sadece rezervasyon saati gelmemişse iptal edilebilir.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. Rezervasyonu kontrol et (Başkası iptal edemesin diye user_id kontrolü şart)
    query = "SELECT start_time, reserv_date, status FROM Reservations WHERE reserv_id=%s AND user_id=%s"
    cursor.execute(query, (reservation_id, user_id))
    rezerv = cursor.fetchone()

    if not rezerv:
        cursor.close()
        db.close()
        return False, "Reservation not found or unauthorized."

    # 2. Zaman geçmiş mi?
    now = datetime.now()
    rezerv_start = datetime.combine(rezerv['reserv_date'], (datetime.min + rezerv['start_time']).time())
    
    if now >= rezerv_start:
        cursor.close()
        db.close()
        return False, "You cannot cancel a reservation that has already started."

    # 3. İptal İşlemi
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

def override_reservation(academic_user_id, room_id, reservation_date, start_time_str, end_time_str):

    # SADECE AKADEMİSYENLER İÇİN:
    # Seçilen saatte öğrenci varsa iptal eder (Override) ve akademisyeni yerleştirir.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. Kullanıcı gerçekten Akademisyen mi?
    role_query = "SELECT role FROM Users WHERE user_id = %s"
    cursor.execute(role_query, (academic_user_id,))
    user_data = cursor.fetchone()

    # SQL tablosunda role enum veya varchar olabilir, kontrol edelim
    # role değerinin 'akademisyen' veya 'Academic' olarak kayıtlı olduğunu varsayıyoruz.
    if not user_data or user_data['role'].lower() not in ['akademisyen', 'academic']:
        cursor.close()
        db.close()
        return False, "Only Academicians can use the override feature."

    try:
        # 2. O saatteki Mevcut Rezervasyonu Bul (Çakışan)
        conflict_query = """
            SELECT reserv_id, user_id 
            FROM Reservations
            WHERE room_id = %s 
              AND reserv_date = %s
              AND status = 'Confirmed'
              AND (
                  (start_time < %s AND end_time > %s)
              )
            LIMIT 1
        """
        cursor.execute(conflict_query, (room_id, reservation_date, end_time_str, start_time_str))
        conflict = cursor.fetchone()

        # Eğer çakışma varsa, o kişiyi iptal et
        if conflict:
            # Çakışan kişi de Akademisyen ise ezemez!
            role_check_q = "SELECT role FROM Users WHERE user_id = %s"
            cursor.execute(role_check_q, (conflict['user_id'],))
            conflict_user_role = cursor.fetchone()
            
            if conflict_user_role['role'].lower() in ['akademisyen', 'academic']:
                 cursor.close()
                 db.close()
                 return False, "You cannot override another Academician's reservation."

            # Öğrenciyse İptal Et
            cancel_q = """
                UPDATE Reservations 
                SET status='Cancelled', cancellation_reason='Academic Priority Override' 
                WHERE reserv_id = %s
            """
            cursor.execute(cancel_q, (conflict['reserv_id'],))
            
            # (Opsiyonel) Bildirim Tablosuna ekle
            notif_q = "INSERT INTO notifications (user_id, message) VALUES (%s, %s)"
            cursor.execute(notif_q, (conflict['user_id'], "Your reservation was cancelled due to Academic Priority."))

        # 3. Yeni Rezervasyonu Oluştur (Akademisyen İçin)
        insert_q = """
            INSERT INTO Reservations 
            (user_id, room_id, reserv_date, start_time, end_time, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'Confirmed', NOW())
        """
        cursor.execute(insert_q, (academic_user_id, room_id, reservation_date, start_time_str, end_time_str))
        db.commit()
        
        cursor.close()
        db.close()
        return True, "Reservation created successfully (Priority Used)."

    except Exception as e:
        if db: db.rollback() # Hata olursa işlemi geri al
        if cursor: cursor.close()
        if db: db.close()
        return False, f"System Error: {str(e)}"
    
# --- ADMİN İŞLEMLERİ ---

def get_admin_stats():

   # Admin paneli dashboard'u için özet sayıları döner.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    stats = {}
    
    # 1. Toplam Kullanıcı Sayısı
    cursor.execute("SELECT COUNT(*) as total_users FROM Users")
    stats['users'] = cursor.fetchone()['total_users']
    
    # 2. Bugünün Rezervasyon Sayısı
    cursor.execute("SELECT COUNT(*) as today_res FROM Reservations WHERE reserv_date = CURDATE()")
    stats['today_res'] = cursor.fetchone()['today_res']
    
    # 3. 'No-Show' (Gelmeyen) Oranı
    cursor.execute("SELECT COUNT(*) as noshow FROM Reservations WHERE status = 'No-Show'")
    stats['noshow'] = cursor.fetchone()['noshow']
    
    # 4. En Popüler Oda (Hangi oda daha çok kiralanmış?)
    popular_q = """
        SELECT R.room_name, COUNT(RES.reserv_id) as count 
        FROM Reservations RES
        JOIN Rooms R ON RES.room_id = R.room_id
        GROUP BY R.room_name
        ORDER BY count DESC LIMIT 1
    """
    cursor.execute(popular_q)
    pop_room = cursor.fetchone()
    stats['popular_room'] = pop_room['room_name'] if pop_room else "No Data"
    
    cursor.close()
    db.close()
    return stats

def get_all_reservations_log():
    
   # Geçmişten bugüne tüm hareketleri (Kim, Hangi odayı, Ne zaman, Durumu ne) çeker.

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT 
            RES.reserv_id,
            U.first_name, 
            U.last_name, 
            U.role,
            R.room_name, 
            RES.reserv_date, 
            RES.start_time, 
            RES.end_time, 
            RES.status
        FROM Reservations RES
        JOIN Users U ON RES.user_id = U.user_id
        JOIN Rooms R ON RES.room_id = R.room_id
        ORDER BY RES.reserv_date DESC, RES.start_time DESC
    """
    cursor.execute(query)
    logs = cursor.fetchall()
    
    cursor.close()
    db.close()
    return logs

def toggle_room_status(room_id, new_status):

   # Odayı aktife veya pasife çeker.
   # new_status: 1 (Aktif) veya 0 (Pasif/Bakımda)

    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        query = "UPDATE Rooms SET is_active = %s WHERE room_id = %s"
        cursor.execute(query, (new_status, room_id))
        db.commit()
        success = True
        msg = f"Room status updated to {'Active' if new_status else 'Out of Order'}."
    except Exception as e:
        success = False
        msg = f"Error: {str(e)}"
        
    cursor.close()
    db.close()
    return success, msg

def add_new_room(room_name, capacity, features):

   # Sisteme yeni bir çalışma odası ekler.

    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # is_active varsayılan olarak 1 (True) gider
        query = """
            INSERT INTO Rooms (room_name, type, capacity, features, is_active)
            VALUES (%s, 'Study Room', %s, %s, 1)
        """
        cursor.execute(query, (room_name, capacity, features))
        db.commit()
        success = True
        msg = f"Room '{room_name}' added successfully."
    except Exception as e:
        success = False
        msg = f"Error: {str(e)}"
        
    cursor.close()
    db.close()
    return success, msg