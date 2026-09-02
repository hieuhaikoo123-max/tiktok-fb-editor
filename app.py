import os
import ffmpeg
import requests
import streamlit as st

st.set_page_config(page_title="Video Editor", layout="centered")
st.title("Tool Render Video TikTok & Facebook")

url = st.text_input("Dán link TikTok hoặc Facebook vào đây:")
text_follow = st.text_input("Nội dung hiển thị bên dưới:", "Follow for more!")


def download_no_watermark(video_url, output_path):
  api_endpoint = "https://api.cobalt.tools/api/json"
  headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
  }
  payload = {"url": video_url, "videoQuality": "720"}

  try:
    response = requests.post(
        api_endpoint, json=payload, headers=headers, timeout=15
    )
    data = response.json()

    if "url" in data:
      direct_link = data["url"]
      video_bytes = requests.get(direct_link, timeout=30).content
      with open(output_path, "wb") as f:
        f.write(video_bytes)
      return True
    return False
  except Exception as e:
    st.error(f"Lỗi khi tải video: {e}")
    return False


if st.button("Tải & Render Video"):
  if not url:
    st.warning("Vui lòng nhập link video!")
  else:
    with st.spinner("Đang tải và xử lý video... Vui lòng chờ vài giây."):
      input_file = "input.mp4"
      output_file = "output.mp4"

      if os.path.exists(input_file):
        os.remove(input_file)
      if os.path.exists(output_file):
        os.remove(output_file)

      success = download_no_watermark(url, input_file)

      if not success:
        st.error(
            "Không thể tải video từ link này. Vui lòng kiểm tra lại đường"
            " dẫn!"
        )
      else:
        try:
          stream_in = ffmpeg.input(input_file)

          background = stream_in.video.filter(
              "scale", 1080, 1920
          ).filter("boxblur", luma_radius=20, luma_power=2)

          foreground = stream_in.video.filter("scale", "iw*0.7", "ih*0.7")

          processed_video = ffmpeg.overlay(
              background, foreground, x="(W-w)/2", y="H/8"
          ).drawtext(
              text=text_follow,
              x="(w-text_w)/2",
              y="H-H/6",
              fontsize=48,
              fontcolor="white",
              shadowcolor="black",
              shadowx=2,
              shadowy=2,
          )

          out = ffmpeg.output(
              processed_video,
              stream_in.audio,
              output_file,
              vcodec="libx264",
              acodec="aac",
          )
          out.run(overwrite_output=True)

          with open(output_file, "rb") as f:
            st.success("Render hoàn tất!")
            st.download_button(
                label="📲 Tải Video Về Điện Thoại",
                data=f,
                file_name="rendered_video.mp4",
                mime="video/mp4",
            )

        except Exception as e:
          st.error(f"Lỗi trong quá trình render video: {e}")
          
