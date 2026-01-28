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
DB_PATH = os.path.join(STORAGE_PATH, "science_tube_v80.db")

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
# 🛡️ 2. نظام الرقابة الفولاذي المحدث (إضافة محظورات جديدة)
# ==========================================
BANNED_WORDS = [
    # أندية ورياضة (توسيع النطاق)
    "الأهلي", "الزمالك", "الجيش الملكي", "الرجاء", "الوداد", "الهلال", "النصر", "الاتحاد", 
    "ريال مدريد", "برشلونة", "ليفربول", "مانشستر", "بايرن", "مباراة", "ملخص", "أهداف", 
    "هدف", "كورة", "كرة", "يتعادل", "يفوز", "خسارة", "دوري", "كأس", "بطولة", "منتخب", 
    "لاعب", "كابتن", "ضربة جزاء", "حكم", "نادي", "المونديال",
    # مشاهير وتريندات وترفيه
    "مقالب", "تحدي", "هبل", "ضحك", "مسخرة", "لعب", "جيمينج", "تيك توك", "بث مباشر", 
    "لايف", "فلوج", "يوميات", "فضيحة", "شاهد قبل الحذف", "مهرجان", "أغنية", "كليب", 
    "فيلم", "مسلسل", "تريند", "بوجي", "تامر", "شيرين", "نمبر وان", "اكتساح",
    # محتوى غير لائق أو غير علمي
    "سياسة", "عاجل", "خبر", "مظاهرات", "انتخابات", "رئيس", "وزير", "شتيمة", "قذارة", 
    "هياط", "خناقة", "ضرب", "دم", "رعب"
]

def is_scientific(title):
    t = title.strip().lower()
    # 1. منع الكلمات المحظورة
    if any(word in t for word in BANNED_WORDS):
        return False
    # 2. منع العناوين القصيرة جداً (أقل من 10 حروف غالباً ما تكون غير جادة)
    if len(t) < 10:
        return False
    return True

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

# أزرار التنقل
c_n1, c_n2 = st.columns([5, 1])
with c_n1:
    if st.button("🏠 الرئيسية", key="top_h"): st.session_state.page = 'home'; st.rerun()
with c_n2:
    label = f"🚀 {st.session_state.user}" if st.session_state.logged_in else "👤 منطقة الناشرين"
    if st.button(label, use_container_width=True, key="top_p"): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# 🏠 4. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.title("🧭 التنقل")
    sub_nav = st.radio("القائمة:", ["🏠 الفيديوهات", "📚 مكتبتي العلمية"], key="sb_nav")
    selected_cat = st.radio("📂 الأقسام العلمية:", all_cats, key="sb_cats")

# ==========================================
# 🏠 5. الصفحة الرئيسية
# ==========================================
if st.session_state.page == 'home':
    if sub_nav == "🏠 الفيديوهات":
        search_q = st.text_input("🔍 ابحث عن فيديو علمي...", "", key="search_bar")
        sql = "SELECT * FROM videos WHERE 1=1"
        params = []
        if selected_cat != "الكل":
            sql += " AND category=?"; params.append(selected_cat)
        if search_q:
            sql += " AND title LIKE ?"; params.append(f"%{search_q}%")
        
        vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()

        if not vids:
            if search_q: st.warning("عذراً، لم يتم العثور على أي محتوى يطابق بحثك..")
            else: st.info("لا يوجد محتوى علمي متاح حالياً في هذا القسم..")
        else:
            for v in vids:
                with st.container(border=True):
                    st.subheader(v[1]); st.video(v[2])
                    st.write(f"👁️ {v[6]} | ✍️ {v[3]} | 📂 {v[4]}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("📚 حفظ", key=f"s_{v[0]}"):
                        if v[0] not in st.session_state.my_library:
                            st.session_state.my_library.append(v[0]); st.success("تم الحفظ!")
                    if c3.button(f"❤️ {v[5]}", key=f"l_{v[0]}"):
                        conn.execute("UPDATE videos SET likes=likes+1 WHERE id=?", (v[0],))
                        conn.commit(); st.rerun()

# ==========================================
# 📊 6. منطقة الناشرين (دخول / استعادة / فحص ونشر)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        t = st.tabs(["🔑 دخول", "📝 تسجيل", "🔐 استعادة"])
        with t[0]:
            u = st.text_input("اسم المستخدم", key="l_u")
            p = st.text_input("كلمة المرور", type="password", key="l_p")
            if st.button("دخول", key="l_b"):
                res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if res: st.session_state.logged_in=True; st.session_state.user=u; st.rerun()
                else: st.error("خطأ!")
        with t[1]:
            ru = st.text_input("اسم مستخدم جديد", key="r_u")
            rp = st.text_input("كلمة سر جديدة", type="password", key="r_p")
            if st.button("تسجيل", key="r_b"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (ru, hash_pass(rp)))
                    conn.commit(); st.success("تم!")
                except: st.error("مكرر!")
        with t[2]:
            fu = st.text_input("الاسم للاستعادة", key="f_u")
            if fu:
                check = conn.execute("SELECT username FROM users WHERE username=?", (fu,)).fetchone()
                if check:
                    np = st.text_input("باسورد جديد", type="password", key="f_p")
                    if st.button("تحديث", key="f_b"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(np), fu))
                        conn.commit(); st.success("تم التحديث!")
                else: st.warning("غير موجود")
    else:
        st.subheader(f"لوحة التحكم: {st.session_state.user}")
        if st.button("🚪 خروج", key="logout"): st.session_state.logged_in=False; st.rerun()
        st.divider()
        vt = st.text_input("عنوان الفيديو العلمي", key="v_t")
        vc = st.selectbox("القسم", all_cats[1:], key="v_c")
        vf = st.file_uploader("ارفع MP4", type=["mp4"], key="v_f")
        
        # الزر المطلوب مع نظام الرقابة الشامل
        if st.button("فحص ونشر الفيديو", key="v_pub"):
            if vt and vf:
                if not is_scientific(vt):
                    st.error("⚠️ السيستم رفض العنوان! المحتوى رياضي، ترفيهي أو غير علمي.")
                else:
                    try:
                        path = os.path.join(VIDEOS_DIR, vf.name)
                        with open(path, "wb") as f: f.write(vf.getbuffer())
                        conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (vt, path, st.session_state.user, vc))
                        conn.commit(); st.success("✅ تم الفحص والنشر بنجاح!")
                    except: st.error("العنوان مكرر!")
