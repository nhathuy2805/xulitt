import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io

st.set_page_config(page_title="Chỉnh sửa ảnh", layout="centered")
st.title("🖼️ Ứng dụng chỉnh sửa ảnh")

if "image" not in st.session_state:
    st.session_state.image = None
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("📤 Tải ảnh lên", type=["png", "jpg", "jpeg"])
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.session_state.image = img.copy()
    st.session_state.history = [img.copy()]

def update_image(new_img):
    st.session_state.image = new_img
    st.session_state.history.append(new_img.copy())

if st.session_state.image:
    st.image(st.session_state.image, caption="Ảnh hiện tại", use_column_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌑 Trắng đen"):
            update_image(st.session_state.image.convert("L").convert("RGB"))
        if st.button("🌫️ Làm mờ"):
            update_image(st.session_state.image.filter(ImageFilter.GaussianBlur(5)))
        if st.button("↔️ Lật ngang"):
            update_image(st.session_state.image.transpose(Image.FLIP_LEFT_RIGHT))
        if st.button("↕️ Lật dọc"):
            update_image(st.session_state.image.transpose(Image.FLIP_TOP_BOTTOM))
    with col2:
        if st.button("🎞️ Vintage"):
            gray = st.session_state.image.convert("L")
            update_image(ImageOps.colorize(gray, "#704214", "#C0C0C0"))
        if st.button("❄️ Lạnh"):
            enhancer = ImageEnhance.Color(st.session_state.image)
            update_image(enhancer.enhance(0.5))
        if st.button("🔥 Ấm"):
            enhancer = ImageEnhance.Color(st.session_state.image)
            update_image(enhancer.enhance(1.5))
        if st.button("☀️ Tăng sáng"):
            enhancer = ImageEnhance.Brightness(st.session_state.image)
            update_image(enhancer.enhance(1.5))
    with col3:
        if st.button("🎚️ Tăng tương phản"):
            enhancer = ImageEnhance.Contrast(st.session_state.image)
            update_image(enhancer.enhance(1.5))
        if st.button("🔎 Làm nét"):
            update_image(st.session_state.image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)))
        if st.button("🔄 Xoay 90°"):
            update_image(st.session_state.image.rotate(90, expand=True))
        if st.button("✂️ Cắt ảnh"):
            w, h = st.session_state.image.size
            left = w // 4
            top = h // 4
            right = w * 3 // 4
            bottom = h * 3 // 4
            update_image(st.session_state.image.crop((left, top, right, bottom)))

    st.write("🎨 **Tách kênh màu RGB:**")
    channel = st.radio("Chọn kênh", ("R", "G", "B"), horizontal=True)
    if st.button("Tách kênh"):
        r, g, b = st.session_state.image.split()
        if channel == "R":
            merged = Image.merge("RGB", (r, Image.new("L", r.size), Image.new("L", r.size)))
        elif channel == "G":
            merged = Image.merge("RGB", (Image.new("L", g.size), g, Image.new("L", g.size)))
        else:
            merged = Image.merge("RGB", (Image.new("L", b.size), Image.new("L", b.size), b))
        update_image(merged)

    if len(st.session_state.history) > 1:
        if st.button("↩️ Quay lại"):
            st.session_state.history.pop()
            st.session_state.image = st.session_state.history[-1]

    img_bytes = io.BytesIO()
    st.session_state.image.save(img_bytes, format="PNG")
    st.download_button("📥 Tải ảnh về", data=img_bytes.getvalue(), file_name="edited.png", mime="image/png")