import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات (G:/PythonProject1)
# ==========================================
PROJECT_ROOT = "G:/PythonProject1" 
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
    conn.commit()
    return conn

conn = init_db()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🛡️ 2. نظام الرقابة (فحص العنوان)
# ==========================================
# قائمة الكلمات المحظورة (يمكنك زيادة الكلمات هنا)
BANNED_WORDS = ["هبل", "شتم", "قذارة", "سياسة", "تحدي", "مقالب", "لعب"] 

def is_scientific(title):
    # تحويل العنوان لنص صغير للفحص
    t = title.lower()
    for word in BANNED_WORDS:
        if word in t:
            return False
    return True

# ==========================================
# 🎨 3. التصميم (الميكروسكوب في المنتصف)
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

all_cats = ["الكل", "البرمجة", "علاج طبيعي", "الفيزياء", "الكيمياء", "الطب", "الفضاء"]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

# أزرار التنقل
t_col1, t_col2 = st.columns([5, 1])
with t_col1:
    if st.button("🏠 الرئيسية"): st.session_state.page = 'home'; st.rerun()
with t_col2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# 🏠 4. الصفحة الرئيسية (مع مربع البحث)
# ==========================================
if st.session_state.page == 'home':
    search_q = st.text_input("🔍 ابحث عن فيديو علمي...")
    
    sql = "SELECT * FROM videos WHERE 1=1"
    params = []
    if search_q:
        sql += " AND title LIKE ?"
        params.append(f"%{search_q}%")
    
    vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()
    for v in vids:
        with st.container(border=True):
            st.subheader(v[1])
            st.video(v[2])
            st.write(f"👁️ {v[6]} مشاهدة | ✍️ الناشر: {v[3]} | 📂 القسم: {v[4]}")

# ==========================================
# 📊 5. منطقة الناشرين (مع الرقابة الصارمة)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔑 دخول", "📝 حساب جديد", "🔐 استعادة"])
        # (أكواد الدخول والتسجيل هنا كما هي في نسختك السابقة)
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        v_t = st.text_input("عنوان الفيديو")
        v_c = st.selectbox("القسم", all_cats[1:])
        v_f = st.file_uploader("ارفع الفيديو", type=["mp4"])
        
        if st.button("فحص ونشر الفيديو"):
            if v_t and v_f:
                # --- تفعيل الرقابة هنا ---
                if not is_scientific(v_t):
                    st.error("⚠️ مرفوض! العنوان يحتوي على كلمات غير لائقة أو غير علمية.")
                else:
                    try:
                        path = os.path.join(VIDEOS_DIR, v_f.name)
                        with open(path, "wb") as f: f.write(v_f.getbuffer())
                        conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (v_t, path, st.session_state.user, v_c))
                        conn.commit(); st.success("✅ تم الفحص والنشر بنجاح!")
                    except: st.error("العنوان مكرر!")
    vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()

    if not vids:
        st.info("لا توجد فيديوهات تطابق بحثك.")

    for v in vids:
        with st.container(border=True):
            st.subheader(v[1])
            if v[0] not in st.session_state.viewed_ids:
                conn.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (v[0],))
                conn.commit(); st.session_state.viewed_ids.add(v[0])
            st.video(v[2])
            res = conn.execute("SELECT views, likes FROM videos WHERE id=?", (v[0],)).fetchone()
            st.markdown(f"**👁️ المشاهدات:** {res[0]} | **✍️ الناشر:** {v[3]} | **📂 القسم:** {v[4]}")
            c1, c2, c3 = st.columns(3)
            if c1.button(f"📚 حفظ في المكتبة", key=f"lib_{v[0]}"):
                if v[0] not in st.session_state.my_library: st.session_state.my_library.append(v[0]); st.rerun()
            try:
                with open(v[2], "rb") as f:
                    c2.download_button("💾 حفظ", f, file_name=f"{v[1]}.mp4", key=f"dl_{v[0]}")
            except: c2.write("غير متوفر")
            if c3.button(f"❤️ {res[1]}", key=f"lk_{v[0]}"):
                conn.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (v[0],))
                conn.commit(); st.rerun()

elif sub_nav == "📚 مكتبتي العلمية":
    st.header("📚 مكتبتي العلمية")
    for vid_id in st.session_state.my_library:
        vi = conn.execute("SELECT * FROM videos WHERE id=?", (vid_id,)).fetchone()
        if vi:
            with st.container(border=True):
                st.subheader(vi[1]); st.video(vi[2])
                if st.button("إزالة", key=f"rem_{vi[0]}"): st.session_state.my_library.remove(vi[0]); st.rerun()

