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
DB_PATH = os.path.join(STORAGE_PATH, "science_tube_v40.db")

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS videos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, path TEXT, 
                  author TEXT, category TEXT, likes INTEGER DEFAULT 0, views INTEGER DEFAULT 0)''')
    conn.commit()
    return conn

conn = init_db()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🛡️ 2. نظام الرقابة (فحص العنوان)
# ==========================================
BANNED_WORDS = ["هبل", "مقالب", "تحدي", "سياسة", "شتيمة", "قذارة", "لعب", "مسخرة", "تيك توك", "كورة", "افلام"]

def is_scientific(title):
    t = title.lower()
    return not any(word in t for word in BANNED_WORDS)

# ==========================================
# 🎨 3. التصميم والشعار
# ==========================================
st.set_page_config(page_title="Science Tube", page_icon="🔬", layout="wide")

st.markdown("""
    <style>
    .main-logo-container { display: flex; justify-content: center; padding: 20px 0; }
    .youtube-style-box {
        background: linear-gradient(180deg, #FF4B4B 0%, #CC0000 100%);
        padding: 10px 40px; border-radius: 20px; display: flex; align-items: center; gap: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4); border: 2px solid #FF0000;
    }
    .logo-text { color: white; font-family: 'Arial Black', sans-serif; font-size: 45px; font-weight: 900; margin: 0; }
    .micro-img { font-size: 55px; }
    </style>
    <div class="main-logo-container">
        <div class="youtube-style-box">
            <span class="logo-text">Science</span>
            <span class="micro-img">🔬</span>
            <span class="logo-text">Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

all_cats = ["الكل", "البرمجة", "علاج طبيعي", "الفيزياء التطبيقية", "الكيمياء", "الطب", "الفضاء", "الذكاء الاصطناعي", "الروبوتات", "الرياضيات", "الجيولوجيا", "علم النفس", "تكنولوجيا النانو", "الأحياء البحرية", "الهندسة", "علم الوراثة", "الأحافير", "الطاقة", "المناخ", "البرمجيات", "الإلكترونيات", "المنطق", "الكيمياء العضوية", "علوم الأعصاب"]

if 'my_library' not in st.session_state: st.session_state.my_library = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

# أزرار التنقل العلوي
c_n1, c_n2 = st.columns([5, 1])
with c_n1:
    if st.button("🏠 الرئيسية", key="top_home"): st.session_state.page = 'home'; st.rerun()
with c_n2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True, key="top_pub"): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# 🏠 4. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.title("🧭 التنقل")
    sub_nav = st.radio("القائمة:", ["🏠 الفيديوهات", "📚 مكتبتي العلمية"], key="sb_radio")
    selected_cat = st.radio("📂 الأقسام العلمية:", all_cats, key="sb_cats_list")

# ==========================================
# 🏠 5. الصفحة الرئيسية (المنطق الجديد للرسائل)
# ==========================================
if st.session_state.page == 'home':
    if sub_nav == "🏠 الفيديوهات":
        search_q = st.text_input("🔍 ابحث عن فيديو علمي...", "", key="main_search_box")

        sql = "SELECT * FROM videos WHERE 1=1"
        params = []
        if selected_cat != "الكل":
            sql += " AND category=?"
            params.append(selected_cat)
        if search_q:
            sql += " AND title LIKE ?"
            params.append(f"%{search_q}%")
        
        vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()

        # --- منطق الرسائل المطلوب ---
        if not vids:
            if search_q: # إذا كان المستخدم يبحث فعلياً
                st.warning("عذراً، لم يتم العثور على أي محتوى يطابق بحثك..")
            else: # إذا كانت الصفحة فارغة ولا يوجد بحث
                st.info("لا يوجد محتوى علمي متاح حالياً في هذا القسم..")
        else:
            for v in vids:
                with st.container(border=True):
                    st.subheader(v[1])
                    st.video(v[2])
                    st.write(f"👁️ {v[6]} | ✍️ {v[3]} | 📂 {v[4]}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("📚 حفظ", key=f"save_{v[0]}"):
                        if v[0] not in st.session_state.my_library:
                            st.session_state.my_library.append(v[0]); st.success("تم الحفظ!")
                    if c3.button(f"❤️ {v[5]}", key=f"like_{v[0]}"):
                        conn.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (v[0],))
                        conn.commit(); st.rerun()

    elif sub_nav == "📚 مكتبتي العلمية":
        st.header("📚 مكتبتي المحفوظة")
        if not st.session_state.my_library:
            st.write("مكتبتك فارغة حالياً.")
        for vid_id in st.session_state.my_library:
            vi = conn.execute("SELECT * FROM videos WHERE id=?", (vid_id,)).fetchone()
            if vi:
                with st.container(border=True):
                    st.subheader(vi[1]); st.video(vi[2])
                    if st.button("إزالة", key=f"del_{vi[0]}"):
                        st.session_state.my_library.remove(vi[0]); st.rerun()

# ==========================================
# 📊 6. منطقة الناشرين (فحص ونشر)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        t1, t2, t3 = st.tabs(["🔑 دخول", "📝 تسجيل", "🔐 استعادة"])
        with t1:
            u = st.text_input("اسم المستخدم", key="u_log")
            p = st.text_input("كلمة المرور", type="password", key="p_log")
            if st.button("دخول", key="b_log"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user: st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("بيانات غير صحيحة")
        with t2:
            ru = st.text_input("اسم جديد", key="u_reg")
            rp = st.text_input("باسورد جديد", type="password", key="p_reg")
            if st.button("تسجيل", key="b_reg"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (ru, hash_pass(rp)))
                    conn.commit(); st.success("تم التسجيل!")
                except: st.error("الاسم مكرر")
        with t3:
            fu = st.text_input("اسم المستخدم", key="u_res")
            if fu:
                if conn.execute("SELECT username FROM users WHERE username=?", (fu,)).fetchone():
                    np = st.text_input("باسورد جديد", type="password", key="p_res")
                    if st.button("تحديث", key="b_res"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(np), fu))
                        conn.commit(); st.success("تم التحديث!")
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج", key="b_exit"): st.session_state.logged_in = False; st.rerun()
        st.divider()
        vt = st.text_input("عنوان الفيديو العلمي", key="v_title")
        vc = st.selectbox("القسم", all_cats[1:], key="v_cat")
        vf = st.file_uploader("ارفع الفيديو", type=["mp4"], key="v_file")
        
        # الزر المطلوب مع الرقابة الصارمة
        if st.button("فحص ونشر الفيديو", key="btn_check_pub"):
            if vt and vf:
                if not is_scientific(vt):
                    st.error("⚠️ السيستم رفض العنوان! يرجى اختيار عنوان علمي وتجنب الكلمات المحظورة.")
                else:
                    try:
                        path = os.path.join(VIDEOS_DIR, vf.name)
                        with open(path, "wb") as f: f.write(vf.getbuffer())
                        conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (vt, path, st.session_state.user, vc))
                        conn.commit(); st.success("✅ تم الفحص والنشر بنجاح!")
                    except: st.error("العنوان مكرر!")
