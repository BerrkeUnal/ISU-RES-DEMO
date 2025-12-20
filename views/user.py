import streamlit as st
from datetime import date
import utils

def classrooms_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Available Classrooms</h2>", unsafe_allow_html=True)
    
    available_rooms = []
    non_available_rooms = []

    # 1. SINIFLARI AYIRALIM
    for classroom in st.session_state.classrooms:
        today_reservations = [r for r in st.session_state.reservations 
                            if r["classroom_id"] == classroom['id'] 
                            and r["date"] == date.today() 
                            and r["status"].lower() in ["active", "confirmed"]]
        
        is_busy_today = len(today_reservations) > 0
        is_active = classroom.get('is_active', 1) == 1 

        # Sınıf objesine aktiflik bilgisini saklıyoruz ki aşağıda butonu ona göre çizelim
        classroom['is_active_status'] = is_active # Bu satırı ekledik

        if is_active and not is_busy_today:
            available_rooms.append(classroom)
        else:
            classroom['reason'] = "Booked" if is_busy_today else "Maintenance / Closed"
            non_available_rooms.append(classroom)

    # Modal state kontrolü
    if "selected_classroom_for_reservation" not in st.session_state:
        st.session_state.selected_classroom_for_reservation = None
    
    if st.session_state.selected_classroom_for_reservation is None:
        # --- SINIF LİSTELEME EKRANI ---
        st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Select a classroom to view available time slots</p>", unsafe_allow_html=True)
        
        # Available sınıfları
        st.subheader("Available")
        if available_rooms:
            col1, col2 = st.columns(2)
            for idx, classroom in enumerate(available_rooms):
                with col1 if idx % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="border: 2px solid green; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin-top:0;'>{classroom['name']}</h4>
                        <p style='margin: 0.3rem 0;'><strong>Capacity:</strong> {classroom['capacity']} people</p>
                        <p style='margin: 0.5rem 0; color:green; font-weight:bold;'>Available</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View Details", key=f"avail_{classroom['id']}", use_container_width=True):
                        st.session_state.selected_classroom_for_reservation = classroom
                        st.rerun()
        else:
            st.info("No classrooms available at the moment.")
            
        # Non-Available sınıfları
        st.subheader("Non-Available")
        if non_available_rooms:
            col1, col2 = st.columns(2)
            for idx, classroom in enumerate(non_available_rooms):
                with col1 if idx % 2 == 0 else col2:
                    reason_text = classroom.get('reason', 'Non-Available')
                    
                    # Kırmızı kart tasarımı
                    st.markdown(f"""
                    <div style="border: 2px solid red; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; background-color: #fff5f5;">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin-top:0;'>{classroom['name']}</h4>
                        <p style='margin: 0.3rem 0;'><strong>Capacity:</strong> {classroom['capacity']} people</p>
                        <p style='margin: 0.5rem 0; color:red; font-weight:bold;'>{reason_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # KRİTİK NOKTA: Sadece sınıf aktifse (yani sadece doluysa) buton görünsün
                    if classroom['is_active_status']:
                        if st.button(f"View Schedule", key=f"nonavail_{classroom['id']}", use_container_width=True):
                            st.session_state.selected_classroom_for_reservation = classroom
                            st.rerun()
                    else:
                        # Sınıf pasifse buton yerine küçük bir bilgilendirme yazısı koyabiliriz
                        st.caption("⚠️ This room is not accepting reservations.")
            
    else:
        # --- REZERVASYON DETAY EKRANI  ---
        selected_class = st.session_state.selected_classroom_for_reservation
        is_admin = st.session_state.user_role == "admin"
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"<h3 style='color:{utils.PRIMARY_COLOR};'>{selected_class['name']}</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state.selected_classroom_for_reservation = None
                st.rerun()
        
        st.markdown("---")
        
        # --- SAAT SEÇİMİ VE GÖRÜNTÜLEME ---
        st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Select a Date and View Available Time Slots</p>", unsafe_allow_html=True)
        reservation_date = st.date_input("Select Date", value=date.today(), min_value=date.today())

        # 1. Dolu saatleri veritabanından çekiyoruz
        busy_hours = set()
        try:
            db = utils.get_db_connection() #
            cursor = db.cursor(dictionary=True) #
            
            # Sadece aktif olan ve bu sınıfa ait rezervasyonları getir
            # SQL tablonuzda status 'Active' veya 'Confirmed' olabilir, her ikisini de kontrol ediyoruz
            query = """
                SELECT start_time, end_time 
                FROM Reservations 
                WHERE room_id = %s 
                AND reserv_date = %s 
                AND status IN ('Active', 'Confirmed', 'active')
            """
            cursor.execute(query, (selected_class['id'], reservation_date))
            db_reservations = cursor.fetchall()
            
            for res in db_reservations:
                # SQL'den gelen time/timedelta objelerini saate çeviriyoruz
                # Örn: 09:00:00 -> 9
                start_time_str = str(res["start_time"])
                end_time_str = str(res["end_time"])
                
                start_hour = int(start_time_str.split(":")[0])
                end_hour = int(end_time_str.split(":")[0])
                
                for h in range(start_hour, end_hour):
                    busy_hours.add(f"{h:02d}:00")
                    
            cursor.close()
            db.close()
        except Exception as e:
            st.error(f"Error fetching availability: {e}")

        # 2. Görselleştirme Kısmı
        all_hours = [h for h in range(7, 20)] # Sayı olarak tutuyoruz
        st.markdown(f"<p style='font-size:0.9rem; color:#666;'>Green = Available | Red = Occupied</p>", unsafe_allow_html=True)

        hours_cols = st.columns(4)
        for idx, h_num in enumerate(all_hours):
            col_idx = idx % 4
            with hours_cols[col_idx]:
                hour_label = f"{h_num:02d}:00"
                next_hour_label = f"{(h_num + 1):02d}:00"
                
                is_busy = hour_label in busy_hours
                color = "red" if is_busy else "green"
                
                # Sadece saati değil, aralığı yazıyoruz: "10:00 - 11:00" gibi
                st.markdown(f"""
                <div style="background:{color}; color:white; padding:8px; border-radius:6px; text-align:center; font-size:0.8rem; font-weight:bold; margin:4px 0; opacity:{'0.6' if is_busy else '1'};">
                    {hour_label} - {next_hour_label}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        
        # --- REZERVASYON FORMU / ADMİN BİLGİ ALANI ---
        if not is_admin:
            # Standart Kullanıcılar İçin Rezervasyon Formu
            st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Make Your Reservation</p>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                start_hour = st.selectbox(
                    "Start Time",
                    options=[f"{h:02d}:00" for h in range(7, 19)],
                    key=f"start_time_{selected_class['id']}"
                )
            
            with col2:
                end_hour = st.selectbox(
                    "End Time",
                    options=[f"{h:02d}:00" for h in range(8, 20)],
                    key=f"end_time_{selected_class['id']}"
                )
            
            purpose = st.text_input("Purpose (optional)")
            
            st.markdown(f"""
            <div style='background:#e8f4f8; padding:1rem; border-radius:8px; margin:1rem 0;'>
                <p style='color:{utils.PRIMARY_COLOR}; margin:0; font-weight:bold;'>Important Rules:</p>
                <ul style='color:#333; margin:0.5rem 0;'>
                    <li>Maximum reservation duration: 3 hours</li>
                    <li>Check-in window: 5 minutes before to 15 minutes after start time</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Confirm Reservation", use_container_width=True, type="primary"):
                # Kullanıcının rolüne göre hangi fonksiyonun çalışacağına karar veriyoruz
                if st.session_state.user_role == "academician":
                    # AKADEMİSYEN: Mevcut rezervasyonu ezebilen (override) fonksiyonu çağır
                    success, message = utils.override_reservation(
                        academic_user_id=st.session_state.user_id,
                        room_id=selected_class['id'],
                        reservation_date=reservation_date,
                        start_time_str=start_hour,
                        end_time_str=end_hour
                    )
                else:
                    # ÖĞRENCİ: Çakışma varsa hata veren normal fonksiyonu çağır
                    success, message = utils.create_reservation(
                        user_id=st.session_state.user_id,
                        room_id=selected_class['id'],
                        reservation_date=reservation_date,
                        start_time_str=start_hour,
                        end_time_str=end_hour
                    )

                if success:
                    utils.add_notification(
                        "Reservation Confirmed", 
                        f"Your reservation for {selected_class['name']} has been confirmed."
                    )
                    st.success(message)
                    st.session_state.selected_classroom_for_reservation = None
                    st.rerun()
                else:
                    # Eğer bir akademisyen başka bir akademisyeni ezmeye çalışırsa 
                    # utils.override_reservation içindeki hata mesajı burada görünür.
                    st.error(message)

def reservations_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>My Reservations</h2>", unsafe_allow_html=True)
    
    user_reservations = utils.get_reservations_by_user(st.session_state.user_email)

    tab1, tab2 = st.tabs(["Active Reservations", "Past Reservations"])
    
    
    with tab1:
        active = [r for r in user_reservations if r["status"].lower() in ["active", "confirmed"] and r["date"] >= date.today()]
        
        if active:
            for reservation in active:
                checked_in = reservation.get("checked_in", False)
                can_do_checkin, checkin_message = utils.can_check_in(reservation)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    checkin_status = "Checked In" if checked_in else "Not Checked In"
                    checkin_color = "#28a745" if checked_in else "#ffc107"

                    start_h = int(reservation['start_time'].split(":")[0])
                    
                    st.markdown(f"""
                    <div class="reservation-card">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin:0;'>{reservation['classroom_name']}</h4>
                        <p><strong>Date:</strong> {reservation['date']}</p>
                        <p><strong>Time:</strong> {reservation['start_time']} - {reservation['end_time']}</p>
                        <p><strong>Purpose:</strong> {reservation['purpose']}</p>
                        <p><strong>Check-in Status:</strong> <span style='color:{checkin_color};'>{checkin_status}</span></p>
                        <p style='font-size:0.85rem; color:#666;'>Check-in window: {start_h-1:02d}:55 - {start_h:02d}:15</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if not checked_in:
                        if can_do_checkin:
                            if st.button("Check In", key=f"checkin_{reservation['id']}", type="primary"):
                                success, msg = utils.check_in_reservation(reservation['id'])
                                
                                if success:
                                    utils.add_notification(
                                        "Check-in Successful",
                                        f"You have successfully checked in for {reservation['classroom_name']} at {reservation['start_time']}."
                                    )
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            st.info(checkin_message)
                    
                    if st.button("Cancel", key=f"cancel_{reservation['id']}"):
                        success, msg = utils.cancel_reservation(reservation['id'], st.session_state.user_id)
                        
                        if success:
                            utils.add_notification(
                                "Reservation Cancelled",
                                f"Your reservation for {reservation['classroom_name']} on {reservation['date']} has been cancelled."
                            )
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No active reservations")
    
    with tab2:
        past = [r for r in user_reservations if r["date"] < date.today()]
        
        if past:
            for reservation in past:
                # Duruma göre renk ve durum metni belirle
                if reservation["status"] == "cancelled":
                    status_color = "#dc3545"
                    status_text = "Cancelled"
                elif reservation["status"] == "auto_cancelled":
                    status_color = "#dc3545"
                    status_text = "Auto-Cancelled (No Check-in)"
                else:
                    status_color = "#28a745"
                    status_text = "Completed"
                
                st.markdown(f"""
                <div class="reservation-card" style="opacity: 0.8;">
                    <h4 style='color:{utils.PRIMARY_COLOR}; margin:0;'>{reservation['classroom_name']}</h4>
                    <p><strong>Date:</strong> {reservation['date']}</p>
                    <p><strong>Time:</strong> {reservation['start_time']} - {reservation['end_time']}</p>
                    <p><strong>Status:</strong> <span style='color:{status_color};'>{status_text}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No past reservations")

def notifications_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Notifications</h2>", unsafe_allow_html=True)
    
    user_notifications = [n for n in st.session_state.notifications if n["user_email"] == st.session_state.user_email]
    
    if user_notifications:
        unread_count = sum(1 for n in user_notifications if not n["is_read"])
        if unread_count > 0:
            st.markdown(f"<p style='color:{utils.PRIMARY_COLOR};'><strong>{unread_count} unread notification(s)</strong></p>", unsafe_allow_html=True)
            
            if st.button("Mark All as Read"):
                for n in st.session_state.notifications:
                    if n["user_email"] == st.session_state.user_email:
                        n["is_read"] = True
                st.rerun()
        
        for notification in user_notifications:
            is_unread = not notification["is_read"]
            bg_color = "#e3f2fd" if is_unread else "#f5f5f5"
            border_color = utils.PRIMARY_COLOR if is_unread else "#ddd"
            
            st.markdown(f"""
            <div style="background-color:{bg_color}; border-left: 4px solid {border_color}; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                <strong style='color:{utils.PRIMARY_COLOR};'>{notification['title']}</strong>
                <p style='margin:0.5rem 0; color:#333;'>{notification['message']}</p>
                <small style='color:#666;'>{notification['created_at'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notifications")
