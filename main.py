import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات وقاعدة البيانات (مرنة)
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STORAGE_PATH = os.path.join(PROJECT_ROOT, "ScienceTubeData")
VIDEOS_DIR = os.path.join(STORAGE_PATH, "videos")
DB_PATH = os.path.join(STORAGE_PATH, "science_tube_v16.db")

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # الحقول PRIMARY KEY تمنع التكرار تلقائياً على مستوى قاعدة البيانات
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, path TEXT, 
                  author TEXT, category TEXT, likes INTEGER DEFAULT 0, views INTEGER DEFAULT 0)''')
    c.execute('CREATE TABLE IF NOT EXISTS comments (v_id INTEGER, user TEXT, text TEXT)')
    conn.commit()
    return conn

conn = init_db()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🎨 2. تصميم الشعار (الميكروسكوب في المنتصف)
# ==========================================
st.set_page_config(page_title="Science Tube", page_icon="🔬", layout="wide")

st.markdown("""
    <style>
    .main-logo-container { display: flex; justify-content: center; padding: 20px 0; }
    .youtube-style-box {
        background: linear-gradient(180deg, #FF4B4B 0%, #CC0000 100%);
        padding: 10px 30px; border-radius: 20px; display: flex; align-items: center; gap: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4); border: 2px solid #FF0000;
    }
    .logo-text { color: white; font-family: 'Arial Black', sans-serif; font-size: 40px; font-weight: 900; margin: 0; }
    .micro-img { font-size: 50px; }
    </style>
    
    <div class="main-logo-container">
        <div class="youtube-style-box">
            <span class="logo-text">Science</span>
            <span class="micro-img">🔬</span>
            <span class="logo-text">Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# الأقسام
all_cats = ["الكل", "البرمجة", "الفيزياء", "الكيمياء", "الطب", "الفضاء", "الذكاء الاصطناعي"]

# إدارة الحالة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

# أزرار التنقل
t_col1, t_col2 = st.columns([5, 1])
with t_col1:
    if st.button("🏠 الرئيسية"): st.session_state.page = 'home'; st.rerun()
with t_col2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 دخول الناشرين"
    if st.button(label, use_container_width=True): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# 📊 3. منطق الصفحة الرئيسية والرفع
# ==========================================
if st.session_state.page == 'home':
    st.header("📺 الفيديوهات العلمية")
    vids = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    for v in vids:
        with st.container(border=True):
            st.subheader(v[1])
            st.video(v[2])
            st.write(f"✍️ الناشر: {v[3]} | 📂 القسم: {v[4]}")

elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 دخول", "📝 حساب جديد"])
        with tab1:
            u = st.text_input("الاسم")
            p = st.text_input("الباسورد", type="password")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user: st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("خطأ في البيانات")
        with tab2:
            reg_u = st.text_input("اسم جديد")
            reg_p = st.text_input("باسورد جديد", type="password")
            if st.button("تسجيل"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                    conn.commit(); st.success("تم التسجيل!")
                except: st.error("هذا الاسم موجود مسبقاً!")
    else:
        st.write(f"### أهلاً {st.session_state.user} 🔬")
        if st.button("🚪 خروج"): st.session_state.logged_in = False; st.rerun()
        
        st.divider()
        v_t = st.text_input("عنوان الفيديو العلمي (يجب أن يكون فريداً)")
        v_c = st.selectbox("القسم", all_cats[1:])
        v_f = st.file_uploader("ملف الفيديو", type=["mp4"])

        if st.button("فحص ونشر الفيديو"):
            if v_t and v_f:
                try:
                    # ميزة فريدة: استخدام hash لاسم الملف لمنع تكرار نفس الملف الفيزيائي
                    video_filename = f"{v_t}_{v_f.name}"
                    path = os.path.join(VIDEOS_DIR, video_filename)
                    with open(path, "wb") as f: f.write(v_f.getbuffer())
                    
                    conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)",
                                 (v_t, path, st.session_state.user, v_c))
                    conn.commit()
                    st.success("✅ تم النشر بنجاح!")
                except sqlite3.IntegrityError:
                    st.error("⚠️ هذا العنوان مستخدم مسبقاً، اختر عنواناً آخر!")
