
import streamlit as st
from ollama import chat

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Script to Video Generator",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Script to Video Generator")
st.write(
    "Turn your script into scenes and generate "
    "AI-powered image prompts."
)

# --------------------------------------------------
# Script input
# --------------------------------------------------

st.subheader("1. Enter Your Script")

uploaded_file = st.file_uploader(
    "Upload your script (.txt)",
    type=["txt"],
    key="script_file"
)

script_input = st.text_area(
    "Or paste your script here",
    height=220,
    placeholder=(
        "Write or paste your video script here...\n\n"
        "Leave a blank line between paragraphs."
    ),
    key="script_input"
)

# --------------------------------------------------
# Character and visual settings
# --------------------------------------------------

st.subheader("2. Character and Visual Settings")

character_description = st.text_input(
    "Main character description",
    placeholder=(
        "A tiny orange kitten with white paws "
        "and large green eyes"
    ),
    key="character_description"
)

visual_style = st.selectbox(
    "Visual style",
    [
        "3D animated movie style",
        "Children's storybook illustration",
        "Realistic cinematic style",
        "Anime style"
    ],
    key="visual_style"
)

# --------------------------------------------------
# Generate scenes and prompts
# --------------------------------------------------

if st.button("Generate Scenes and Prompts", type="primary"):

    # Read script
    if uploaded_file is not None:
        try:
            script = uploaded_file.getvalue().decode("utf-8-sig")
        except UnicodeDecodeError:
            st.error(
                "Could not read the file. Please save it "
                "as a UTF-8 encoded .txt file."
            )
            st.stop()
    else:
        script = script_input

    if not script.strip():
        st.warning("Please enter a script or upload a text file.")
        st.session_state.pop("generated_scenes", None)
        st.stop()

    # Split script into scenes using blank lines
    scenes = [
        paragraph.strip()
        for paragraph in script.split("\n\n")
        if paragraph.strip()
    ]
    

    character = (
        character_description.strip()
        or "The main character described in the scene"
    )

    generated_results = []
    progress_bar = st.progress(0)
    status = st.empty()

    try:
        for index, scene in enumerate(scenes, start=1):
            status.write(
                f"Generating image prompt for scene "
                f"{index} of {len(scenes)}..."
            )

            response = chat(
                model="qwen3:4b",
                messages=[
                    {
                        "role": "system",
                        "content": """
/no_think
You create image prompts for a video generation application.

Return only the image prompt as plain text.
Do not return JSON.
Do not use Markdown or quotation marks around the prompt.

Create one detailed visual prompt for the supplied scene.
Preserve the character's appearance.
Describe the action, environment, lighting, camera angle,
and composition.
Follow the requested visual style.
Use cinematic 16:9 composition.
Aim for 40 to 60 words.
Do not add events that are not in the scene.
Do not include text, captions, logos, or watermarks.
"""
                    },
                    {
                        "role": "user",
                        "content": f"""
Main character:
{character}

Visual style:
{visual_style}

Scene {index}:
{scene}

Write the image prompt for this scene only.
"""
                    }
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": 180
                }
            )

            image_prompt = response.message.content.strip()

            # Remove accidental Markdown fences if returned
            if image_prompt.startswith("```"):
                lines = image_prompt.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                image_prompt = "\n".join(lines).strip()

            generated_results.append({
                "scene_number": index,
                "scene_text": scene,
                "image_prompt": image_prompt,
                "error": (
                    None if image_prompt
                    else "The model returned an empty prompt."
                )
            })

            progress_bar.progress(index / len(scenes))

        st.session_state["generated_scenes"] = generated_results
        st.session_state["last_character"] = character
        st.session_state["last_visual_style"] = visual_style

        success_count = sum(
            bool(item["image_prompt"])
            for item in generated_results
        )

        status.empty()
        progress_bar.empty()

        if success_count == len(scenes):
            st.success(
                f"Generated prompts for all {success_count} scenes!"
            )
        else:
            st.warning(
                f"Generated {success_count} of {len(scenes)} prompts."
            )

    except Exception as error:
        status.empty()
        progress_bar.empty()
        st.error(f"Prompt generation failed: {error}")
        st.info(
            "Check that Ollama is running and the qwen3:4b "
            "model is installed. You can verify this with "
            "`ollama list` in PowerShell."
        )

# --------------------------------------------------
# Display generated scenes and editable prompts
# --------------------------------------------------

if st.session_state.get("generated_scenes"):

    generated_scenes = st.session_state["generated_scenes"]

    st.divider()
    st.header("3. Generated Scenes")

    success_count = sum(
        bool(item["image_prompt"])
        for item in generated_scenes
    )

    st.write(
        f"Total scenes: {len(generated_scenes)} | "
        f"Prompts generated: {success_count}"
    )

    for item in generated_scenes:
        scene_number = item["scene_number"]

        with st.expander(
            f"Scene {scene_number}",
            expanded=True
        ):
            st.markdown("**Original scene**")
            st.write(item["scene_text"])

            if item["error"]:
                st.warning(item["error"])
                continue

            st.markdown("**AI-generated image prompt**")

            st.text_area(
                f"Edit prompt for Scene {scene_number}",
                value=item["image_prompt"],
                height=160,
                key=f"prompt_{scene_number}"
            )

    # --------------------------------------------------
    # Download prompts
    # --------------------------------------------------

    prompt_lines = []

    for item in generated_scenes:
        scene_number = item["scene_number"]

        current_prompt = st.session_state.get(
            f"prompt_{scene_number}",
            item["image_prompt"]
        )

        prompt_lines.append(
            f"SCENE {scene_number}\n"
            f"Original scene:\n{item['scene_text']}\n\n"
            f"Image prompt:\n{current_prompt}\n"
        )

    st.download_button(
        label="Download All Prompts (.txt)",
        data="\n\n".join(prompt_lines),
        file_name="video_image_prompts.txt",
        mime="text/plain"
    )
