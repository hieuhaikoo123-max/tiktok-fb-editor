import os
import subprocess
import ffmpeg
import requests
import streamlit as st

st.set_page_config(page_title="Video Editor", layout="centered")
st.title("Tool Render Video TikTok & Facebook")

url = st.text_input("Dán link TikTok hoặc Facebook vào đây:")
text_follow = st.text_input("Nội dung hiển thị bên dưới:", "Follow for more!")

def download_tiktok(video_url, output_path):
    """Sử dụng TikWM API với Header chuẩn browser"""
    try:
        api_url = "https://www.tikwm.com/api/"
        data = {"url": video_url, "hd": 1}
        
        # Giả lập User-Agent đầy đủ của Chrome trên máy tính
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

        res = requests.post(api_url, data=data, headers=headers, timeout=15).json()

        if res.get("code") == 0:
            play_url = res["data"].get("play") or res["data"].get("wmplay")
            if play_url and not play_url.startswith("http"):
                play_url = "https://www.tikwm.com" + play_url

            video_bytes = requests.get(play_url, headers=headers, timeout=30).content
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            return True
    except Exception as e:
        st.write(f"TikWM Error: {e}")
    return False

def download_tiktok_backup(video_url, output_path):
    """API dự phòng dùng SSSTik nếu TikWM thất bại"""
    try:
        api_url = "https://lovetik.com/api/ajax/search"
        data = {"query": video_url}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        res = requests.post(api_url, data=data, headers=headers, timeout=15).json()
        if res.get("status") == "ok" and res.get("links"):
            # Lấy link tải không watermark
            dl_url = res["links"][0]["a"]
            video_bytes = requests.get(dl_url, headers=headers, timeout=30).content
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            return True
    except Exception as e:
        st.write(f"Backup API Error: {e}")
    return False

def download_generic(video_url, output_path):
    """Dùng yt-dlp dự phòng cho Facebook/nền tảng khác"""
    try:
        cmd = [
            "yt-dlp",
            "-o", output_path,
            "--no-playlist",
            "--format", "mp4",
            "--referer", "https://www.tiktok.com/",
            video_url
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
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

            # Thử lần lượt các phương thức tải
            success = download_tiktok(url, input_file)
            if not success:
                success = download_tiktok_backup(url, input_file)
            if not success:
                success = download_generic(url, input_file)

            if not success:
                st.error("Không thể tải video từ liên kết này. Vui lòng kiểm tra lại đường dẫn!")
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
          
