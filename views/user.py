import streamlit as st
from datetime import datetime, date
import utils

def classrooms_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Available Classrooms</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    for idx, classroom in enumerate(st.session_state.classrooms):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"""
            <div class="classroom-card">
                <h4 style='color:{utils.PRIMARY_COLOR}; margin:0;'>{classroom['name']}</h4>
                <p style='margin:0.5rem 0;'><strong>Building:</strong> {classroom['building']}</p>
                <p style='margin:0.5rem 0;'><strong>Floor:</strong> {classroom['floor']}</p>
                <p style='margin:0.5rem 0;'><strong>Capacity:</strong> {classroom['capacity']} seats</p>
            </div>
            """, unsafe_allow_html=True)

def make_reservation_page():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Make a Reservation</h2>", unsafe_allow_html=True)
    
    classroom_options = {f"{c['name']} ({c['building']})": c['id'] for c in st.session_state.classrooms}
    time_slots = utils.get_time_slots()
    
    with st.form("reservation_form"):
        selected_classroom = st.selectbox("Select Classroom", list(classroom_options.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            reservation_date = st.date_input("Date", min_value=date.today())
        with col2:
            slot_labels = [slot["label"] for slot in time_slots]
            selected_slot = st.selectbox("Time Slot (3 hours)", slot_labels)
        
        purpose = st.text_input("Purpose (optional)")
        
        st.markdown(f"""
        <div style='background:#e8f4f8; padding:1rem; border-radius:8px; margin:1rem 0;'>
            <p style='color:{utils.PRIMARY_COLOR}; margin:0;'><strong>Important Rules:</strong></p>
            <ul style='color:#333; margin:0.5rem 0;'>
                <li>You will receive a reminder notification 1 hour before your reservation</li>
                <li>Check-in window: 5 minutes before to 15 minutes after start time</li>
                <li>If you don't check in within 15 minutes, your reservation will be automatically cancelled</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Make Reservation", use_container_width=True)
        
        if submitted:
            classroom_id = classroom_options[selected_classroom]
            classroom_name = selected_classroom.split(" (")[0]
            
            selected_time = next(slot for slot in time_slots if slot["label"] == selected_slot)
            start_time = selected_time["start"]
            end_time = selected_time["end"]
            
            conflict = False
            for res in st.session_state.reservations:
                if (res["classroom_id"] == classroom_id and 
                    res["date"] == reservation_date and 
                    res["status"] == "active" and
                    res["start_time"] == start_time):
                    conflict = True
                    break
            
            if conflict:
                st.error("This time slot is already booked. Please choose a different time.")
            else:
                new_reservation = {
                    "id": len(st.session_state.reservations) + 1,
                    "user_email": st.session_state.user_email,
                    "user_name": st.session_state.user_name,
                    "classroom_id": classroom_id,
                    "classroom_name": classroom_name,
                    "date": reservation_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "purpose": purpose or "General use",
                    "status": "active",
                    "checked_in": False,
                    "created_at": datetime.now()
                }
                st.session_state.reservations.append(new_reservation)
                
                utils.add_notification(
                    "Reservation Confirmed",
                    f"Your reservation for {classroom_name} on {reservation_date} from {start_time} to {end_time} has been confirmed. Remember to check in within 15 minutes of start time!"
                )
                
                st.success("Reservation created successfully!")
                st.rerun()

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
        past = [r for r in user_reservations if r["status"] != "active" or r["date"] < date.today()]
        
        if past:
            for reservation in past:
                if reservation["status"] == "completed" or reservation.get("checked_in", False):
                    status_color = "#28a745"
                    status_text = "Completed"
                elif reservation["status"] == "auto_cancelled":
                    status_color = "#dc3545"
                    status_text = "Auto-Cancelled (No Check-in)"
                elif reservation["status"] == "cancelled":
                    status_color = "#dc3545"
                    status_text = "Cancelled"
                else:
                    status_color = "#666"
                    status_text = reservation["status"].capitalize()
                
                st.markdown(f"""
                <div class="reservation-card" style="opacity: 0.7;">
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
            card_class = "notification-card notification-unread" if not notification["is_read"] else "notification-card"
            st.markdown(f"""
            <div class="{card_class}">
                <strong>{notification['title']}</strong>
                <p style='margin:0.3rem 0;'>{notification['message']}</p>
                <small style='color:#666;'>{notification['created_at'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notifications")