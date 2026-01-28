import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات والقاعدة
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_PATH = os.path.join(BASE_DIR, "ScienceTubeData")
VIDEOS_DIR = os.path.join(STORAGE_PATH, "videos")
DB_PATH = os.path.join(STORAGE_PATH, "science_tube_final.db")

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS videos 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, path TEXT, 
              author TEXT, category TEXT, likes INTEGER DEFAULT 0, views INTEGER DEFAULT 0)''')
conn.commit()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🛡️ 2. نظام الرقابة الصارم (فلتر العلم)
# ==========================================
BANNED_WORDS = ["الأهلي", "الزمالك", "الجيش الملكي", "الرجاء", "الوداد", "مباراة", "ملخص", "أهداف", "هدف", "كورة", "كرة", "يتعادل", "يفوز", "خسارة", "دوري", "كأس", "مقالب", "تحدي", "هبل", "ضحك", "مسخرة", "تيك توك", "فضيحة", "تريند"]

def is_scientific(title):
    t = title.strip().lower()
    if any(word in t for word in BANNED_WORDS): return False
    return len(t) >= 10

# ==========================================
# 🎨 3. إعدادات التطبيق للشاشة الرئيسية (Chrome PWA)
# ==========================================
st.set_page_config(page_title="Science Tube", page_icon="🔬", layout="wide")

# هذا الجزء يجعل كروم يتعرف على الاسم والأيقونة عند التثبيت
st.markdown(f"""
    <head>
        <title>Science Tube</title>
        <meta name="apple-mobile-web-app-title" content="Science Tube">
        <meta name="application-name" content="Science Tube">
    </head>
    <style>
    .header-container {{
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }}
    .logo-box {{
        background-color: #FF0000;
        color: white;
        padding: 15px 35px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0px 4px 15px rgba(255, 0, 0, 0.3);
    }}
    .logo-text {{
        font-family: 'Arial Black', sans-serif;
        font-size: 38px;
        font-weight: bold;
        margin: 0;
    }}
    .logo-icon {{
        font-size: 45px;
    }}
    </style>
    <div class="header-container">
        <div class="logo-box">
            <span class="logo-icon">🔬</span>
            <span class="logo-text">Science Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🏠 4. إدارة الصفحات والقوائم
# ==========================================
all_cats = ["الكل", "البرمجة", "علاج طبيعي", "الفيزياء التطبيقية", "الكيمياء", "الطب", "الفضاء", "الذكاء الاصطناعي", "الروبوتات", "الرياضيات", "الجيولوجيا", "علم النفس", "تكنولوجيا النانو", "الأحياء البحرية", "الهندسة", "علم الوراثة", "الأحافير", "الطاقة", "المناخ", "البرمجيات", "الإلكترونيات", "المنطق", "الكيمياء العضوية", "علوم الأعصاب"]

if 'my_library' not in st.session_state: st.session_state.my_library = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

# أزرار التنقل
c_n1, c_n2 = st.columns([5, 1])
with c_n1:
    if st.button("🏠 الرئيسية", key="h_b"): st.session_state.page = 'home'; st.rerun()
with c_n2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True, key="p_b"): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

with st.sidebar:
    st.title("🧭 التنقل")
    sub_nav = st.radio("القائمة:", ["🏠 الفيديوهات", "📚 مكتبتي العلمية"], key="s_nav")
    selected_cat = st.radio("📂 الأقسام العلمية:", all_cats, key="s_cats")

# ==========================================
# 🏠 5. المحتوى والبحث
# ==========================================
if st.session_state.page == 'home':
    if sub_nav == "🏠 الفيديوهات":
        search_q = st.text_input("🔍 ابحث عن فيديو علمي...", "", key="search_main")
        sql = "SELECT * FROM videos WHERE 1=1"
        params = []
        if selected_cat != "الكل":
            sql += " AND category=?"; params.append(selected_cat)
        if search_q:
            sql += " AND title LIKE ?"; params.append(f"%{search_q}%")
        
        vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()

        if not vids:
            if search_q: st.warning("عذراً، لم يتم العثور على نتائج تطابق بحثك..")
            else: st.info("لا يوجد محتوى علمي متاح حالياً في هذا القسم..")
        else:
            for v in vids:
                with st.container(border=True):
                    st.subheader(v[1]); st.video(v[2])
                    st.write(f"👁️ {v[6]} | ✍️ {v[3]} | 📂 {v[4]}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("📚 حفظ", key=f"sv_{v[0]}"):
                        if v[0] not in st.session_state.my_library:
                            st.session_state.my_library.append(v[0]); st.success("تم الحفظ!")
                    if c3.button(f"❤️ {v[5]}", key=f"lk_{v[0]}"):
                        conn.execute("UPDATE videos SET likes=likes+1 WHERE id=?", (v[0],))
                        conn.commit(); st.rerun()

# ==========================================
# 📊 6. منطقة الناشرين (دخول / استعادة / رفع)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        t = st.tabs(["🔑 دخول", "📝 تسجيل", "🔐 استعادة"])
        with t[0]:
            u = st.text_input("اسم المستخدم", key="l_u"); p = st.text_input("كلمة المرور", type="password", key="l_p")
            if st.button("دخول", key="l_b"):
                res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if res: st.session_state.logged_in=True; st.session_state.user=u; st.rerun()
                else: st.error("خطأ!")
        with t[1]:
            ru = st.text_input("اسم جديد", key="r_u"); rp = st.text_input("كلمة سر", type="password", key="r_p")
            if st.button("تسجيل", key="r_b"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (ru, hash_pass(rp)))
                    conn.commit(); st.success("تم!")
                except: st.error("موجود!")
        with t[2]:
            fu = st.text_input("الاسم للاستعادة", key="f_u")
            if fu:
                if conn.execute("SELECT username FROM users WHERE username=?", (fu,)).fetchone():
                    np = st.text_input("باسورد جديد", type="password", key="f_p")
                    if st.button("تحديث", key="f_b"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(np), fu))
                        conn.commit(); st.success("تم التحديث!")
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج", key="logout"): st.session_state.logged_in=False; st.rerun()
        st.divider()
        vt = st.text_input("عنوان الفيديو العلمي", key="up_t")
        vc = st.selectbox("القسم", all_cats[1:], key="up_c")
        vf = st.file_uploader("ارفع MP4", type=["mp4"], key="up_f")
        if st.button("فحص ونشر الفيديو", key="up_btn"):
            if vt and vf:
                if not is_scientific(vt): st.error("⚠️ السيستم رفض العنوان! المحتوى غير علمي.")
                else:
                    try:
                        path = os.path.join(VIDEOS_DIR, vf.name)
                        with open(path, "wb") as f: f.write(vf.getbuffer())
                        conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (vt, path, st.session_state.user, vc))
                        conn.commit(); st.success("✅ تم الفحص والنشر!")
                    except: st.error("مكرر!")
