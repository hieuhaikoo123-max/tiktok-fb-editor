import os
import subprocess
import streamlit as st

st.set_page_config(page_title="Render Video Shorts/Reels", layout="centered")
st.title("🎬 Tool Render Video Tự Động")

uploaded_file = st.file_uploader("Chọn video MP4 từ điện thoại", type=["mp4", "mov", "mkv"])

# Tuỳ chọn chữ ở bên dưới (mặc định là FOLLOW)
sub_text = st.text_input("Nội dung chữ bên dưới video:", value="FOLLOW")

if uploaded_file is not None:
    st.video(uploaded_file)
    
    input_path = "input_raw.mp4"
    output_path = "output_follow.mp4"
    
    if st.button("🚀 Bắt đầu Render Video"):
        with st.spinner("Đang xử lý thu nhỏ, làm mờ nền và chèn FOLLOW... Vui lòng đợi!"):
            # 1. Lưu file tạm
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Xóa file output cũ nếu có
            if os.path.exists(output_path):
                os.remove(output_path)
            
            # 2. Bộ lọc FFmpeg:
            # - Tạo nền 1080x1920 làm mờ bằng boxblur
            # - Video chính thu nhỏ 70% (scale=1080*0.7:-2 = 756px), kéo lên trên y=(H-h)/2 - 150
            # - Vẽ nút FOLLOW: hộp trắng box=1, chữ vàng fontcolor=yellow, viền chữ đen borderw=3
            filter_complex = (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
                "[0:v]scale=756:-2[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2-160[v1];"
                f"[v1]drawtext=text='{sub_text}':fontcolor=yellow:fontsize=52:bordercolor=black:borderw=3:"
                "x=(w-text_w)/2:y=h/2+330:box=1:boxcolor=white:boxborderw=18[v]"
            )
            
            # 3. Chạy FFmpeg
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
            
            # 4. Hiển thị kết quả
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
            else:
                st.error("Render thất bại! Vui lòng kiểm tra lại.")
        api_url = f"https://www.tikwm.com/api/?url={video_url}"
        res = requests.get(api_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }, timeout=10).json()
        
        if res.get("code") == 0:
            play_url = res["data"]["play"]
            if not play_url.startswith("http"):
                play_url = "https://www.tikwm.com" + play_url
            video_data = requests.get(play_url, timeout=20).content
            with open(output_path, "wb") as f:
                f.write(video_data)
            return True
    except Exception:
        pass
    return False

if st.button("Tải & Render Video"):
    if not url:
        st.warning("Vui lòng nhập link video!")
    else:
        with st.spinner("Đang tải và xử lý video... Vui lòng chờ chút nhé."):
            input_file = "input.mp4"
            output_file = "output.mp4"

            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)

            # Thử tải video
            success = download_with_ytdlp(url, input_file)
            if not success:
                success = download_tikwm_direct(url, input_file)

            if not success:
                st.error("Không thể tải video. Hãy kiểm tra phần log thông báo ở trên để biết nguyên nhân cụ thể!")
            else:
                try:
                    stream_in = ffmpeg.input(input_file)

                    # Khung nền Blur
                    background = stream_in.video.filter("scale", 1080, 1920).filter("boxblur", luma_radius=20, luma_power=2)

                    # Video chính co lại 70%
                    foreground = stream_in.video.filter("scale", "iw*0.7", "ih*0.7")

                    # Ghép lớp & Chèn chữ
                    processed_video = ffmpeg.overlay(background, foreground, x="(W-w)/2", y="H/8").drawtext(
                        text=text_follow,
                        x="(w-text_w)/2",
                        y="H-H/6",
                        fontsize=48,
                        fontcolor="white",
                        shadowcolor="black",
                        shadowx=2,
                        shadowy=2
                    )

                    out = ffmpeg.output(processed_video, stream_in.audio, output_file, vcodec="libx264", acodec="aac")
                    out.run(overwrite_output=True)

                    with open(output_file, "rb") as f:
                        st.success("Render hoàn tất!")
                        st.download_button(
                            label="📲 Tải Video Về Điện Thoại",
                            data=f,
                            file_name="rendered_video.mp4",
                            mime="video/mp4"
                        )

                except Exception as e:
                    st.error(f"Lỗi khi render video: {e}")
        
