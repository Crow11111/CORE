# HA Configuration for Scout MX Brio (via go2rtc)
# Add this to your HA configuration.yaml

camera:
  - platform: generic
    name: "Scout MX"
    still_image_url: "http://<SCOUT_IP>:1984/api/frame.jpeg?src=mx_brio"
    stream_source: "rtsp://<SCOUT_IP>:8554/mx_brio"
    verify_ssl: false

# Alternative (Passive/Raw FFmpeg - less efficient):
# camera:
#   - platform: ffmpeg
#     input: /dev/video0
#     name: "Scout MX Raw"
