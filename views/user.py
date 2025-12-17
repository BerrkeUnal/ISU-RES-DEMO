import streamlit as st
from datetime import datetime, date
import utils

def classrooms_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Available Classrooms</h2>", unsafe_allow_html=True)
    
    # Modal state kontrolü
    if "selected_classroom_for_reservation" not in st.session_state:
        st.session_state.selected_classroom_for_reservation = None
    
    if st.session_state.selected_classroom_for_reservation is None:
        # --- SINIF LİSTELEME EKRANI (Aynı Kalıyor) ---
        st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Select a classroom to view available time slots</p>", unsafe_allow_html=True)
        
        # Available sınıfları
        st.subheader("Available")
        col1, col2 = st.columns(2)
        col_idx = 0
        
        for classroom in st.session_state.classrooms:
            today_reservations = [r for r in st.session_state.reservations 
                                 if r["classroom_id"] == classroom['id'] 
                                 and r["date"] == date.today() 
                                 and r["status"] == "active"]
            
            is_busy_today = len(today_reservations) > 0
            
            if not is_busy_today:
                with col1 if col_idx % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="border: 2px solid green; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin-top:0;'>{classroom['name']}</h4>
                        <p style='margin: 0.3rem 0;'><strong>Building:</strong> {classroom['building']}</p>
                        <p style='margin: 0.3rem 0;'><strong>Floor:</strong> {classroom['floor']}</p>
                        <p style='margin: 0.3rem 0;'><strong>Capacity:</strong> {classroom['capacity']} people</p>
                        <p style='margin: 0.5rem 0; color:green; font-weight:bold;'>Available</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"View Details", key=f"select_class_{classroom['id']}", use_container_width=True):
                        st.session_state.selected_classroom_for_reservation = classroom
                        st.rerun()
                col_idx += 1
        
        # Non-Available sınıfları
        st.subheader("Non-Available")
        col1, col2 = st.columns(2)
        col_idx = 0
        
        for classroom in st.session_state.classrooms:
            today_reservations = [r for r in st.session_state.reservations 
                                 if r["classroom_id"] == classroom['id'] 
                                 and r["date"] == date.today() 
                                 and r["status"] == "active"]
            
            is_busy_today = len(today_reservations) > 0
            
            if is_busy_today:
                with col1 if col_idx % 2 == 0 else col2:
                    st.markdown(f"""
                    <div style="border: 2px solid red; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin-top:0;'>{classroom['name']}</h4>
                        <p style='margin: 0.3rem 0;'><strong>Building:</strong> {classroom['building']}</p>
                        <p style='margin: 0.3rem 0;'><strong>Floor:</strong> {classroom['floor']}</p>
                        <p style='margin: 0.3rem 0;'><strong>Capacity:</strong> {classroom['capacity']} people</p>
                        <p style='margin: 0.5rem 0; color:red; font-weight:bold;'>Non-Available</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"View Details", key=f"select_class_{classroom['id']}", use_container_width=True):
                        st.session_state.selected_classroom_for_reservation = classroom
                        st.rerun()
                col_idx += 1
    
    else:
        # --- REZERVASYON DETAY EKRANI (Admin Kontrolü Buradadır) ---
        selected_class = st.session_state.selected_classroom_for_reservation
        is_admin = st.session_state.user_role == "admin" # Admin kontrolü eklendi
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"<h3 style='color:{utils.PRIMARY_COLOR};'>{selected_class['name']}</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state.selected_classroom_for_reservation = None
                st.rerun()
        
        st.markdown("---")
        
        # SAAT SEÇİMİ VE GÖRÜNTÜLEME
        st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Select a Date and View Available Time Slots</p>", unsafe_allow_html=True)
        reservation_date = st.date_input("Select Date", value=date.today(), min_value=date.today())
        
        # Dolu saatleri hesapla (Eski Fonksiyonelliği Korumaktadır)
        busy_hours = set()
        for res in st.session_state.reservations:
            if res["classroom_id"] == selected_class['id'] and res["date"] == reservation_date and res["status"] == "active":
                start_hour = int(res["start_time"].split(":")[0])
                end_hour = int(res["end_time"].split(":")[0])
                for h in range(start_hour, end_hour):
                    busy_hours.add(f"{h:02d}:00")
        
        all_hours = [f"{h:02d}:00" for h in range(7, 20)]
        st.markdown(f"<p style='font-size:0.9rem; color:#666;'>Green = Available | Red = Occupied</p>", unsafe_allow_html=True)
        
        hours_cols = st.columns(4)
        for idx, hour in enumerate(all_hours):
            col_idx = idx % 4
            with hours_cols[col_idx]:
                is_busy = hour in busy_hours
                color = "red" if is_busy else "green"
                # Admin için butonlar etkisizmiş gibi görünür
                st.markdown(f"""
                <div style="background:{color}; color:white; padding:8px; border-radius:6px; text-align:center; font-weight:bold; margin:4px 0; opacity:{'0.6' if is_busy else '1'};">
                    {hour}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- REZERVASYON FORMU / ADMİN BİLGİ ALANI ---
        if not is_admin:
            # Standart Kullanıcılar İçin Rezervasyon Formu (Mevcut haliyle korundu)
            st.markdown(f"<p style='color:{utils.PRIMARY_COLOR}; font-weight:bold;'>Make Your Reservation</p>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                start_hour = st.selectbox(
                    "Start Time",
                    options=[f"{h:02d}:00" for h in range(7, 20)],
                    key=f"start_time_{selected_class['id']}"
                )
            
            with col2:
                end_hour = st.selectbox(
                    "End Time",
                    options=[f"{h:02d}:00" for h in range(7, 20)],
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
                try:
                    start_h = int(start_hour.split(":")[0])
                    end_h = int(end_hour.split(":")[0])
                    
                    if end_h <= start_h:
                        st.error("End time must be later than start time")
                    elif end_h - start_h > 3:
                        st.error("Reservation duration cannot exceed 3 hours")
                    else:
                        conflict = False
                        for res in st.session_state.reservations:
                            if (res["classroom_id"] == selected_class['id'] and 
                                res["date"] == reservation_date and 
                                res["status"] == "active"):
                                res_start = int(res["start_time"].split(":")[0])
                                res_end = int(res["end_time"].split(":")[0])
                                if not (end_h <= res_start or start_h >= res_end):
                                    conflict = True
                                    break
                        
                        if conflict:
                            st.error("This time slot conflicts with existing reservation")
                        else:
                            new_reservation = {
                                "id": len(st.session_state.reservations) + 1,
                                "user_email": st.session_state.user_email,
                                "user_name": st.session_state.user_name,
                                "classroom_id": selected_class['id'],
                                "classroom_name": selected_class['name'],
                                "date": reservation_date,
                                "start_time": start_hour,
                                "end_time": end_hour,
                                "purpose": purpose or "General use",
                                "status": "active",
                                "checked_in": False,
                                "created_at": datetime.now()
                            }
                            st.session_state.reservations.append(new_reservation)
                            utils.add_notification("Reservation Confirmed", f"Your reservation for {selected_class['name']} has been confirmed.")
                            st.success("Reservation created successfully!")
                            st.session_state.selected_classroom_for_reservation = None
                            st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            # Admin İçin Bilgilendirme Notu
            st.info("💡 **Admin View Only:** You can see all occupancy details, but cannot create a reservation from this screen. To manage classrooms or users, please go to the **Admin Panel**.")

def reservations_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>My Reservations</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Active Reservations", "Past Reservations"])
    
    user_reservations = [r for r in st.session_state.reservations if r["user_email"] == st.session_state.user_email]
    
    with tab1:
        active = [r for r in user_reservations if r["status"] == "active" and r["date"] >= date.today()]
        
        if active:
            for reservation in active:
                checked_in = reservation.get("checked_in", False)
                can_do_checkin, checkin_message = utils.can_check_in(reservation)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    checkin_status = "Checked In" if checked_in else "Not Checked In"
                    checkin_color = "#28a745" if checked_in else "#ffc107"
                    
                    st.markdown(f"""
                    <div class="reservation-card">
                        <h4 style='color:{utils.PRIMARY_COLOR}; margin:0;'>{reservation['classroom_name']}</h4>
                        <p><strong>Date:</strong> {reservation['date']}</p>
                        <p><strong>Time:</strong> {reservation['start_time']} - {reservation['end_time']}</p>
                        <p><strong>Purpose:</strong> {reservation['purpose']}</p>
                        <p><strong>Check-in Status:</strong> <span style='color:{checkin_color};'>{checkin_status}</span></p>
                        <p style='font-size:0.85rem; color:#666;'>Check-in window: {int(reservation['start_time'][:2])-1:02d}:55 - {reservation['start_time'][:2]}:15</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if not checked_in:
                        if can_do_checkin:
                            if st.button("Check In", key=f"checkin_{reservation['id']}", type="primary"):
                                for r in st.session_state.reservations:
                                    if r["id"] == reservation["id"]:
                                        r["checked_in"] = True
                                        break
                                
                                utils.add_notification(
                                    "Check-in Successful",
                                    f"You have successfully checked in for {reservation['classroom_name']} at {reservation['start_time']}."
                                )
                                
                                st.success("Checked in successfully!")
                                st.rerun()
                        else:
                            st.info(checkin_message)
                    
                    if st.button("Cancel", key=f"cancel_{reservation['id']}"):
                        for r in st.session_state.reservations:
                            if r["id"] == reservation["id"]:
                                r["status"] = "cancelled"
                                break
                        
                        utils.add_notification(
                            "Reservation Cancelled",
                            f"Your reservation for {reservation['classroom_name']} on {reservation['date']} has been cancelled."
                        )
                        
                        st.success("Reservation cancelled")
                        st.rerun()
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
