
#joyCaption
import os
import sys
#print(sys.executable)
import torch
from pathlib import Path
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration
print("Let's load the captioning models")
# Load JoyCaption model and tokenizer
MODEL_NAME = "fancyfeast/llama-joycaption-alpha-two-hf-llava"
processor = AutoProcessor.from_pretrained(MODEL_NAME, use_fast=False)
llava_model = LlavaForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16, device_map="cuda")
llava_model.eval()
user_prompt = os.environ["JOY_CAPTION_PROMPT"]
system_prompt = "You are describing motion. Pay attention to the subjects characteristics, how they change from frame to frame? What can you convey about this motion? try your best to create a description that both contains the motion (positions of subjects) and also intricate details about the subjects. Remember, describe only as videos. Avoid the words grid, image, still, sequence, frames, series, photograph. "

def generate_caption(image_path):
    # Load image
    image = Image.open(image_path).convert("RGB")

    # Build the conversation
    convo = [
        {"role": "system", "content": "You are a helpful video captioner."},
        {"role": "user", "content": system_prompt + user_prompt },
    ]
    # Format the conversation
    convo_string = processor.apply_chat_template(convo, tokenize=False, add_generation_prompt=True)
    assert isinstance(convo_string, str)

    # Process the inputs
    inputs = processor(text=[convo_string], images=[image], return_tensors="pt").to("cuda")
    inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

    # Generate the captions
    with torch.no_grad():
        generate_ids = llava_model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            suppress_tokens=None,
            use_cache=True,
            temperature=0.6,
            top_k=None,
            top_p=0.9,
        )[0]

    # Trim off the prompt
    generate_ids = generate_ids[inputs['input_ids'].shape[1]:]

    # Decode the caption
    caption = processor.tokenizer.decode(generate_ids, skip_special_tokens=True,
                                         clean_up_tokenization_spaces=False).strip()
    return caption


def process_grids(grids_folder):
    for image_file in os.listdir(grids_folder):
        if image_file.endswith('.jpg'):
            image_path = os.path.join(grids_folder, image_file)
            caption = generate_caption(image_path)
            caption_path = Path(image_path).with_suffix('.txt')
            with open(caption_path, 'w') as f:
                f.write(caption)
            print(f"Caption saved for {image_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python joyCaption.py <path_to_grids>")
        sys.exit(1)

    grids_folder = sys.argv[1]
    process_grids(grids_folder)
    print("Thanks for using HDS and happy training!")
