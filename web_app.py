import streamlit as st
from supabase import create_client, Client
import secrets_config
import time
from datetime import datetime
import pandas as pd

# Sayfa Ayarlari
st.set_page_config(
    page_title="Sağlık Asistanım",
    page_icon="💧",
    layout="centered"
)

# Supabase Baglantisi
@st.cache_resource
def init_connection():
    # 1. Once Streamlit Secrets'a bak (Bulut icin)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        pass
        
    # 2. Bulamazsa yerel dosyaya bak (PC icin)
    try:
        import secrets_config
        return create_client(secrets_config.SUPABASE_URL, secrets_config.SUPABASE_KEY)
    except ImportError:
        st.error("Veritabanı bağlantı bilgileri bulunamadı (Secrets veya config dosyası yok).")
        return None

supabase = init_connection()

# Veri Yukleme
def get_data():
    try:
        response = supabase.table("user_settings").select("data").eq("id", 1).execute()
        if response.data:
            return response.data[0]["data"]
        return None
    except Exception as e:
        st.error(f"Baglanti hatasi: {e}")
        return None

# Veri Kaydetme
def save_data(data):
    try:
        supabase.table("user_settings").update({"data": data}).eq("id", 1).execute()
    except Exception as e:
        st.error(f"Kayit hatasi: {e}")

# Styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 3rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Kişisel Sağlık Asistanım 💧")

# Verileri Cek
if 'data' not in st.session_state:
    st.session_state.data = get_data()

data = st.session_state.data

if data:
    # --- SU TAKIBI ---
    st.header("Su Durumu")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("İçilen", f"{data['su_icilen']} ml")
    with col2:
        st.metric("Hedef", f"{data['su_hedef']} ml")
        
    # Progress Bar
    progress = data['su_icilen'] / data['su_hedef']
    if progress > 1.0: progress = 1.0
    st.progress(progress)
    
    # Ekleme Butonlari
    col_add1, col_add2 = st.columns(2)
    with col_add1:
        if st.button("+200 ml Ekle 💧"):
            data["su_icilen"] += 200
            data["son_su_zamani"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["hatirlatici_referans"] = time.time() # Hatirlaticiyi sifirla
            save_data(data)
            st.rerun()
            
    with col_add2:
        if st.button("+500 ml Ekle 🥤"):
            data["su_icilen"] += 500
            data["son_su_zamani"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["hatirlatici_referans"] = time.time()
            save_data(data)
            st.rerun()

    # --- VITAMINLER ---
    st.header("Vitaminler 💊")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if not data["vitaminler"]:
        st.info("Henüz vitamin eklenmemiş.")
    
    # Vitamin Listesi
    for i, vit in enumerate(data["vitaminler"]):
        with st.container():
            col_v1, col_v2 = st.columns([3, 1])
            is_taken = vit.get("son_alinma") == today_str
            
            with col_v1:
                st.subheader(f"{vit['isim']} ({vit['saat']})")
                
            with col_v2:
                # Checkbox yerine buton kullanalim, mobilde daha rahat
                if is_taken:
                    st.success("Alındı ✅")
                else:
                    if st.button("Aldım", key=f"take_{i}"):
                        data["vitaminler"][i]["son_alinma"] = today_str
                        save_data(data)
                        st.rerun()

    # Sayfayi yenileme butonu (Manuel sync)
    st.divider()
    if st.button("🔄 Durumu Güncelle"):
        st.session_state.data = get_data()
        st.rerun()

else:
    st.warning("Veriler yüklenemedi. Lütfen internet bağlantınızı kontrol edin.")
