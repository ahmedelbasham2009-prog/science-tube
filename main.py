import streamlit as st
import sqlite3
import os
import hashlib

# ==========================================
# ðŸ’¾ 1. Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ù…Ø³Ø§Ø±Ø§Øª ÙˆØ§Ù„Ù‚Ø§Ø¹Ø¯Ø©
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
# ðŸ›¡ï¸ 2. Ù†Ø¸Ø§Ù… Ø§Ù„Ø±Ù‚Ø§Ø¨Ø© Ø§Ù„ÙÙˆÙ„Ø§Ø°ÙŠ Ø§Ù„Ù…Ø­Ø¯Ø« (Ø¥Ø¶Ø§ÙØ© Ù…Ø­Ø¸ÙˆØ±Ø§Øª Ø¬Ø¯ÙŠØ¯Ø©)
# ==========================================
BANNED_WORDS = [
    # Ø£Ù†Ø¯ÙŠØ© ÙˆØ±ÙŠØ§Ø¶Ø© (ØªÙˆØ³ÙŠØ¹ Ø§Ù„Ù†Ø·Ø§Ù‚)
    "Ø§Ù„Ø£Ù‡Ù„ÙŠ", "Ø§Ù„Ø²Ù…Ø§Ù„Ùƒ", "Ø§Ù„Ø¬ÙŠØ´ Ø§Ù„Ù…Ù„ÙƒÙŠ", "Ø§Ù„Ø±Ø¬Ø§Ø¡", "Ø§Ù„ÙˆØ¯Ø§Ø¯", "Ø§Ù„Ù‡Ù„Ø§Ù„", "Ø§Ù„Ù†ØµØ±", "Ø§Ù„Ø§ØªØ­Ø§Ø¯", 
    "Ø±ÙŠØ§Ù„ Ù…Ø¯Ø±ÙŠØ¯", "Ø¨Ø±Ø´Ù„ÙˆÙ†Ø©", "Ù„ÙŠÙØ±Ø¨ÙˆÙ„", "Ù…Ø§Ù†Ø´Ø³ØªØ±", "Ø¨Ø§ÙŠØ±Ù†", "Ù…Ø¨Ø§Ø±Ø§Ø©", "Ù…Ù„Ø®Øµ", "Ø£Ù‡Ø¯Ø§Ù", 
    "Ù‡Ø¯Ù", "ÙƒÙˆØ±Ø©", "ÙƒØ±Ø©", "ÙŠØªØ¹Ø§Ø¯Ù„", "ÙŠÙÙˆØ²", "Ø®Ø³Ø§Ø±Ø©", "Ø¯ÙˆØ±ÙŠ", "ÙƒØ£Ø³", "Ø¨Ø·ÙˆÙ„Ø©", "Ù…Ù†ØªØ®Ø¨", 
    "Ù„Ø§Ø¹Ø¨", "ÙƒØ§Ø¨ØªÙ†", "Ø¶Ø±Ø¨Ø© Ø¬Ø²Ø§Ø¡", "Ø­ÙƒÙ…", "Ù†Ø§Ø¯ÙŠ", "Ø§Ù„Ù…ÙˆÙ†Ø¯ÙŠØ§Ù„",
    # Ù…Ø´Ø§Ù‡ÙŠØ± ÙˆØªØ±ÙŠÙ†Ø¯Ø§Øª ÙˆØªØ±ÙÙŠÙ‡
    "Ù…Ù‚Ø§Ù„Ø¨", "ØªØ­Ø¯ÙŠ", "Ù‡Ø¨Ù„", "Ø¶Ø­Ùƒ", "Ù…Ø³Ø®Ø±Ø©", "Ù„Ø¹Ø¨", "Ø¬ÙŠÙ…ÙŠÙ†Ø¬", "ØªÙŠÙƒ ØªÙˆÙƒ", "Ø¨Ø« Ù…Ø¨Ø§Ø´Ø±", 
    "Ù„Ø§ÙŠÙ", "ÙÙ„ÙˆØ¬", "ÙŠÙˆÙ…ÙŠØ§Øª", "ÙØ¶ÙŠØ­Ø©", "Ø´Ø§Ù‡Ø¯ Ù‚Ø¨Ù„ Ø§Ù„Ø­Ø°Ù", "Ù…Ù‡Ø±Ø¬Ø§Ù†", "Ø£ØºÙ†ÙŠØ©", "ÙƒÙ„ÙŠØ¨", 
    "ÙÙŠÙ„Ù…", "Ù…Ø³Ù„Ø³Ù„", "ØªØ±ÙŠÙ†Ø¯", "Ø¨ÙˆØ¬ÙŠ", "ØªØ§Ù…Ø±", "Ø´ÙŠØ±ÙŠÙ†", "Ù†Ù…Ø¨Ø± ÙˆØ§Ù†", "Ø§ÙƒØªØ³Ø§Ø­",
    # Ù…Ø­ØªÙˆÙ‰ ØºÙŠØ± Ù„Ø§Ø¦Ù‚ Ø£Ùˆ ØºÙŠØ± Ø¹Ù„Ù…ÙŠ
    "Ø³ÙŠØ§Ø³Ø©", "Ø¹Ø§Ø¬Ù„", "Ø®Ø¨Ø±", "Ù…Ø¸Ø§Ù‡Ø±Ø§Øª", "Ø§Ù†ØªØ®Ø§Ø¨Ø§Øª", "Ø±Ø¦ÙŠØ³", "ÙˆØ²ÙŠØ±", "Ø´ØªÙŠÙ…Ø©", "Ù‚Ø°Ø§Ø±Ø©", 
    "Ù‡ÙŠØ§Ø·", "Ø®Ù†Ø§Ù‚Ø©", "Ø¶Ø±Ø¨", "Ø¯Ù…", "Ø±Ø¹Ø¨"
]

