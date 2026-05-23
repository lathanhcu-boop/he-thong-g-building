import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta, timezone

# Khởi tạo Múi giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="QUẢN LÝ NHÂN SỰ", layout="wide")

URL_NV = "https://docs.google.com/spreadsheets/d/1XoiaAab4uTuHiGw5Q54JF362P--QjQsA/export?format=csv&gid=1095724926"
URL_CV = "https://docs.google.com/spreadsheets/d/1YpMjVzZLsfX9Eedu3rrlDlKiVCHQcNidJK69Pw1wxUo/export?format=csv&gid=2113008419"

DATA_FILE = "lich_su_lam_viec.csv"
ASSIGN_HISTORY_FILE = "phan_cong_data.csv"
ISSUE_FILE = "cong_viec_phat_sinh.csv" # File lưu yêu cầu từ khách hàng

@st.cache_data(ttl=60)
def load_data():
    try:
        df_nv = pd.read_csv(URL_NV)
        df_nv.columns = df_nv.columns.str.strip()
        df_cv = pd.read_csv(URL_CV)
        df_cv.columns = df_cv.columns.str.strip()
        job_dict = df_cv.groupby('KhuVuc')['CongViec'].apply(list).to_dict()
        return df_nv, job_dict
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu từ Google Sheets: {e}")
        return pd.DataFrame(), {}

df_nv, job_list = load_data()

# SỬA LỖI MÚI GIỜ: Cập nhật biến today_str
today_str = datetime.now(VN_TZ).strftime("%Y-%m-%d")

# --- 2. KHỞI TẠO FILE & SESSION STATE ---
def init_files():
    if not os.path.exists(ASSIGN_HISTORY_FILE):
        pd.DataFrame(columns=["Ngày", "Nhân viên", "Khu vực"]).to_csv(ASSIGN_HISTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(ISSUE_FILE):
        pd.DataFrame(columns=["Ngày", "Khu vực", "Nội dung", "Khách hàng", "Trạng thái"]).to_csv(ISSUE_FILE, index=False, encoding='utf-8-sig')
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if 'Ngày' not in df.columns: df['Ngày'] = today_str
        st.session_state.history = df
    else:
        st.session_state.history = pd.DataFrame(columns=["Ngày", "Khu vực", "Công việc", "Nhân viên", "Bắt đầu", "Hoàn thành", "Trạng thái", "Xác nhận", "Thời gian QC"])

init_files()

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
if st.session_state.user is None:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("#### HỆ THỐNG QUẢN LÝ CHẤT LƯỢNG")
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        role_select = st.radio("Đăng nhập với vai trò:", ["Nhân viên", "Giám sát", "Khách hàng"], horizontal=True)
        
        if role_select == "Nhân viên":
            uid = st.text_input("Nhập mã nhân viên:").strip()
            if st.button("Đăng nhập", use_container_width=True):
                match = df_nv[df_nv['MaNV'].astype(str) == uid]
                if not match.empty:
                    st.session_state.user = match.iloc[0]['HoTen']
                    st.session_state.role = "staff"; st.rerun()
                else: st.error("Mã nhân viên không đúng
