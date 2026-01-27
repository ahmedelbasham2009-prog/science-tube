import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات وقاعدة البيانات (مرنة وعامة)
# ==========================================
# المشروع سيعمل في أي هارد أو فولدر تضعه فيه تلقائياً
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STORAGE_PATH = os.path.join(PROJECT_ROOT, "ScienceTubeData")
VIDEOS_DIR = os.path.join(STORAGE_PATH, "videos")
DB_PATH = os.path.join(STORAGE_PATH, "science_tube_v16.db")

# إنشاء المجلدات إذا لم تكن موجودة
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # PRIMARY KEY يمنع تكرار اليوزر نهائياً
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    # UNIQUE يمنع تكرار عنوان الفيديو نهائياً
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
        padding: 10px 40px; border-radius: 20px; display: flex; align-items: center; gap: 20px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4); border: 2px solid #FF0000;
    }
    .logo-text { color: white; font-family: 'Arial Black', sans-serif; font-size: 45px; font-weight: 900; margin: 0; }
    .micro-img { font-size: 60px; filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.5)); }
    </style>
    
    <div class="main-logo-container">
        <div class="youtube-style-box">
            <span class="logo-text">Science</span>
            <span class="micro-img">🔬</span>
            <span class="logo-text">Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# الأقسام العلمية
all_cats = ["الكل", "البرمجة", "الفيزياء", "الكيمياء", "الطب", "الفضاء", "الذكاء الاصطناعي", "الأحياء"]

# إدارة حالة الجلسة
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
# 🏠 3. الصفحة الرئيسية (عرض الفيديوهات)
# ==========================================
if st.session_state.page == 'home':
    st.header("📺 أحدث الفيديوهات العلمية")
    vids = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    
    if not vids:
        st.info("لا توجد فيديوهات منشورة حالياً. كن أول من ينشر!")
    else:
        for v in vids:
            with st.container(border=True):
                st.subheader(v[1]) # العنوان
                st.video(v[2])     # المسار
                st.write(f"✍️ الناشر: {v[3]} | 📂 القسم: {v[4]}")

# ==========================================
# 📊 4. منطقة الناشرين (دخول + رفع بدون تكرار)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])
        
        with tab1:
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
                    
        with tab2:
            reg_u = st.text_input("اختر اسم مستخدم فريد")
            reg_p = st.text_input("اختر كلمة مرور قوية", type="password")
            if st.button("تأكيد التسجيل"):
                if reg_u and reg_p:
                    try:
                        conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                        conn.commit()
                        st.success("تم إنشاء الحساب بنجاح! يمكنك الدخول الآن.")
                    except sqlite3.IntegrityError:
                        st.error("⚠️ هذا الاسم مأخوذ مسبقاً، اختر اسماً آخر.")
                else:
                    st.warning("برجاء ملء جميع الخانات.")
    
    else:
        st.subheader(f"مرحباً بك يا دكتور {st.session_state.user} 🔬")
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user = "زائر"
            st.rerun()
        
        st.divider()
        st.write("### 📤 رفع فيديو علمي جديد")
        v_t = st.text_input("عنوان الفيديو (سيظهر للجمهور)")
        v_c = st.selectbox("اختر تخصص الفيديو", all_cats[1:])
        v_f = st.file_uploader("ارفع ملف الفيديو (MP4)", type=["mp4"])

        if st.button("فحص ونشر الفيديو"):
            if v_t and v_f:
                try:
                    # تكوين اسم الملف وحفظه
                    video_filename = f"{v_t.replace(' ', '_')}_{v_f.name}"
                    path = os.path.join(VIDEOS_DIR, video_filename)
                    
                    with open(path, "wb") as f:
                        f.write(v_f.getbuffer())
                    
                    # الحفظ في قاعدة البيانات (سيفشل لو العنوان مكرر بسبب UNIQUE)
                    conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)",
                                 (v_t, path, st.session_state.user, v_c))
                    conn.commit()
                    st.success("✅ تم الفحص والنشر بنجاح!")
                    st.balloons()
                except sqlite3.IntegrityError:
                    st.error("⚠️ خطأ: هذا العنوان موجود مسبقاً! يرجى اختيار عنوان مختلف للفيديو.")
            else:
                st.warning("برجاء إدخال العنوان ورفع الملف.")
