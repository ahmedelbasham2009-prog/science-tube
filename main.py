import streamlit as st
import os

# --- الإعدادات الأساسية (الهارد G) ---
DATA_FOLDER = r"G:\PythonProject1\ScienceTubeData"
VIDEO_FOLDER = os.path.join(DATA_FOLDER, "videos")
DB_FILE = os.path.join(DATA_FOLDER, "database.txt")

# إنشاء المجلدات لو مش موجودة
os.makedirs(VIDEO_FOLDER, exist_ok=True)

st.title("Science Tube - ساينس تيوب")

# --- دالة فحص التكرار والنشر ---
def publish_video(v_name, v_file):
    # 1. التأكد من عدم تكرار الاسم
    if os.path.exists(os.path.join(VIDEO_FOLDER, v_name)):
        return False, "⚠️ خطأ: هذا الفيديو موجود مسبقاً في الهارد G!"

    # 2. حفظ الملف في الهارد G
    video_path = os.path.join(VIDEO_FOLDER, v_name)
    with open(video_path, "wb") as f:
        f.write(v_file.getbuffer())
    
    # 3. تسجيل الفيديو في قاعدة البيانات (بدون تكرار)
    with open(DB_FILE, "a", encoding="utf-8") as db:
        db.write(f"{v_name}\n")
    
    return True, "✅ تم الفحص والنشر بنجاح في الهارد G"

# --- واجهة الناشرين ---
st.header("منطقة الناشرين")
uploaded_file = st.file_uploader("اختر الفيديو", type=["mp4", "mov", "avi"])
video_title = st.text_input("اسم الفيديو العلمي (يجب أن يكون فريداً)")

if st.button("فحص ونشر الفيديو"):
    if uploaded_file and video_title:
        # إضافة امتداد الملف للاسم
        full_name = video_title + "." + uploaded_file.name.split(".")[-1]
        
        success, message = publish_video(full_name, uploaded_file)
        
        if success:
            st.success(message)
        else:
            st.error(message)
    else:
        st.warning("من فضلك ارفع الفيديو واكتب الاسم أولاً")

# --- عرض الفيديوهات ---
st.header("الفيديوهات المنشورة")
if os.path.exists(VIDEO_FOLDER):
    videos = os.listdir(VIDEO_FOLDER)
    for v in videos:
        st.subheader(f"فيديو: {v}")
        st.video(os.path.join(VIDEO_FOLDER, v))