def is_scientific(title):
    t = title.strip().lower()
    # 1. Ù…Ù†Ø¹ Ø§Ù„ÙƒÙ„Ù…Ø§Øª Ø§Ù„Ù…Ø­Ø¸ÙˆØ±Ø©
    if any(word in t for word in BANNED_WORDS):
        return False
    # 2. Ù…Ù†Ø¹ Ø§Ù„Ø¹Ù†Ø§ÙˆÙŠÙ† Ø§Ù„Ù‚ØµÙŠØ±Ø© Ø¬Ø¯Ø§Ù‹ (Ø£Ù‚Ù„ Ù…Ù† 10 Ø­Ø±ÙˆÙ ØºØ§Ù„Ø¨Ø§Ù‹ Ù…Ø§ ØªÙƒÙˆÙ† ØºÙŠØ± Ø¬Ø§Ø¯Ø©)
    if len(t) < 10:
        return False
    return True

# ==========================================
# ðŸŽ¨ 3. Ø§Ù„ØªØµÙ…ÙŠÙ… ÙˆØ§Ù„Ø´Ø¹Ø§Ø±
# ==========================================
st.set_page_config(page_title="Science Tube", page_icon="ðŸ”¬", layout="wide")

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
            <span class="micro-img">ðŸ”¬</span>
            <span class="logo-text">Tube</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

