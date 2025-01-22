HunYuan Dataset Creator

This tool splits videos into snippets, generates image grids, and then uses a model to caption each grid. An NVIDIA GPU with CUDA is strongly recommended, or else captioning might be extremely slow (and the GUI may appear to freeze).

Quick Start
Clone this repository:

git clone https://github.com/lealcc/HunYuan-DatasetCreator/tree/master
Then open the cloned folder:


On Windows, double-click start.bat:

The script will create a virtual environment (if missing), install requirements, and launch the GUI.
Using the GUI:

Click Browse to select the folder containing your videos.
(Optional) Enter a Caption Prompt.
Specify the Snippet Duration in seconds.
Click Start Processing.
It will split videos, create image grids, and run captioning on each grid.

Note: The process can appear “frozen” while the model is generating captions. This is normal, especially on a slower system or when using CPU instead of GPU.

Requirements
Python 3.9+ (if you plan to run outside of the provided scripts).
NVIDIA GPU with CUDA for faster captioning.
Internet (if you haven’t pre-downloaded large models and are fetching from Hugging Face).
All other needed Python packages are installed automatically via pip install -r requirements.txt when start.bat runs.
