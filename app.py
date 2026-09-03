import os
import subprocess
import requests
import ffmpeg
import streamlit as st

st.set_page_config(page_title="Video Editor", layout="centered")
st.title("Tool Render Video TikTok & Facebook")

url = st.text_input("Dán link TikTok hoặc Facebook vào đây:")
text_follow = st.text_input("Nội dung hiển thị bên dưới:", "Follow for more!")

def download_with_ytdlp(video_url, output_path):
    """Tải video bằng yt-dlp với cấu hình vượt rào anti-bot"""
    try:
        cmd = [
            "yt-dlp",
            "-o", output_path,
            "--no-playlist",
            "--format", "mp4/best",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--referer", "https://www.tiktok.com/",
            video_url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            st.write(f"Log lỗi yt-dlp: {result.stderr}")
    except Exception as e:
        st.write(f"Lỗi thực thi: {e}")
    return False

def download_tikwm_direct(video_url, output_path):
    """Phương án dự phòng 2"""
    try:
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
        