all_cats = ["Ø§Ù„ÙƒÙ„", "Ø§Ù„Ø¨Ø±Ù…Ø¬Ø©", "Ø¹Ù„Ø§Ø¬ Ø·Ø¨ÙŠØ¹ÙŠ", "Ø§Ù„ÙÙŠØ²ÙŠØ§Ø¡ Ø§Ù„ØªØ·Ø¨ÙŠÙ‚ÙŠØ©", "Ø§Ù„ÙƒÙŠÙ…ÙŠØ§Ø¡", "Ø§Ù„Ø·Ø¨", "Ø§Ù„ÙØ¶Ø§Ø¡", "Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ", "Ø§Ù„Ø±ÙˆØ¨ÙˆØªØ§Øª", "Ø§Ù„Ø±ÙŠØ§Ø¶ÙŠØ§Øª", "Ø§Ù„Ø¬ÙŠÙˆÙ„ÙˆØ¬ÙŠØ§", "Ø¹Ù„Ù… Ø§Ù„Ù†ÙØ³", "ØªÙƒÙ†ÙˆÙ„ÙˆØ¬ÙŠØ§ Ø§Ù„Ù†Ø§Ù†Ùˆ", "Ø§Ù„Ø£Ø­ÙŠØ§Ø¡ Ø§Ù„Ø¨Ø­Ø±ÙŠØ©", "Ø§Ù„Ù‡Ù†Ø¯Ø³Ø©", "Ø¹Ù„Ù… Ø§Ù„ÙˆØ±Ø§Ø«Ø©", "Ø§Ù„Ø£Ø­Ø§ÙÙŠØ±", "Ø§Ù„Ø·Ø§Ù‚Ø©", "Ø§Ù„Ù…Ù†Ø§Ø®", "Ø§Ù„Ø¨Ø±Ù…Ø¬ÙŠØ§Øª", "Ø§Ù„Ø¥Ù„ÙƒØªØ±ÙˆÙ†ÙŠØ§Øª", "Ø§Ù„Ù…Ù†Ø·Ù‚", "Ø§Ù„ÙƒÙŠÙ…ÙŠØ§Ø¡ Ø§Ù„Ø¹Ø¶ÙˆÙŠØ©", "Ø¹Ù„ÙˆÙ… Ø§Ù„Ø£Ø¹ØµØ§Ø¨"]

if 'my_library' not in st.session_state: st.session_state.my_library = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "Ø²Ø§Ø¦Ø±"
if 'page' not in st.session_state: st.session_state.page = 'home'

# Ø£Ø²Ø±Ø§Ø± Ø§Ù„ØªÙ†Ù‚Ù„
c_n1, c_n2 = st.columns([5, 1])
with c_n1:
    if st.button("ðŸ  Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ©", key="top_h"): st.session_state.page = 'home'; st.rerun()
with c_n2:
    label = f"ðŸš€ {st.session_state.user}" if st.session_state.logged_in else "ðŸ‘¤ Ù…Ù†Ø·Ù‚Ø© Ø§Ù„Ù†Ø§Ø´Ø±ÙŠÙ†"
    if st.button(label, use_container_width=True, key="top_p"): st.session_state.page = 'publisher_area'; st.rerun()

st.divider()

# ==========================================
# ðŸ  4. Ø§Ù„Ù‚Ø§Ø¦Ù…Ø© Ø§Ù„Ø¬Ø§Ù†Ø¨ÙŠØ©
# ==========================================
with st.sidebar:
    st.title("ðŸ§­ Ø§Ù„ØªÙ†Ù‚Ù„")
    sub_nav = st.radio("Ø§Ù„Ù‚Ø§Ø¦Ù…Ø©:", ["ðŸ  Ø§Ù„ÙÙŠØ¯ÙŠÙˆÙ‡Ø§Øª", "ðŸ“š Ù…ÙƒØªØ¨ØªÙŠ Ø§Ù„Ø¹Ù„Ù…ÙŠØ©"], key="sb_nav")
    selected_cat = st.radio("ðŸ“‚ Ø§Ù„Ø£Ù‚Ø³Ø§Ù… Ø§Ù„Ø¹Ù„Ù…ÙŠØ©:", all_cats, key="sb_cats")

