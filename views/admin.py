import streamlit as st
import utils
from datetime import date

def admin_panel():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Admin Panel</h2>", unsafe_allow_html=True)
    
    admin_tab = st.tabs(["Dashboard", "Manage Users", "Manage Classrooms", "All Reservations"])
    
    with admin_tab[0]:

        stats = utils.get_admin_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f'<div class="stat-card"><h3>{stats["users"]}</h3><p>Total Users</p></div>', unsafe_allow_html=True)
        with col2:
            # SQL'deki toplam oda sayısı
            st.markdown(f'<div class="stat-card"><h3>{len(st.session_state.classrooms)}</h3><p>Classrooms</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><h3>{stats["today_res"]}</h3><p>Today\'s Res.</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-card"><h3>{stats["noshow"]}</h3><p>No-Shows</p></div>', unsafe_allow_html=True)
        with col5:
            # En çok kullanılan sınıfı gösteren kart
            st.markdown(f'<div class="stat-card"><h3>★</h3><p>Most Popular:<br><b>{stats["popular_room"]}</b></p></div>', unsafe_allow_html=True)
    
    # --- MANAGE USERS ---
    with admin_tab[1]:
        st.subheader("All Users")
        
        # Modal state
        if "editing_user_email" not in st.session_state:
            st.session_state.editing_user_email = None
        
        if st.session_state.editing_user_email is None:
            # KULLANICI LİSTESİ
            for user in st.session_state.users:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.write(f"**{user['name']}** ({user['email']})")
                with col2:
                    st.write(f"Role: {user['role'].capitalize()}")
                with col3:
                    if user["role"] != "admin":
                        if st.button("Update", key=f"edit_user_{user['email']}", use_container_width=True):
                            st.session_state.editing_user_email = user['email']
                            st.rerun()
                with col4:
                    if st.button("Delete", key=f"del_user_{user['email']}", use_container_width=True):
                        success, msg = utils.delete_user(user['email'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            # GÜNCELLEME EKRANI
            editing_user = next((u for u in st.session_state.users if u['email'] == st.session_state.editing_user_email), None)
            
            st.markdown(f"<h4 style='color:{utils.PRIMARY_COLOR};'>Edit User: {editing_user['email']}</h4>", unsafe_allow_html=True)
            
            col_back, col_empty = st.columns([1, 4])
            with col_back:
                if st.button("← Back"):
                    st.session_state.editing_user_email = None
                    st.rerun()
            
            st.markdown("---")
            
            updated_name = st.text_input("Full Name", value=editing_user['name'])
            updated_password = st.text_input("Password", value=editing_user['password'], type="password")
            updated_role = st.selectbox("Role", ["student", "academician"], index=0 if editing_user['role'] == "student" else 1)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes", use_container_width=True, type="primary"):
                    success, msg = utils.update_user_profile(
                        st.session_state.editing_user_email, 
                        updated_name, 
                        updated_password, 
                        updated_role
                    )
                    if success:
                        st.success(msg)
                        st.session_state.editing_user_email = None
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.editing_user_email = None
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            new_email = st.text_input("Email")
            new_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["student", "academician", "admin"])
            
            if st.form_submit_button("Add User"):
                if new_email and new_name and new_password:
                    success, msg = utils.add_user_to_db(new_email, new_name, new_password, new_role)
                    if success:
                        st.success(msg)
                        # init_session_state verileri tazeleyeceği için listeye otomatik yansır
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill all fields")
    
    # --- MANAGE CLASSROOMS ---
    with admin_tab[2]:
        st.subheader("All Classrooms")
        
        # Modal state
        if "editing_class_id" not in st.session_state:
            st.session_state.editing_class_id = None
        
        if st.session_state.editing_class_id is None:
            # SINIFLARI LİSTELE
            for classroom in st.session_state.classrooms:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    status_indicator = "✓ Active" if classroom.get('is_active', True) else "✗ Inactive"
                    st.write(f"**{classroom['name']}** - {classroom['building']}, {classroom['floor']} [{status_indicator}]")
                with col2:
                    st.write(f"Cap: {classroom['capacity']}")
                with col3:
                    if st.button("Update", key=f"edit_class_{classroom['id']}", use_container_width=True):
                        st.session_state.editing_class_id = classroom['id']
                        st.rerun()
                with col4:
                    if st.button("Delete", key=f"del_class_{classroom['id']}", use_container_width=True):
                        success, msg = utils.delete_classroom(classroom['id'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            # GÜNCELLEME EKRANI
            editing_class = next((c for c in st.session_state.classrooms if c['id'] == st.session_state.editing_class_id), None)
            
            st.markdown(f"<h4 style='color:{utils.PRIMARY_COLOR};'>Edit Classroom: {editing_class['name']}</h4>", unsafe_allow_html=True)
            
            col_back, col_empty = st.columns([1, 4])
            with col_back:
                if st.button("← Back"):
                    st.session_state.editing_class_id = None
                    st.rerun()
            
            st.markdown("---")
            
            updated_name = st.text_input("Classroom Name", value=editing_class['name'])
            updated_building = st.text_input("Building", value=editing_class['building'])
            updated_floor = st.text_input("Floor", value=editing_class['floor'])
            updated_capacity = st.number_input("Capacity", min_value=1, value=editing_class['capacity'])
            
            # Aktif/Kapalı durumu
            is_active_options = ["Active", "Inactive"]
            current_status = "Active" if editing_class.get('is_active', True) else "Inactive"
            current_idx = 0 if current_status == "Active" else 1
            updated_status = st.selectbox("Status", is_active_options, index=current_idx)
            updated_is_active = (updated_status == "Active")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes", use_container_width=True, type="primary"):
                    success, msg = utils.update_classroom_details(
                        st.session_state.editing_class_id,
                        updated_name,
                        updated_capacity,
                        updated_is_active
                    )
                    if success:
                        st.success(msg)
                        st.session_state.editing_class_id = None
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.editing_class_id = None
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Add New Classroom")
        
        with st.form("add_classroom_form"):
            class_name = st.text_input("Classroom Name")
            class_building = st.text_input("Building")
            class_floor = st.text_input("Floor")
            class_capacity = st.number_input("Capacity", min_value=1, value=30)
            
            
            if st.form_submit_button("Add Classroom"):
                if class_name:
                    success, msg = utils.add_new_room(
                        room_name=class_name, 
                        capacity=class_capacity, 
                        features=f"{class_building}, {class_floor}"
                    )
                    
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill required fields")
    
    # --- ALL RESERVATIONS ---
    with admin_tab[3]:
        st.subheader("All Reservations")
        
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Cancelled", "Past"])
    
        all_res = utils.get_all_reservations()
        filtered = all_res
        
        if status_filter == "Active":
            filtered = [r for r in all_res if r["status"].lower() in ["active", "confirmed"] and r["date"] >= date.today()]
        elif status_filter == "Cancelled":
            filtered = [r for r in all_res if r["status"].lower() == "cancelled"]
        elif status_filter == "Past":
            filtered = [r for r in all_res if r["date"] < date.today()]
        
        if filtered:
            for reservation in filtered:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{reservation['classroom_name']}** - {reservation['date']}")
                    st.write(f"Time: {reservation['start_time']} - {reservation['end_time']}")
                    st.write(f"User: {reservation['user_name']} ({reservation['user_email']})")
                with col2:
                    status_color = "#28a745" if reservation["status"] == "active" else "#dc3545"
                    st.markdown(f"<span style='color:{status_color};'>{reservation['status'].capitalize()}</span>", unsafe_allow_html=True)
                with col3:
                    if reservation["status"] == "active":
                        if st.button("Cancel", key=f"admin_cancel_{reservation['id']}"):
                            for r in st.session_state.reservations:
                                if r["id"] == reservation["id"]:
                                    r["status"] = "cancelled"
                                    break
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info(f"No {status_filter.lower()} reservations found")
