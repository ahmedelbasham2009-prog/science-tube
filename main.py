import streamlit as st
import os

# --- الإعدادات المرنة (تلقائياً في نفس مكان الملف) ---
# سيقوم بجلب مسار المجلد الحالي للمشروع مهما كان (في G أو C أو غيره)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "ScienceTubeData")
VIDEO_FOLDER = os.path.join(DATA_FOLDER, "videos")
DB_FILE = os.path.join(DATA_FOLDER, "database.txt")

# إنشاء المجلدات تلقائياً إذا لم تكن موجودة
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER, exist_ok=True)

st.set_page_config(page_title="Science Tube", layout="wide")
st.title("🔬 Science Tube - ساينس تيوب")

# --- دالة فحص التكرار والنشر ---
def publish_video(v_name, v_file):
    # الفحص: هل يوجد فيديو بنفس الاسم في مجلد الفيديوهات؟
    if os.path.exists(os.path.join(VIDEO_FOLDER, v_name)):
        return False, "⚠️ خطأ: هذا الفيديو موجود مسبقاً في النظام!"

    # حفظ الملف في مجلد المشروع
    video_path = os.path.join(VIDEO_FOLDER, v_name)
    with open(video_path, "wb") as f:
        f.write(v_file.getbuffer())
    
    # تسجيل الاسم في قاعدة البيانات
    with open(DB_FILE, "a", encoding="utf-8") as db:
        db.write(f"{v_name}\n")
    
    return True, "✅ تم الفحص والنشر بنجاح"

# --- واجهة الناشرين ---
st.sidebar.header("منطقة الناشرين")
video_title = st.sidebar.text_input("عنوان الفيديو العلمي")
uploaded_file = st.sidebar.file_uploader("اختر ملف الفيديو", type=["mp4", "mov", "avi"])

if st.sidebar.button("فحص ونشر الفيديو"):
    if uploaded_file and video_title:
        # استخراج الامتداد الأصلي للملف (مثل .mp4)
        ext = os.path.splitext(uploaded_file.name)[1]
        full_name = video_title + ext
        
        success, message = publish_video(full_name, uploaded_file)
        
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)
    else:
        st.sidebar.warning("يرجى إكمال البيانات (الاسم والملف)")

# --- عرض المحتوى ---
st.header("📺 الفيديوهات العلمية المتاحة")
if os.path.exists(VIDEO_FOLDER):
    videos = os.listdir(VIDEO_FOLDER)
    if not videos:
        st.info("لا توجد فيديوهات منشورة حالياً.")
    else:
        # عرض الفيديوهات في أعمدة
        cols = st.columns(2)
        for index, v in enumerate(videos):
            with cols[index % 2]:
                st.subheader(v)
                st.video(os.path.join(VIDEO_FOLDER, v))
