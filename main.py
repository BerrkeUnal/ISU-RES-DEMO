import streamlit as st
from streamlit_option_menu import option_menu
import utils

# Diğer dosyaları import ediyoruz
from views import auth, admin, user

st.set_page_config(
    page_title="IsuRes - Reservation System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR ---  
# --- SIDEBAR ---  
def sidebar_menu():
    with st.sidebar:
        try:
            st.image("IsuRes Logo.png", use_container_width=True)
        except:
            pass 
        
        user_name = st.session_state.get("user_name", "Kullanıcı")
        user_role = st.session_state.get("user_role", "student")

        st.markdown(f"<p style='text-align:center; color:#007f9b;'>Welcome, {user_name}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#007f9b; opacity:0.8;'>Role: {user_role.capitalize()}</p>", unsafe_allow_html=True)
        
        # --- MENÜ AYARLARI GÜNCELLENDİ ---
        if user_role == "admin":
            # ADMIN MENÜSÜ: "Reservations" buradan KALDIRILDI.
            # Admin artık sadece Sınıfları ve Admin Panelini görür.
            menu_options = ["Classrooms", "Admin Panel"]
            icons = ["building", "gear"]
        else:
            # STANDART MENÜ: Öğrenci ve Akademisyenler için hepsi açık.
            menu_options = ["Classrooms", "Make Reservation", "Reservations", "Notifications"]
            icons = ["building", "calendar-plus", "calendar-check", "bell"]
        
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "transparent"
                },
                "icon": {
                    "color": "#007f9b", 
                    "font-size": "18px"
                },
                "nav-link": {
                    "color": "#333333", 
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#f0f2f6" 
                },
                "nav-link-selected": {
                    "background-color": "#007f9b", 
                    "color": "white", 
                    "font-weight": "bold",
                },
            }
        )
        
        st.markdown("---")
        # Logout butonu
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.user_role = ""
            st.rerun()
        
        return selected

def main():
    # 1. Temel Ayarları Yükle
    utils.init_session_state()
    utils.load_css()
    
    # 2. Giriş Yapıldıysa Arka Plan Kontrollerini Yap
    if st.session_state.logged_in:
        utils.check_and_create_reminders()
        utils.auto_cancel_expired_reservations()
    
    # 3. Yönlendirme (Routing) Mantığı
    if not st.session_state.logged_in:
        auth.login_page()
    else:
        selected_page = sidebar_menu()
        
        if selected_page == "Classrooms":
            user.classrooms_page()
            
        elif selected_page == "Reservations":
            # Admin artık menüde bunu görmüyor ama kod güvenliği için burada kalsa da sorun olmaz.
            user.reservations_page()
            
        elif selected_page == "Make Reservation":
            # Sadece Öğrenci ve Akademisyen erişebilir
            if st.session_state.user_role in ["student", "academician"]:
                user.make_reservation_page()
            else:
                st.error("Bu sayfaya erişim yetkiniz yok.")
            
        elif selected_page == "Notifications":
            user.notifications_page()
            
        elif selected_page == "Admin Panel":
            # Sadece Admin girebilir
            if st.session_state.user_role == "admin":
                admin.admin_panel()
            else:
                st.error("You are not authorized to view this page.")

if __name__ == "__main__":
    main()