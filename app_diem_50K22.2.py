import pandas as pd
import streamlit as st
import os

# 1. Tự động tìm file Excel trong thư mục (để tránh sai tên file)
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
FILE_PATH = excel_files[0] if excel_files else 'ELC3020_50K22_2_Diem.xlsx'

# Danh sách cột điểm (Cập nhật theo file lớp 50K22.2 - KHÔNG CÓ Điểm danh 2)
SCORE_COLUMNS = [
    'Điểm danh 1', 
    'Kiểm tra chương 1', 
    'Kiểm tra tiền xử lý dữ liệu', 
    'Kiểm tra data mining', 
    'Điểm cộng',
    'Thành phần 1',
    'Thành phần 1 chính thức (nếu Thành phần 1 > 10 thì lấy 10)',
    'Biểu đồ nâng cao (15% TP2)', 
    'Tư duy phân tích và xây dựng dashboard (15% TP2)',
    'Thi giữa kỳ (70% TP2)', 
    'Thành phần 2',
    'Điểm dư từ TP1',
    'Thành phần 2 chính thức = Thành phần 2 + Điểm dư từ TP1/3'
]

# Danh sách các cột cần bôi đậm (4 cột điểm tổng kết)
HIGHLIGHT_COLUMNS = [
    'Thành phần 1',
    'Thành phần 1 chính thức (nếu Thành phần 1 > 10 thì lấy 10)',
    'Thành phần 2',
    'Thành phần 2 chính thức = Thành phần 2 + Điểm dư từ TP1/3'
]

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH)
        # Xóa khoảng trắng thừa trong tên cột
        df.columns = df.columns.str.strip()
        
        # Chuyển MSSV sang chuỗi và xóa khoảng trắng
        df['MSSV'] = df['MSSV'].astype(str).str.strip()
        
        # Ghép tên (Dùng cột Họ và tên đệm và Tên)
        df['Họ và Tên'] = df['Họ và tên đệm'].fillna('') + " " + df['Tên'].fillna('')
        
        # Làm tròn 1 chữ số thập phân cho các cột điểm
        for col in SCORE_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(1)
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return None

# Hàm bôi đen và tô màu dòng quan trọng
def highlight_row(row):
    # Kiểm tra nếu tên thành phần nằm trong danh sách cần bôi đậm
    if any(col in row['Thành phần'] for col in HIGHLIGHT_COLUMNS):
        return ['background-color: #ffe6cc; font-weight: bold; color: #000000'] * len(row)
    return [''] * len(row)

# --- GIAO DIỆN ---
st.set_page_config(page_title="Tra cứu điểm ELC3020 - Lớp 50K22.2", layout="centered")
st.title('📊 Tra cứu Điểm ELC3020 - Lớp 50K22.2')
st.info("Khoa Thương mại điện tử - Đại học Kinh tế Đà Nẵng")

df = load_data()

if df is not None:
    mssv_input = st.text_input('Nhập Mã số sinh viên (MSSV):', placeholder='Ví dụ: 221121330159')

    if st.button('Xem kết quả', type="primary") or mssv_input:
        if mssv_input:
            # Tra cứu chính xác
            result = df[df['MSSV'] == mssv_input.strip()]
            
            if not result.empty:
                student = result.iloc[0]
                st.success(f"Sinh viên: **{student['Họ và Tên']}**")
                
                c1, c2 = st.columns(2)
                c1.write(f"**Lớp:** {student['Lớp']}")
                c2.write(f"**MSSV:** {student['MSSV']}")
                
                st.divider()

                 # Thêm phần lưu ý về tỉ lệ điểm
                st.warning("• Tỉ lệ cột điểm **Thành phần 1 chính thức**: **10%**\n\n"
                           "• Tỉ lệ cột điểm **Thành phần 2 chính thức**: **30%**")
                
                # Chuẩn bị bảng điểm dọc
                display_list = []
                for col in SCORE_COLUMNS:
                    if col in df.columns:
                        val = student[col]
                        # Format điểm: nếu có giá trị thì làm tròn 1 chữ số thập phân
                        if pd.notna(val):
                            formatted_val = f"{val:.1f}"
                        else:
                            formatted_val = "-"
                        display_list.append({
                            "Thành phần": col, 
                            "Điểm số": formatted_val
                        })
                
                score_df = pd.DataFrame(display_list)
                
                # Áp dụng bôi đậm cho 4 cột điểm tổng kết
                styled_df = score_df.style.apply(highlight_row, axis=1)
                st.table(styled_df)
            else:
                st.error("Không tìm thấy MSSV này. Bạn vui lòng kiểm tra lại.")
        else:
            st.warning("Vui lòng nhập MSSV.")

st.divider()
st.caption("© 2026 - Giảng viên: Đỗ Hoàng Thu - DUE")
