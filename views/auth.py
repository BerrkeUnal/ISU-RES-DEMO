# Dosya Adı: views/auth.py
import streamlit as st
import utils
import base64

def get_img_as_base64(file):
    """Logoyu HTML içinde kullanabilmek için base64 formatına çevirir."""
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def login_page():
    # --- CSS TASARIMI ---
    st.markdown(f"""
    <style>
        /* Ortadaki kolonu (login kartı) şekillendir */
        div[data-testid="column"]:nth-of-type(2) > div {{
            background-color: white;
            padding: 2.5rem 3rem;
            border-radius: 20px;
            /* Koyu arka plan üzerinde daha belirgin gölge */
            box-shadow: 0 15px 35px rgba(0,0,0,0.25); 
            /* Kenarlığı kaldırdık, gölge yeterli */
            border: none; 
            text-align: center;
        }}
        
        /* Radio Buton Alanı */
        div[role="radiogroup"] {{
            background-color: #f9fbfc;
            padding: 12px 15px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            display: flex; justify-content: space-around; margin-bottom: 1rem;
        }}
        div[role="radiogroup"] label p {{
             font-size: 15px !important; font-weight: 500 !important; color: #333 !important;
        }}
        
        /* Input alanları */
        .stTextInput input {{ border-radius: 10px; border: 1px solid #ddd; padding: 10px; }}
        
        /* Demo bilgileri */
        .demo-info {{
            font-size: 0.85rem; color: #666; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;
        }}
    </style>
    """, unsafe_allow_html=True)

    # --- 1. LOGOYU SAYFAYA ORTALA ---
    img = get_img_as_base64("IsuRes Logo.png")
    if img:
        # Logoya biraz da gölge (drop-shadow) ekleyerek koyu zeminde patlamasını sağladık
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-top: 2rem; margin-bottom: 2rem;">
                <img src="data:image/png;base64,{img}" width="250" style="filter: drop-shadow(0 5px 15px rgba(0,0,0,0.2));">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align:center; color:white;'>IsuRes</h1>", unsafe_allow_html=True)

    # --- 2. GİRİŞ KARTI ---
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #666; margin-top: 5px; font-size: 1.1rem;">University Reservation System</h2>
            </div>
        """, unsafe_allow_html=True)

        # ROL SEÇİMİ
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        email = st.text_input("Email Address", placeholder="email@isures.edu")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        if st.button("Login", use_container_width=True, key="login_page_button"): 
            if email and password:
                user_found = utils.login_check(email, password) 
                
                if user_found:
                    # Oturum bilgilerini SQL'den gelen verilerle dolduruyoruz
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_found["user_id"] 
                    st.session_state.user_email = user_found["school_mail"]
                    st.session_state.user_name = f"{user_found['first_name']} {user_found['last_name']}"
                    st.session_state.user_role = user_found["role"]
                    st.rerun() # Sayfayı yenileyerek ana menüye yönlendir
                else:
                    st.error("Invalid email or password!")
            else:
                st.warning("Please fill in all fields.")

        # DEMO BİLGİLERİ
        st.markdown(f"""
        <div class="demo-info">
            <p style="margin-bottom:5px;"><strong>Demo Accounts:</strong></p>
            Admin: <code>berke.unal@istinye.edu.tr</code> / <code>Berke_Admin_2025!</code><br>
            Academician: <code>murat.aksoy@istinye.edu.tr</code> / <code>Murat_Academic_12</code><br>
            Student: <code>ebru.sahin@stu.istinye.edu.tr</code> / <code>Ebru_Pass_2025!</code>
        </div>
        """, unsafe_allow_html=True)
