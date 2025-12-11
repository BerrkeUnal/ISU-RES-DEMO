import streamlit as st
import utils

def admin_panel():
    st.markdown(f"<h2 style='color:{utils.PRIMARY_COLOR};'>Admin Panel</h2>", unsafe_allow_html=True)
    
    admin_tab = st.tabs(["Dashboard", "Manage Users", "Manage Classrooms", "All Reservations"])
    
    with admin_tab[0]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{len(st.session_state.users)}</h3>
                <p>Total Users</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{len(st.session_state.classrooms)}</h3>
                <p>Classrooms</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{len(st.session_state.reservations)}</h3>
                <p>Total Reservations</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            active_count = len([r for r in st.session_state.reservations if r["status"] == "active"])
            st.markdown(f"""
            <div class="stat-card">
                <h3>{active_count}</h3>
                <p>Active Reservations</p>
            </div>
            """, unsafe_allow_html=True)
    
    with admin_tab[1]:
        st.subheader("All Users")
        
        for user in st.session_state.users:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{user['name']}** ({user['email']})")
            with col2:
                st.write(f"Role: {user['role'].capitalize()}")
            with col3:
                if user["role"] != "admin":
                    if st.button("Delete", key=f"del_user_{user['email']}"):
                        st.session_state.users = [u for u in st.session_state.users if u["email"] != user["email"]]
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
                    existing = [u for u in st.session_state.users if u["email"] == new_email]
                    if existing:
                        st.error("Email already exists")
                    else:
                        st.session_state.users.append({
                            "email": new_email,
                            "name": new_name,
                            "password": new_password,
                            "role": new_role
                        })
                        st.success("User added successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill all fields")
    
    with admin_tab[2]:
        st.subheader("All Classrooms")
        
        for classroom in st.session_state.classrooms:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{classroom['name']}** - {classroom['building']}, {classroom['floor']}")
            with col2:
                st.write(f"Capacity: {classroom['capacity']}")
            with col3:
                if st.button("Delete", key=f"del_class_{classroom['id']}"):
                    st.session_state.classrooms = [c for c in st.session_state.classrooms if c["id"] != classroom["id"]]
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Add New Classroom")
        
        with st.form("add_classroom_form"):
            class_name = st.text_input("Classroom Name")
            class_building = st.text_input("Building")
            class_floor = st.text_input("Floor")
            class_capacity = st.number_input("Capacity", min_value=1, value=30)
            
            if st.form_submit_button("Add Classroom"):
                if class_name and class_building:
                    new_id = max([c["id"] for c in st.session_state.classrooms], default=0) + 1
                    st.session_state.classrooms.append({
                        "id": new_id,
                        "name": class_name,
                        "building": class_building,
                        "floor": class_floor,
                        "capacity": class_capacity
                    })
                    st.success("Classroom added successfully!")
                    st.rerun()
                else:
                    st.warning("Please fill required fields")
    
    with admin_tab[3]:
        st.subheader("All Reservations")
        
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Cancelled"])
        
        filtered = st.session_state.reservations
        if status_filter != "All":
            filtered = [r for r in filtered if r["status"] == status_filter.lower()]
        
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