# ==========================================
# 📊 4. منطقة الناشرين (دون تعديل)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب", "🔐 نسيت كلمة السر"])
        with tab1:
            u = st.text_input("اسم المستخدم", key="l_u")
            p = st.text_input("كلمة المرور", type="password", key="l_p")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user: st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("خطأ في البيانات")
        with tab2:
            reg_u = st.text_input("اسم مستخدم جديد", key="r_u")
            reg_p = st.text_input("كلمة مرور جديدة", type="password", key="r_p")
            if st.button("تأكيد التسجيل"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                    conn.commit(); st.success("تم التسجيل!")
                except: st.error("الاسم مأخوذ")
        with tab3:
            f_u = st.text_input("اسم المستخدم للتحقق")
            if f_u:
                if conn.execute("SELECT username FROM users WHERE username=?", (f_u,)).fetchone():
                    n_p = st.text_input("كلمة السر الجديدة", type="password")
                    if st.button("تحديث"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(n_p), f_u))
                        conn.commit(); st.success("تم التحديث!")
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج"): st.session_state.logged_in = False; st.session_state.user = "زائر"; st.rerun()
        st.divider()
        v_t = st.text_input("عنوان الفيديو")
        v_c = st.selectbox("القسم العلمي", all_cats[1:])
        v_f = st.file_uploader("اختر ملف الفيديو", type=["mp4"])
        if st.button("فحص ونشر الفيديو"): 
            if v_t and v_f:
                try:
                    path = os.path.join(VIDEOS_DIR, v_f.name)
                    with open(path, "wb") as f: f.write(v_f.getbuffer())
                    conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (v_t, path, st.session_state.user, v_c))
                    conn.commit(); st.success("✅ تم النشر!"); st.rerun()
                except sqlite3.IntegrityError: st.error("⚠️ العنوان مكرر!")
                conn.commit(); st.rerun()

            with st.expander("💬 قسم التعليقات والمناقشة"):
                comments = conn.execute("SELECT user, text FROM comments WHERE v_id = ?", (v[0],)).fetchall()
                for cm in comments: st.markdown(f"**👤 {cm[0]}:** {cm[1]}")
                new_comm = st.text_input("اكتب تعليقك هنا...", key=f"in_{v[0]}")
                if st.button("نشر التعليق", key=f"btn_{v[0]}"):
                    if new_comm:
                        conn.execute("INSERT INTO comments (v_id, user, text) VALUES (?,?,?)", (v[0], st.session_state.user, new_comm))
                        conn.commit(); st.rerun()

elif sub_nav == "📚 مكتبتي العلمية":
    st.header("📚 مكتبتي")
    for vid_id in st.session_state.my_library:
        vi = conn.execute("SELECT * FROM videos WHERE id=?", (vid_id,)).fetchone()
        if vi:
            with st.container(border=True):
                st.subheader(vi[1]); st.video(vi[2])
                if st.button("إزالة", key=f"rem_{vi[0]}"): st.session_state.my_library.remove(vi[0]); st.rerun()

# ==========================================
# 📊 4. منطقة الناشرين (كل شيء عربي)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب", "🔐 نسيت كلمة السر"])
        with tab1:
            u = st.text_input("اسم المستخدم", key="l_u")
            p = st.text_input("كلمة المرور", type="password", key="l_p")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user: st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("خطأ في البيانات")
        with tab2:
            reg_u = st.text_input("اسم مستخدم جديد", key="r_u")
            reg_p = st.text_input("كلمة مرور جديدة", type="password", key="r_p")
            if st.button("تأكيد التسجيل"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                    conn.commit(); st.success("تم الحفظ بنجاح!")
                except: st.error("الاسم مأخوذ")
        with tab3:
            st.write("### استعادة كلمة السر")
            f_u = st.text_input("أدخل اسم المستخدم للتحقق")
            if f_u:
                if conn.execute("SELECT username FROM users WHERE username=?", (f_u,)).fetchone():
                    st.success("تم العثور على الحساب")
                    n_p = st.text_input("كلمة السر الجديدة", type="password")
                    if st.button("تحديث كلمة السر"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(n_p), f_u))
                        conn.commit(); st.success("تم التحديث!")
                else: st.warning("اسم المستخدم غير مسجل")
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج"): st.session_state.logged_in = False; st.session_state.user = "زائر"; st.rerun()
        st.divider()
        st.write("### 📤 فحص ونشر الفيديو")
        v_t = st.text_input("عنوان الفيديو")
        v_c = st.selectbox("القسم العلمي", all_cats[1:])
        v_f = st.file_uploader("اختر ملف الفيديو", type=["mp4"])
        
        if st.button("فحص ونشر الفيديو"): 
            if v_t and v_f:
                path = os.path.join(VIDEOS_DIR, v_f.name)
                with open(path, "wb") as f: f.write(v_f.getbuffer())
                conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (v_t, path, st.session_state.user, v_c))
                conn.commit(); st.success("تم النشر بنجاح!"); st.rerun()
