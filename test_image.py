import openvino_genai
from PIL import Image

model_path = "stable-diffusion-v1-5-int8-ov"

print("Loading the image model...")

pipe = openvino_genai.Text2ImagePipeline(
    model_path,
    "GPU",
)

prompt = input("Enter a scene description: ")

print("Generating your first image...")

image_tensor = pipe.generate(
    prompt,
    width=512,
    height=512,
    num_inference_steps=20,
    num_images_per_prompt=1,
)

image = Image.fromarray(image_tensor.data[0])
file_name = input("Enter image file name (without extension): ")
image.save(f"{file_name}.png")

print("Success! Image saved as test_scene.png")
