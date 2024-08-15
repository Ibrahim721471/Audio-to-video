from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from moviepy.editor import AudioFileClip, ColorClip, concatenate_videoclips
import os

# Create a directory for uploads and output if not exist
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Helper function to split audio and create green background video
def split_audio_to_video(audio_path):
    video_clips = []
    audio_clip = AudioFileClip(audio_path)
    duration = 58  # 58 seconds per clip

    # Calculate how many segments we need
    for i in range(0, int(audio_clip.duration), duration):
        segment = audio_clip.subclip(i, min(i + duration, audio_clip.duration))
        
        # Create a green screen background video
        green_clip = ColorClip(size=(1280, 720), color=(0, 255, 0), duration=segment.duration)
        
        # Set the audio of the green background
        green_clip = green_clip.set_audio(segment)
        
        # Save this clip to the video_clips list
        video_clips.append(green_clip)

    return video_clips

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Save uploaded file
        if 'audio' not in request.files:
            return "No file part"
        
        file = request.files['audio']
        if file.filename == '':
            return "No selected file"

        # Save the uploaded audio file
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(audio_path)

        # Process the audio into videos
        video_clips = split_audio_to_video(audio_path)
        
        # Export the videos as individual clips
        video_paths = []
        for idx, clip in enumerate(video_clips):
            video_output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'video_part_{idx+1}.mp4')
            clip.write_videofile(video_output_path, codec='libx264')
            video_paths.append(video_output_path)
        
        return render_template('index.html', video_paths=video_paths)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
