import streamlit as st
import openvino_genai
from PIL import Image
import pyttsx3
from pathlib import Path
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def count_words(text):
    return len(text.split())


def estimate_video_minutes(word_count):
    return round(word_count / 130, 1)


def classify_script(word_count):
    if word_count < 50:
        return "Short script"
    elif word_count < 200:
        return "Medium script"
    else:
        return "Long script"


def split_into_scenes(text):
    return [
        scene.strip()
        for scene in text.replace("\r\n", "\n").split("\n\n")
        if scene.strip()
    ]


def create_image_prompt(scene_text):
    return (
        f"Create a cinematic video scene showing: {scene_text}. "
        "Use realistic lighting, clear composition, detailed visuals, "
        "and a widescreen 16:9 aspect ratio."
    )


@st.cache_resource
def load_image_pipeline():
    return openvino_genai.Text2ImagePipeline(
        "stable-diffusion-v1-5-int8-ov",
        "GPU",
    )


st.title("My Script Analyzer")
st.write("Welcome! Let's analyze your video script")

# Initialize session state.
if "analyzed_script" not in st.session_state:
    st.session_state.analyzed_script = ""

if "scene_count" not in st.session_state:
    st.session_state.scene_count = 0

# Script input.
script_input = st.text_area(
    "Enter your video script",
    placeholder="Write your script here...",
    key="script_input",
)

# Analyze button.
if st.button("Analyze Script", key="analyze_script"):
    if script_input.strip():
        scenes = split_into_scenes(script_input)
        st.session_state.analyzed_script = script_input
        st.session_state.scene_count = len(scenes)

        # Clear old edits and generated assets for the previous script.
        for key in list(st.session_state.keys()):
            if key.startswith("scene_edit_") or key.startswith("scene_image_"):
                del st.session_state[key]

        st.session_state.pop("voiceover_path", None)
        st.session_state.pop("voiceover_script", None)

        # Store each scene so edits survive Streamlit reruns.
        for index, scene in enumerate(scenes):
            st.session_state[f"scene_edit_{index}"] = scene
    else:
        st.warning("Please enter a script first.")

