import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات وقاعدة البيانات
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
    .main-logo-container { display: flex; justify-content: center; padding: 25px 0; }
    .youtube-style-box {
        background: linear-gradient(180deg, #FF4B4B 0%, #CC0000 100%);
        padding: 12px 35px; border-radius: 20px; display: flex; align-items: center; gap: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4); border: 2px solid #FF0000;
    }
    .logo-text { color: white; font-family: 'Arial Black', sans-serif; font-size: 42px; font-weight: 900; margin: 0; }
    .micro-img { font-size: 55px; filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.5)); }
    </style>
    
    <div class="main-logo-container">
        <div class="youtube-style-box">
            <span class="logo-text">Science</span>
            <span class="micro-img">🔬</span>
            <span class="logo-text">Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

all_cats = ["الكل", "البرمجة", "الفيزياء", "الكيمياء", "الطب", "الفضاء", "الذكاء الاصطناعي"]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

# أزرار التنقل العلوي
t_col1, t_col2 = st.columns([5, 1])
with t_col1:
    if st.button("🏠 الرئيسية"): st.session_state.page = 'home'; st.rerun()
with t_col2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# 🏠 3. الصفحة الرئيسية
# ==========================================
if st.session_state.page == 'home':
    st.header("📺 الفيديوهات المنشورة")
    vids = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    for v in vids:
        with st.container(border=True):
            st.subheader(v[1])
            st.video(v[2])
            st.write(f"👁️ المشاهدات: {v[6]} | ✍️ الناشر: {v[3]} | 📂 القسم: {v[4]}")

# ==========================================
# 📊 4. منطقة الناشرين (مع ميزة استعادة الحساب)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        # هنا ميزة "استعادة الحساب" موجودة في التاب الثالث كما طلبت
        tab1, tab2, tab3 = st.tabs(["🔑 دخول", "📝 حساب جديد", "🔐 استعادة الحساب"])
        
        with tab1:
            u = st.text_input("اسم المستخدم", key="login_u")
            p = st.text_input("كلمة المرور", type="password", key="login_p")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user: st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("بيانات الدخول غير صحيحة")
                
        with tab2:
            reg_u = st.text_input("اسم مستخدم جديد", key="reg_u")
            reg_p = st.text_input("كلمة مرور جديدة", type="password", key="reg_p")
            if st.button("تأكيد التسجيل"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                    conn.commit(); st.success("تم إنشاء الحساب!")
                except: st.error("هذا الاسم موجود مسبقاً!")

        with tab3:
            st.subheader("🔐 هل نسيت كلمة السر؟")
            f_u = st.text_input("ادخل اسم المستخدم الخاص بك")
            if f_u:
                user_exists = conn.execute("SELECT username FROM users WHERE username=?", (f_u,)).fetchone()
                if user_exists:
                    new_p = st.text_input("ادخل كلمة المرور الجديدة", type="password")
                    if st.button("تحديث كلمة المرور"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(new_p), f_u))
                        conn.commit(); st.success("تم تغيير كلمة المرور بنجاح!")
                else: st.warning("هذا الاسم غير مسجل لدينا.")
    
    else:
        # لوحة تحكم الناشر بعد الدخول
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج"): st.session_state.logged_in = False; st.rerun()
        
        st.divider()
        st.write("### 📤 رفع فيديو جديد")
        v_t = st.text_input("عنوان الفيديو")
        v_c = st.selectbox("القسم", all_cats[1:])
        v_f = st.file_uploader("ملف الفيديو", type=["mp4"])

        if st.button("فحص ونشر الفيديو"):
            if v_t and v_f:
                try:
                    video_filename = f"{v_t}_{v_f.name}"
                    path = os.path.join(VIDEOS_DIR, video_filename)
                    with open(path, "wb") as f: f.write(v_f.getbuffer())
                    
                    conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)",
                                 (v_t, path, st.session_state.user, v_c))
                    conn.commit(); st.success("✅ تم النشر بنجاح!")
                except sqlite3.IntegrityError:
                    st.error("⚠️ العنوان مكرر!")
