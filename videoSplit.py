# videoSplit
import os
import shutil
import cv2
import logging
import tkinter as tk
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import numpy as np
import subprocess
import sys
print(sys.executable)
print(sys.argv[1])
# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
snippet_duration = int(sys.argv[2])
print(sys.argv[2])
def call_joycaption(grids_folder):
    env = os.environ.copy()
    python_executable = sys.executable  # Use the current Python interpreter
    subprocess.run([python_executable, "joyCaption.py", grids_folder], env=env)

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder with Videos")
    logging.info(f"Selected input folder: {folder_selected}")
    return folder_selected


def split_video(input_path, output_dir, segment_duration=snippet_duration):
    os.makedirs(output_dir, exist_ok=True)
    video = VideoFileClip(input_path)
    width, height = video.size  # Get video dimensions
    aspect_ratio = width / height  # Maintain original aspect ratio

    video_duration = int(video.duration)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    logging.info(f"Splitting video: {input_path} into {segment_duration}-second snippets")

    for start_time in range(0, video_duration, segment_duration):
        end_time = min(start_time + segment_duration, video_duration)
        segment = video.subclipped(start_time, end_time)  # Updated for MoviePy 2.0
        output_path = os.path.join(output_dir, f"{base_name}_part{start_time}-{end_time}.mp4")
        segment.write_videofile(output_path, codec='libx264', audio_codec='aac')
        logging.info(f"Created segment: {output_path}")


def extract_frames(video_path, frame_interval=6):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_count += 1

    cap.release()
    logging.info(f"Extracted {len(frames)} frames from {video_path}")
    return frames


def create_image_grid(frames, grid_size=(3, 3), output_path=None):
    assert len(frames) >= grid_size[0] * grid_size[1], "Not enough frames to fill the grid."
    frames = frames[:grid_size[0] * grid_size[1]]
    max_width = max(frame.shape[1] for frame in frames)
    max_height = max(frame.shape[0] for frame in frames)

    grid_image = Image.new('RGB', (grid_size[1] * max_width, grid_size[0] * max_height), (255, 255, 255))

    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        row = i // grid_size[1]
        col = i % grid_size[1]
        x_offset = col * max_width + (max_width - img.width) // 2
        y_offset = row * max_height + (max_height - img.height) // 2
        grid_image.paste(img, (x_offset, y_offset))

    if output_path:
        grid_image.save(output_path)
        logging.info(f"Created image grid: {output_path}")


def process_videos(input_folder):
    output_folder = os.path.join(input_folder, "snippets")
    grid_folder = os.path.join(input_folder, "grids")
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(grid_folder, exist_ok=True)

    for video_file in os.listdir(input_folder):
        if video_file.endswith('.mp4'):
            video_path = os.path.join(input_folder, video_file)
            base_name = os.path.splitext(video_file)[0]
            segment_folder = os.path.join(output_folder, base_name)
            os.makedirs(segment_folder, exist_ok=True)

            split_video(video_path, segment_folder)

            for segment_file in os.listdir(segment_folder):
                if segment_file.endswith('.mp4'):
                    segment_path = os.path.join(segment_folder, segment_file)
                    frames = extract_frames(segment_path)
                    if len(frames) >= 9:
                        grid_output_path = os.path.join(grid_folder, f"{os.path.splitext(segment_file)[0]}.jpg")
                        create_image_grid(frames, output_path=grid_output_path)

    logging.info("Video processing complete. You can check the original folder for snippets and grids.")
    logging.info("Now let's caption the videos...")
    call_joycaption(grid_folder)


if __name__ == "__main__":
    input_folder = sys.argv[1]
    if input_folder:
        process_videos(input_folder)
