import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# 💾 1. إعدادات المسارات الديناميكية
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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, path TEXT, 
                  author TEXT, category TEXT, likes INTEGER DEFAULT 0, views INTEGER DEFAULT 0)''')
    c.execute('CREATE TABLE IF NOT EXISTS comments (v_id INTEGER, user TEXT, text TEXT)')
    conn.commit()
    return conn

conn = init_db()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🎨 2. الإعدادات العامة والواجهة
# ==========================================
all_cats = [
    "الكل", "البرمجة", "علاج طبيعي", "الفيزياء التطبيقية", "الكيمياء",
    "الطب", "الفضاء", "الذكاء الاصطناعي", "الروبوتات", "الرياضيات",
    "الجيولوجيا", "علم النفس", "تكنولوجيا النانو", "الأحياء البحرية",
    "الهندسة", "علم الوراثة", "الأحافير", "الطاقة", "المناخ",
    "البرمجيات", "الإلكترونيات", "المنطق", "الكيمياء العضوية", "علوم الأعصاب"
]

if 'viewed_ids' not in st.session_state: st.session_state.viewed_ids = set()
if 'my_library' not in st.session_state: st.session_state.my_library = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "زائر"
if 'page' not in st.session_state: st.session_state.page = 'home'

st.set_page_config(page_title="Science Tube", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00ff00;'>🔬 Science Tube</h1>", unsafe_allow_html=True)

# أزرار التنقل
t_col1, t_col2 = st.columns([5, 1])
with t_col1:
    if st.button("🏠 الرئيسية"):
        st.session_state.page = 'home'
        st.rerun()
with t_col2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True):
        st.session_state.page = 'publisher_area'
        st.rerun()

st.divider()

# ==========================================
# 🏠 3. الصفحة الرئيسية والمكتبة
# ==========================================
with st.sidebar:
    st.title("🧭 التنقل")
    sub_nav = st.radio("القائمة:", ["🏠 الفيديوهات", "📚 مكتبتي العلمية"])
    selected_cat = st.radio("📂 الأقسام:", all_cats)

if st.session_state.page == 'home' and sub_nav == "🏠 الفيديوهات":
    query = "SELECT * FROM videos"
    params = ()
    if selected_cat != "الكل":
        query += " WHERE category=?"
        params = (selected_cat,)
    
    vids = conn.execute(query + " ORDER BY id DESC", params).fetchall()

    if not vids:
        st.info("لا توجد فيديوهات في هذا القسم حالياً.")

    for v in vids:
        with st.container(border=True):
            st.subheader(v[1])
            if v[0] not in st.session_state.viewed_ids:
                conn.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (v[0],))
                conn.commit()
                st.session_state.viewed_ids.add(v[0])

            if os.path.exists(v[2]):
                st.video(v[2])
            else:
                st.error("ملف الفيديو غير موجود.")

            res = conn.execute("SELECT views, likes FROM videos WHERE id=?", (v[0],)).fetchone()
            st.markdown(f"**👁️ المشاهدات:** {res[0]} | **✍️ الناشر:** {v[3]} | **📂 القسم:** {v[4]}")

            c1, c2, c3 = st.columns(3)
            if c1.button(f"📚 حفظ في المكتبة", key=f"lib_{v[0]}"):
                if v[0] not in st.session_state.my_library: 
                    st.session_state.my_library.append(v[0])
                    st.toast("تمت الإضافة للمكتبة")

            try:
                with open(v[2], "rb") as f:
                    c2.download_button("💾 تحميل", f, file_name=f"{v[1]}.mp4", key=f"dl_{v[0]}")
            except:
                pass

            if c3.button(f"❤️ {res[1]} أعجبني", key=f"lk_{v[0]}"):
                conn.execute("UPDATE videos SET likes = likes + 1 WHERE id = ?", (v[0],))
                conn.commit()
                st.rerun()

            with st.expander("💬 التعليقات"):
                comments = conn.execute("SELECT user, text FROM comments WHERE v_id = ?", (v[0],)).fetchall()
                for cm in comments: st.markdown(f"**👤 {cm[0]}:** {cm[1]}")
                new_comm = st.text_input("أضف تعليقك...", key=f"in_{v[0]}")
                if st.button("نشر التعليق", key=f"btn_{v[0]}"):
                    if new_comm:
                        conn.execute("INSERT INTO comments (v_id, user, text) VALUES (?,?,?)",
                                     (v[0], st.session_state.user, new_comm))
                        conn.commit()
                        st.rerun()

elif sub_nav == "📚 مكتبتي العلمية":
    st.header("📚 مكتبتي")
    for vid_id in st.session_state.my_library:
        vi = conn.execute("SELECT * FROM videos WHERE id=?", (vid_id,)).fetchone()
        if vi:
            with st.container(border=True):
                st.subheader(vi[1])
                st.video(vi[2])
                if st.button("إزالة", key=f"rem_{vi[0]}"):
                    st.session_state.my_library.remove(vi[0])
                    st.rerun()

# ==========================================
# 📊 4. منطقة الناشرين (مع منع التكرار)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب", "🔐 نسيت كلمة السر"])
        with tab1:
            u = st.text_input("اسم المستخدم", key="l_u")
            p = st.text_input("كلمة المرور", type="password", key="l_p")
            if st.button("دخول"):
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if user:
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")
        with tab2:
            reg_u = st.text_input("اسم مستخدم جديد", key="r_u")
            reg_p = st.text_input("كلمة مرور جديدة", type="password", key="r_p")
            if st.button("تأكيد التسجيل"):
                if reg_u and reg_p:
                    # التحقق من عدم تكرار المستخدم
                    check_user = conn.execute("SELECT username FROM users WHERE username=?", (reg_u,)).fetchone()
                    if check_user:
                        st.error("⚠️ اسم المستخدم هذا موجود بالفعل، اختر اسماً آخر.")
                    else:
                        conn.execute("INSERT INTO users VALUES (?,?)", (reg_u, hash_pass(reg_p)))
                        conn.commit()
                        st.success("✅ تم إنشاء الحساب بنجاح! توجه لتبويب تسجيل الدخول.")
                else:
                    st.warning("يرجى إدخال البيانات كاملة.")
        with tab3:
            f_u = st.text_input("أدخل اسم المستخدم للتحقق")
            if f_u:
                if conn.execute("SELECT username FROM users WHERE username=?", (f_u,)).fetchone():
                    n_p = st.text_input("كلمة السر الجديدة", type="password")
                    if st.button("تحديث"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(n_p), f_u))
                        conn.commit()
                        st.success("✅ تم التحديث!")
                else:
                    st.warning("الحساب غير موجود")
    else:
        st.subheader(f"مرحباً بك: {st.session_state.user}")
        if st.button("🚪 تسجيل الخروج"): 
            st.session_state.logged_in = False
            st.session_state.user = "زائر"
            st.rerun()
        
        st.divider()
        st.write("### 📤 رفع فيديو علمي جديد")
        v_t = st.text_input("عنوان الفيديو")
        v_c = st.selectbox("القسم العلمي", all_cats[1:])
        v_f = st.file_uploader("اختر ملف الفيديو (MP4 فقط)", type=["mp4"])

        if st.button("نشر الفيديو"):
            if v_t and v_f:
                # التحقق من عدم تكرار الفيديو (عن طريق العنوان أو اسم الملف)
                check_vid = conn.execute("SELECT title FROM videos WHERE title=?", (v_t,)).fetchone()
                if check_vid:
                    st.error("⚠️ فيديو بهذا العنوان موجود بالفعل، يرجى تغيير العنوان.")
                else:
                    video_filename = f"{hashlib.md5(v_f.name.encode()).hexdigest()}_{v_f.name}"
                    path = os.path.join(VIDEOS_DIR, video_filename)
                    with open(path, "wb") as f:
                        f.write(v_f.getbuffer())
                    
                    conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)",
                                 (v_t, path, st.session_state.user, v_c))
                    conn.commit()
                    st.success("✅ تم النشر بنجاح!")
                    st.rerun()
            else:
                st.warning("يرجى ملء جميع البيانات.")
