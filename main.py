import streamlit as st
import sqlite3
import os

# --- 1. إعداد المجلدات وقاعدة البيانات ---
if not os.path.exists("science_videos_storage"):
    os.makedirs("science_videos_storage")


def init_db():
    conn = sqlite3.connect('science_tube_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     title
                     TEXT,
                     category
                     TEXT,
                     file_path
                     TEXT
                 )''')
    conn.commit()
    return conn


conn = init_db()

# --- 2. قائمة الأقسام العلمية (المحدثة) ---
SCIENTIFIC_SECTIONS = [
    "البرمجة", "العلاج الطبيعي", "الفضاء والفلك", "الذكاء الاصطناعي",
    "الطب البشري", "الجراحة", "الهندسة المدنية", "الهندسة الكهربائية",
    "الكيمياء العضوية", "الكيمياء التحليلية", "الرياضيات",
    "الفيزياء النظرية", "علوم البحار", "الأمن السيبراني",
    "الروبوتات", "التقنية الحيوية", "علم النفس",
    "الاقتصاد", "علوم البيئة", "الطاقة المتجددة",
    "الجيولوجيا", "علم الآثار", "اللغويات",
    "علوم النانو", "علم الوراثة"
]

# --- 3. تصميم الواجهة (Science Tube Design) ---
st.set_page_config(page_title="Science Tube", layout="wide", page_icon="🧪")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; background-color: #161b22; padding: 12px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { background-color: #21262d; border-radius: 6px; color: #c9d1d9; padding: 6px 10px; }
    .stTabs [aria-selected="true"] { background-color: #e91e63 !important; color: white !important; }
    .video-card { border: 1px solid #30363d; padding: 20px; border-radius: 15px; background-color: #1c2128; margin-bottom: 25px; }
    h1, h2 { color: #e91e63; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. القائمة الجانبية ---
st.sidebar.title("🧪 Science Tube")
choice = st.sidebar.radio("القائمة", ["🏠 تصفح الأقسام", "📤 رفع فيديو جديد", "🛠️ إدارة المحتوى (حذف)"])

# --- 5. صفحة تصفح الأقسام ---
if choice == "🏠 تصفح الأقسام":
    st.title("🧪 Science Tube")
    tabs = st.tabs(SCIENTIFIC_SECTIONS)
    for i, cat in enumerate(SCIENTIFIC_SECTIONS):
        with tabs[i]:
            vids = conn.execute("SELECT title, file_path FROM videos WHERE category = ?", (cat,)).fetchall()
            if not vids:
                st.info(f"قسم {cat} بانتظار مساهماتكم.")
            else:
                cols = st.columns(2)
                for idx, vid in enumerate(vids):
                    with cols[idx % 2]:
                        st.markdown('<div class="video-card">', unsafe_allow_html=True)
                        st.subheader(f"🎬 {vid[0]}")
                        st.video(vid[1])
                        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. صفحة رفع الفيديو ---
elif choice == "📤 رفع فيديو جديد":
    st.title("📤 إضافة فيديو إلى Science Tube")
    with st.form("upload_form"):
        v_title = st.text_input("عنوان الفيديو")
        v_cat = st.selectbox("اختر القسم العلمي", SCIENTIFIC_SECTIONS)
        v_file = st.file_uploader("اختر ملف الفيديو", type=["mp4", "mov"])
        if st.form_submit_button("🚀 فحص و نشر الفيديو"):
            if v_title and v_file:
                # منطق الرقابة البسيط
                science_keywords = ["برمج", "كود", "علاج", "طبيعي", "جسم", "طب", "فضاء", "علم", "هندسة", "كيمياء",
                                    "رياضيات"]
                if any(word in v_title.lower() for word in science_keywords):
                    file_path = os.path.join("science_videos_storage", v_file.name)
                    with open(file_path, "wb") as f:
                        f.write(v_file.getbuffer())
                    conn.execute("INSERT INTO videos (title, category, file_path) VALUES (?,?,?)",
                                 (v_title, v_cat, file_path))
                    conn.commit()
                    st.success("✅ تم النشر بنجاح!")
                    st.balloons()
                else:
                    st.error("❌ مرفوض: العنوان يجب أن يحتوي على مصطلحات علمية تخصصية.")
            else:
                st.warning("يرجى إكمال البيانات.")

# --- 7. صفحة الحذف ---
elif choice == "🛠️ إدارة المحتوى (حذف)":
    st.title("🛠️ إدارة فيديوهات Science Tube")
    password = st.sidebar.text_input("أدخل كلمة مرور الإدارة للحذف", type="password")

    if password == "1234":  # يمكنك تغيير كلمة المرور هنا
        all_vids = conn.execute("SELECT id, title, category, file_path FROM videos").fetchall()
        if not all_vids:
            st.info("لا توجد فيديوهات مسجلة.")
        else:
            for vid_id, title, cat, path in all_vids:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{title}** ({cat})")
                with col2:
                    if st.button(f"🗑️ حذف", key=f"del_{vid_id}"):
                        if os.path.exists(path):
                            os.remove(path)
                        conn.execute("DELETE FROM videos WHERE id = ?", (vid_id,))
                        conn.commit()
                        st.success("تم الحذف!")
                        st.rerun()
    else:
        st.error("يرجى إدخال كلمة المرور الصحيحة في القائمة الجانبية لتتمكن من الحذف.")