# ==========================================
# ðŸ  5. Ø§Ù„ØµÙØ­Ø© Ø§Ù„Ø±Ø¦ÙŠØ³ÙŠØ©
# ==========================================
if st.session_state.page == 'home':
    if sub_nav == "ðŸ  Ø§Ù„ÙÙŠØ¯ÙŠÙˆÙ‡Ø§Øª":
        search_q = st.text_input("ðŸ” Ø§Ø¨Ø­Ø« Ø¹Ù† ÙÙŠØ¯ÙŠÙˆ Ø¹Ù„Ù…ÙŠ...", "", key="search_bar")
        sql = "SELECT * FROM videos WHERE 1=1"
        params = []
        if selected_cat != "Ø§Ù„ÙƒÙ„":
            sql += " AND category=?"; params.append(selected_cat)
        if search_q:
            sql += " AND title LIKE ?"; params.append(f"%{search_q}%")
        
        vids = conn.execute(sql + " ORDER BY id DESC", tuple(params)).fetchall()

        if not vids:
            if search_q: st.warning("Ø¹Ø°Ø±Ø§Ù‹ØŒ Ù„Ù… ÙŠØªÙ… Ø§Ù„Ø¹Ø«ÙˆØ± Ø¹Ù„Ù‰ Ø£ÙŠ Ù…Ø­ØªÙˆÙ‰ ÙŠØ·Ø§Ø¨Ù‚ Ø¨Ø­Ø«Ùƒ..")
            else: st.info("Ù„Ø§ ÙŠÙˆØ¬Ø¯ Ù…Ø­ØªÙˆÙ‰ Ø¹Ù„Ù…ÙŠ Ù…ØªØ§Ø­ Ø­Ø§Ù„ÙŠØ§Ù‹ ÙÙŠ Ù‡Ø°Ø§ Ø§Ù„Ù‚Ø³Ù…..")
        else:
            for v in vids:
                with st.container(border=True):
                    st.subheader(v[1]); st.video(v[2])
                    st.write(f"ðŸ‘ï¸ {v[6]} | âœï¸ {v[3]} | ðŸ“‚ {v[4]}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("ðŸ“š Ø­ÙØ¸", key=f"s_{v[0]}"):
                        if v[0] not in st.session_state.my_library:
                            st.session_state.my_library.append(v[0]); st.success("ØªÙ… Ø§Ù„Ø­ÙØ¸!")
                    if c3.button(f"â¤ï¸ {v[5]}", key=f"l_{v[0]}"):
                        conn.execute("UPDATE videos SET likes=likes+1 WHERE id=?", (v[0],))
                        conn.commit(); st.rerun()

# ==========================================
# ðŸ“Š 6. Ù…Ù†Ø·Ù‚Ø© Ø§Ù„Ù†Ø§Ø´Ø±ÙŠÙ† (Ø¯Ø®ÙˆÙ„ / Ø§Ø³ØªØ¹Ø§Ø¯Ø© / ÙØ­Øµ ÙˆÙ†Ø´Ø±)
# ==========================================
elif st.session_state.page == 'publisher_area':
    if not st.session_state.logged_in:
        t = st.tabs(["ðŸ”‘ Ø¯Ø®ÙˆÙ„", "ðŸ“ ØªØ³Ø¬ÙŠÙ„", "ðŸ” Ø§Ø³ØªØ¹Ø§Ø¯Ø©"])
        with t[0]:
            u = st.text_input("Ø§Ø³Ù… Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…", key="l_u")
            p = st.text_input("ÙƒÙ„Ù…Ø© Ø§Ù„Ù…Ø±ÙˆØ±", type="password", key="l_p")
            if st.button("Ø¯Ø®ÙˆÙ„", key="l_b"):
                res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_pass(p))).fetchone()
                if res: st.session_state.logged_in=True; st.session_state.user=u; st.rerun()
                else: st.error("Ø®Ø·Ø£!")
        with t[1]:
            ru = st.text_input("Ø§Ø³Ù… Ù…Ø³ØªØ®Ø¯Ù… Ø¬Ø¯ÙŠØ¯", key="r_u")
            rp = st.text_input("ÙƒÙ„Ù…Ø© Ø³Ø± Ø¬Ø¯ÙŠØ¯Ø©", type="password", key="r_p")
            if st.button("ØªØ³Ø¬ÙŠÙ„", key="r_b"):
                try:
                    conn.execute("INSERT INTO users VALUES (?,?)", (ru, hash_pass(rp)))
                    conn.commit(); st.success("ØªÙ…!")
                except: st.error("Ù…ÙƒØ±Ø±!")
        with t[2]:
            fu = st.text_input("Ø§Ù„Ø§Ø³Ù… Ù„Ù„Ø§Ø³ØªØ¹Ø§Ø¯Ø©", key="f_u")
            if fu:
                check = conn.execute("SELECT username FROM users WHERE username=?", (fu,)).fetchone()
                if check:
                    np = st.text_input("Ø¨Ø§Ø³ÙˆØ±Ø¯ Ø¬Ø¯ÙŠØ¯", type="password", key="f_p")
                    if st.button("ØªØ­Ø¯ÙŠØ«", key="f_b"):
                        conn.execute("UPDATE users SET password=? WHERE username=?", (hash_pass(np), fu))
                        conn.commit(); st.success("ØªÙ… Ø§Ù„ØªØ­Ø¯ÙŠØ«!")
                else: st.warning("ØºÙŠØ± Ù…ÙˆØ¬ÙˆØ¯")
    else:
        st.subheader(f"Ù„ÙˆØ­Ø© Ø§Ù„ØªØ­ÙƒÙ…: {st.session_state.user}")
        if st.button("ðŸšª Ø®Ø±ÙˆØ¬", key="logout"): st.session_state.logged_in=False; st.rerun()
        st.divider()
        vt = st.text_input("Ø¹Ù†ÙˆØ§Ù† Ø§Ù„ÙÙŠØ¯ÙŠÙˆ Ø§Ù„Ø¹Ù„Ù…ÙŠ", key="v_t")
        vc = st.selectbox("Ø§Ù„Ù‚Ø³Ù…", all_cats[1:], key="v_c")
        vf = st.file_uploader("Ø§Ø±ÙØ¹ MP4", type=["mp4"], key="v_f")
        
        # Ø§Ù„Ø²Ø± Ø§Ù„Ù…Ø·Ù„ÙˆØ¨ Ù…Ø¹ Ù†Ø¸Ø§Ù… Ø§Ù„Ø±Ù‚Ø§Ø¨Ø© Ø§Ù„Ø´Ø§Ù…Ù„
        if st.button("ÙØ­Øµ ÙˆÙ†Ø´Ø± Ø§Ù„ÙÙŠØ¯ÙŠÙˆ", key="v_pub"):
            if vt and vf:
                if not is_scientific(vt):
                    st.error("âš ï¸ Ø§Ù„Ø³ÙŠØ³ØªÙ… Ø±ÙØ¶ Ø§Ù„Ø¹Ù†ÙˆØ§Ù†! Ø§Ù„Ù…Ø­ØªÙˆÙ‰ Ø±ÙŠØ§Ø¶ÙŠØŒ ØªØ±ÙÙŠÙ‡ÙŠ Ø£Ùˆ ØºÙŠØ± Ø¹Ù„Ù…ÙŠ.")
                else:
                    try:
                        path = os.path.join(VIDEOS_DIR, vf.name)
                        with open(path, "wb") as f: f.write(vf.getbuffer())
                        conn.execute("INSERT INTO videos (title, path, author, category) VALUES (?,?,?,?)", (vt, path, st.session_state.user, vc))
                        conn.commit(); st.success("âœ… ØªÙ… Ø§Ù„ÙØ­Øµ ÙˆØ§Ù„Ù†Ø´Ø± Ø¨Ù†Ø¬Ø§Ø­!")
                    except: st.error("Ø§Ù„Ø¹Ù†ÙˆØ§Ù† Ù…ÙƒØ±Ø±!")
                    
