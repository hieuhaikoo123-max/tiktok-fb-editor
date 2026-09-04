import os
import subprocess
import streamlit as st

st.set_page_config(page_title="Render Video MP4")
st.title("Công cụ render video từ file MP4")

# 1. Chọn file MP4 từ bộ nhớ điện thoại
uploaded_file = st.file_uploader("Chọn video MP4 từ máy:", type=["mp4", "mov", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    input_path = "input_temp.mp4"
    output_path = "output_rendered.mp4"
    
    if st.button("🚀 Bắt đầu Render"):
        with st.spinner("Đang render video... Vui lòng đợi!"):
            # Lưu tạm video vào máy
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Lệnh FFmpeg xử lý video (thêm -preset ultrafast để render nhanh trên điện thoại)
            cmd = f'ffmpeg -y -i "{input_path}" -c:v libx264 -preset ultrafast -c:a aac "{output_path}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(output_path):
                st.success("Render hoàn tất!")
                # Nút tải video kết quả về điện thoại
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Tải video đã render về máy",
                        data=file,
                        file_name="video_rendered.mp4",
                        mime="video/mp4"
                    )
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
        