# Display results after a script has been analyzed.
if st.session_state.analyzed_script:
    original_script = st.session_state.analyzed_script

    st.subheader("Script Analysis")
    original_word_count = count_words(original_script)
    original_characters = len(original_script)
    original_video_minutes = estimate_video_minutes(original_word_count)
    original_script_type = classify_script(original_word_count)

    col1, col2, col3 = st.columns(3)
    col1.metric("Original Words", original_word_count)
    col2.metric("Original Characters", original_characters)
    col3.metric("Estimated Duration", f"{original_video_minutes} min")
    st.info(f"Original script category: {original_script_type}")

    # Editable scenes.
    st.subheader("Scene Breakdown")
    st.write("Total scenes:", st.session_state.scene_count)
    edited_scenes = []

    for scene_number in range(1, st.session_state.scene_count + 1):
        scene_index = scene_number - 1
        st.markdown(f"**Scene {scene_number}**")
        edited_scene = st.text_area(
            f"Edit Scene {scene_number}",
            key=f"scene_edit_{scene_index}",
        )
        edited_scenes.append(edited_scene)
        st.divider()

    # Build the updated script on every rerun, outside button blocks.
    updated_script = "\n\n".join(edited_scenes)

    st.subheader("Updated Script Analysis")
    updated_word_count = count_words(updated_script)
    updated_characters = len(updated_script)
    updated_video_minutes = estimate_video_minutes(updated_word_count)
    updated_script_type = classify_script(updated_word_count)

    col1, col2, col3 = st.columns(3)
    col1.metric("Words", updated_word_count)
    col2.metric("Characters", updated_characters)
    col3.metric("Estimated Duration", f"{updated_video_minutes} min")
    st.info(f"Updated script category: {updated_script_type}")

    st.subheader("Updated Script Preview")
    st.text_area(
        "Your revised video script",
        value=updated_script,
        height=200,
        disabled=True,
        key="updated_script_preview",
    )

    # Image prompt and individual image-generation controls.
    st.subheader("Scene Visual Prompts")
    for scene_number, scene_text in enumerate(edited_scenes, start=1):
        st.markdown(f"**Scene {scene_number}**")
        prompt = create_image_prompt(scene_text)
        st.write("Visual prompt:", prompt)

        if st.button(
            f"Generate Image for Scene {scene_number}",
            key=f"generate_image_{scene_number}",
        ):
            if not scene_text.strip():
                st.warning(f"Scene {scene_number} is empty. Add text first.")
            else:
                with st.spinner(f"Generating image for Scene {scene_number}..."):
                    pipe = load_image_pipeline()
                    image_tensor = pipe.generate(
                        prompt,
                        width=512,
                        height=512,
                        num_inference_steps=20,
                        num_images_per_prompt=1,
                    )
                    image = Image.fromarray(image_tensor.data[0])
                    image_path = OUTPUT_DIR / f"scene_{scene_number}.png"
                    image.save(image_path)
                    st.session_state[f"scene_image_{scene_number}"] = image_path

    # This button is outside the scene loop, so it appears only once.
    if st.button("Generate All Scene Images", key="generate_all_scene_images"):
        scenes_to_generate = [
            (scene_number, scene_text)
            for scene_number, scene_text in enumerate(edited_scenes, start=1)
            if scene_text.strip()
            and f"scene_image_{scene_number}" not in st.session_state
        ]

        if not scenes_to_generate:
            st.info(
                "All non-empty scenes already have images. "
                "Use an individual scene button to regenerate an image."
            )
        else:
            pipe = load_image_pipeline()
            for scene_number, scene_text in scenes_to_generate:
                prompt = create_image_prompt(scene_text)
                with st.spinner(f"Generating image for Scene {scene_number}..."):
                    image_tensor = pipe.generate(
                        prompt,
                        width=512,
                        height=512,
                        num_inference_steps=20,
                        num_images_per_prompt=1,
                    )
                    image = Image.fromarray(image_tensor.data[0])
                    image_path = OUTPUT_DIR / f"scene_{scene_number}.png"
                    image.save(image_path)
                    st.session_state[f"scene_image_{scene_number}"] = image_path
            st.success("All missing scene images are ready!")

    # Display images that have been generated.
    st.subheader("Generated Scene Images")
    has_any_image = False
    for scene_number, _scene_text in enumerate(edited_scenes, start=1):
        image_path = st.session_state.get(f"scene_image_{scene_number}")
        if image_path:
            has_any_image = True
            st.image(
                image_path,
                caption=f"Generated image for Scene {scene_number}",
                width=400,
            )
    if not has_any_image:
        st.caption("Generate an image for one scene or use Generate All Scene Images.")

    # Voice-over controls use the current updated script.
    st.subheader("Voice-over")
    if st.button("Generate Voice-over", key="generate_voiceover"):
        if updated_script.strip():
            with st.spinner("Generating voice-over..."):
                
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)

                audio_path = OUTPUT_DIR / "voiceover.wav"

                st.write("Preparing narration...")
                engine.save_to_file(
                    updated_script,
                    str(audio_path)
                )

                st.write("Converting text to speech...")
                engine.runAndWait()
                engine.stop()

                st.write("Voice generation finished.")

                st.session_state["voiceover_path"] = audio_path
                st.session_state["voiceover_script"] = updated_script
            st.success("Voice-over generated successfully!")
        else:
            st.warning("Please enter some script text before generating narration.")

    # Only show audio if it was generated from the current script.
    if (
        st.session_state.get("voiceover_path")
        and st.session_state.get("voiceover_script") == updated_script
    ):
        st.audio(st.session_state["voiceover_path"])
        with open(st.session_state["voiceover_path"], "rb") as audio_file:
            st.download_button(
                "Download Voice-over",
                data=audio_file.read(),
                file_name="voiceover.wav",
                mime="audio/wav",
            )
    
    # -------------------------------
    # VIDEO CREATION
    # -------------------------------

    st.header("🎬 Create Your Video")

    st.write(
        "Combine your generated scene images "
        "and voiceover into a single MP4 video."
    )

    if st.button("Create Video", type="primary"):

        audio_path = OUTPUT_DIR / "voiceover.wav"
        output_path = OUTPUT_DIR / "first_video.mp4"

        # Find the generated scene images in order
        
        # Use only images generated for the current script
        image_paths = []

        for scene_number in range(1, st.session_state.scene_count + 1):
            image_path = st.session_state.get(
                f"scene_image_{scene_number}"
            )

            if image_path and Path(image_path).exists():
                image_paths.append(Path(image_path))


        if not image_paths:
            st.error(
                "No scene images found. "
                "Generate your scene images first."
            )

        elif not audio_path.exists():
            st.error(
                "Voiceover not found. "
                "Generate your voiceover first."
            )

        else:
            clips = []
            audio_clip = None
            final_clip = None

            try:
                with st.spinner(
                    "Creating your video... Please wait."
                ):
                    audio_clip = AudioFileClip(str(audio_path))

                    # Divide narration duration across scenes
                    scene_weights = []

                    for image_path in image_paths:
                        scene_weights.append(1)

                    total_weight = sum(scene_weights)

                    for image_path, weight in zip(
                        image_paths, scene_weights
                    ):
                        duration = (
                            audio_clip.duration
                            * weight
                            / total_weight
                        )

                        clip = (
                            ImageClip(str(image_path))
                            .with_duration(duration)
                        )

                        clips.append(clip)

                    # Join all scene images
                    video_clip = concatenate_videoclips(
                        clips,
                        method="compose"
                    )

                    # Attach the narration
                    final_clip = video_clip.with_audio(
                        audio_clip
                    )

                    # Export MP4
                    final_clip.write_videofile(
                        str(output_path),
                        fps=24,
                        codec="libx264",
                        audio_codec="aac",
                        logger=None
                    )

                st.success("Your video has been created!")

            except Exception as error:
                st.error(f"Video creation failed: {error}")

            finally:
                if final_clip is not None:
                    final_clip.close()

                for clip in clips:
                    clip.close()

                if audio_clip is not None:
                    audio_clip.close()

    # Preview and download the generated video
    if Path(OUTPUT_DIR /"first_video.mp4").exists():
        st.subheader("Your Generated Video")

        st.video(OUTPUT_DIR /"first_video.mp4")

        with open(OUTPUT_DIR /"first_video.mp4", "rb") as video_file:
            st.download_button(
                label="Download Video",
                data=video_file.read(),
                file_name="first_video.mp4",
                mime="video/mp4"
            )

    elif st.session_state.get("voiceover_path"):
        st.info("Your script has changed. Generate the voice-over again to match it.")
