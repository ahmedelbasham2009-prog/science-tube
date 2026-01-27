import streamlit as st
import os

# --- الإعدادات (الهارد G كما كانت) ---
VIDEO_FOLDER = r"G:\PythonProject1\ScienceTubeData\videos"
USER_FILE = r"G:\PythonProject1\ScienceTubeData\users.txt"

# إنشاء المجلدات لو مش موجودة
os.makedirs(VIDEO_FOLDER, exist_ok=True)
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f: pass

st.title("Science Tube - ساينس تيوب")

# --- منطقة الناشرين (في منتصف الصفحة كما طلبت) ---
st.header("منطقة الناشرين")

username = st.text_input("اسم الناشر (يجب أن يكون فريداً)")
video_title = st.text_input("عنوان الفيديو العلمي")
uploaded_file = st.file_uploader("اختر الفيديو", type=["mp4", "mov", "avi"])

if st.button("فحص ونشر الفيديو"):
    if username and video_title and uploaded_file:
        # 1. فحص تكرار المستخدم
        with open(USER_FILE, "r") as f:
            existing_users = f.read().splitlines()
        
        # 2. فحص تكرار الفيديو (بالاسم)
        ext = os.path.splitext(uploaded_file.name)[1]
        full_video_name = video_title + ext
        
        if username in existing_users:
            st.error("⚠️ هذا المستخدم مسجل مسبقاً!")
        elif os.path.exists(os.path.join(VIDEO_FOLDER, full_video_name)):
            st.error("⚠️ هذا الفيديو تم نشره مسبقاً بنفس العنوان!")
        else:
            # حفظ الفيديو في الهارد G
            with open(os.path.join(VIDEO_FOLDER, full_video_name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # حفظ اسم المستخدم لمنع التكرار
            with open(USER_FILE, "a") as f:
                f.write(username + "\n")
                
            st.success("✅ تم الفحص والنشر بنجاح في الهارد G")
    else:
        st.warning("يرجى ملء جميع البيانات")

# --- عرض الفيديوهات ---
st.header("الفيديوهات المنشورة")
if os.path.exists(VIDEO_FOLDER):
    videos = os.listdir(VIDEO_FOLDER)
    for v in videos:
        st.subheader(f"فيديو: {v}")
        st.video(os.path.join(VIDEO_FOLDER, v))
