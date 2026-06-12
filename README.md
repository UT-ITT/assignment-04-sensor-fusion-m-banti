[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AktWbCri)

# assignment-04-CV-Sensor-Fusion
To test all three applicsations create a python virtual environment by using the requirements.txt file. (Since it's assignment 4 and we all know how it works I'm not writing an instruction)

## Perspective Transformer

This script allows us to select an image that needs to be cropped. The cropping area results from choosing 4 corner points inside the image. The cropped picture can be saved, discarded or the process can be canceled.

### How it works

1. Either use the provided image or choose your own (I highly recomment using the provided one)
2. Input to terminal:

```
    python3 image_extractor.py <input_path> <output_path> <width> <height>"
```

Example:

```
    python3 image_extractor.py images/image.jpg images/extracted_image.png 200 200
```

3. To cut the image just set the corner points of the selecting by right clicking with your mouse on the respective area.
4. To save the image press the key "s". To discard the selection press the key "d". To exit after saving the image or to cancel the process press the key "esc"

#### Assets

(Source of: image.jpg)[https://en.meming.world/wiki/File:Crying_Cat.jpg/]

This repository was implemented via Apple Silicon M4 Chip. In addition I used Pillow instead of Pill because of that:

> Use Pillow instead, as PIL is basically dead. Pillow is a maintained fork of PIL.

Source: https://stackoverflow.com/questions/20060096/how-to-install-pil-with-pip-on-mac-os
