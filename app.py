import os
import subprocess
import streamlit as st

st.set_page_config(page_title="Render Video Shorts/Reels", layout="centered")
st.title("🎬 Tool Render Video Tự Động")

uploaded_file = st.file_uploader("Chọn video MP4 từ điện thoại", type=["mp4", "mov", "mkv"])

sub_text = st.text_input("Nội dung chữ bên dưới video:", value="FOLLOW")

if uploaded_file is not None:
    st.video(uploaded_file)
    
    input_path = "input_raw.mp4"
    output_path = "output_follow.mp4"
    
    if st.button("🚀 Bắt đầu Render Video"):
        with st.spinner("Đang xử lý thu nhỏ, làm mờ nền và chèn FOLLOW... Vui lòng đợi!"):
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if os.path.exists(output_path):
                os.remove(output_path)
            
            filter_complex = (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
                "[0:v]scale=756:-2[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2-160[v1];"
                f"[v1]drawtext=text='{sub_text}':fontcolor=yellow:fontsize=52:bordercolor=black:borderw=3:"
                "x=(w-text_w)/2:y=h/2+330:box=1:boxcolor=white:boxborderw=18[v]"
            )
            
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "0:a?",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                st.success("🎉 Render hoàn tất!")
                st.video(output_path)
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Tải video về máy",
                        data=file,
                        file_name="video_rendered.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("Render gặp lỗi! Chi tiết:")
                st.code(process.stderr)
                
