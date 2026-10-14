
# Script-to-Video Generator 🎬

A Python application that transforms a written script into a narrated video using AI-generated scene images.

The application provides a simple Streamlit interface to analyze scripts, divide them into scenes, generate visuals locally with OpenVINO, create voice-over narration, and combine everything into an MP4 video.

## ✨ Features

- **Script analysis:** Count words and characters and estimate video duration.
- **Scene breakdown:** Split a script into individual scenes using blank lines.
- **Editable scenes:** Review and modify each scene before generating visuals.
- **AI image generation:** Generate scene images locally using OpenVINO GenAI.
- **Voice-over generation:** Convert the updated script into narration using pyttsx3.
- **Video creation:** Combine scene images and narration into an MP4 video.
- **Preview and download:** Play and download the generated video through the application.
- **Local processing:** Run image generation on your own computer with a compatible OpenVINO GPU setup.

## 🛠️ Technologies Used

- Python
- Streamlit
- OpenVINO GenAI
- Stable Diffusion 1.5 INT8 OpenVINO model
- Pillow
- pyttsx3
- MoviePy

## 📁 Project Structure

```text
script-to-video-generator/
├── day1_UI.py
├── app.py
├── day2_practice.py
├── test_image.py
├── test_voice.py
├── requirements.txt
├── .gitignore
├── README.md
├── output/                      # Generated media; excluded from Git
└── stable-diffusion-v1-5-int8-ov/ # Local model; excluded from Git
```

The `.venv-image/` virtual environment is also kept locally and excluded from Git.

## ⚙️ Prerequisites

- Windows computer
- Python installed
- Git installed
- A compatible OpenVINO environment and supported GPU
- The required OpenVINO GenAI model available locally

The AI model is not included in this repository. You must obtain the compatible model separately and place it in the expected local model directory before running image generation.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/lakhwinder1495/script-to-video-generator.git
cd script-to-video-generator
```

### 2. Create and activate a virtual environment

In PowerShell:

```powershell
python -m venv .venv-image
.\.venv-image\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow your system's Python environment guidance or activate the environment through VS Code.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The OpenVINO packages and GPU configuration must be compatible with your system. Dependency installation alone does not guarantee that GPU image generation will work.

### 4. Prepare the local AI model

Place the compatible OpenVINO Stable Diffusion model in:

```text
stable-diffusion-v1-5-int8-ov/
```

The application currently loads this directory and requests the `GPU` device.

### 5. Run the application

```bash
streamlit run day1_UI.py
```

Streamlit will provide a local URL to open in your browser.

## 📝 How to Use

1. Enter a script in the text area.
2. Separate scenes with a blank line.
3. Click **Analyze Script**.
4. Review and edit the scene text.
5. Generate an image for each scene or use **Generate All Scene Images**.
6. Generate the voice-over.
7. Click **Create Video**.
8. Preview and download the MP4 video.

## 📂 Generated Files

Generated assets are stored in the local `output/` directory:

- `scene_1.png`, `scene_2.png`, and other scene images
- `voiceover.wav`
- `first_video.mp4`

These files are excluded from Git tracking.

## ⚠️ Current Limitations

- Image generation requires a compatible local OpenVINO model and supported hardware.
- Generated scene images are currently slideshow-style visuals rather than animated scenes.
- Narration duration is divided equally across the generated scene images.
- Scene boundaries are determined by blank lines in the script.
- Dependency and hardware compatibility may vary between computers.

## 🔮 Future Improvements

- Improve scene-to-narration timing.
- Add background music and transitions.
- Improve scene prompt generation.
- Add configurable video resolution and aspect ratio.
- Improve error handling and progress reporting.
- Provide a more flexible model and device configuration.

## 👩‍💻 Author

**Lakhwinder Kaur**

GitHub: [@lakhwinder1495](https://github.com/lakhwinder1495)
