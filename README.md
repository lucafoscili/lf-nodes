<!-- markdownlint-disable MD033 -->
# LF Nodes

<div align="center">

![LF Nodes](https://img.shields.io/badge/dynamic/json?logo=python&logoColor=black&labelColor=white&color=black&label=Nodes&query=nodes&url=https://raw.githubusercontent.com/lucafoscili/lf-nodes/master/count.json)

</div>

<div align="center">

![LFNodes](https://github.com/lucafoscili/lucafoscili/blob/996cb0c00612e3278798c32eea80f1332277132e/lf-nodes/logo/LFN.png "LF Nodes logo")

</div>

<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/lucafoscili/lf-nodes?logo=github&logoColor=black&labelColor=white&color=black)

</div>

## Overview

A suite of custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) aimed at enhancing user experience with more interactive and visually engaging widgets.

Most UI elements used by the frontend belong to the [LF Widgets webcomponents library](https://github.com/lucafoscili/lf-widgets), a modern collection of modular and customizable webcomponents built on Stencil.js specifically to integrate with LF Nodes.

![Simple inpaint](https://github.com/lucafoscili/lucafoscili/blob/e988f5c1df6299e96f2bf6b164c3b99e6df841f7/lf-nodes/screenshots/Screenshot%202025-10-03%20224716.jpg "Simple inpaint")

The nodes span quite a few categories:

- **Analytics nodes**: Visualize and track data, like checkpoint/LoRA usage or image histograms.
- **Configuration nodes**: Manage CivitAI metadata, and control the suite via the Control Panel.
- **Filter nodes**: Apply various filters to images, including blur, sharpen, and edge detection.
- **Image manipulation nodes**: Tools to manipulate images, such as filter and resize nodes.
- **IO Operations nodes**: Load and save files to/from the file system.
- **JSON nodes**: Tools to manipulate and display JSON data.
- **Latent manipulation nodes**: Latent decoding and encoding tools.
- **LLM nodes**: Interface with locally running LLMs, like the Messenger node, which also manages characters.
- **Logic nodes**: Control flow using simple switches.
- **Primitive nodes**: Work with primitive data types, offering features like history.
- **Region nodes**: Image region selection and editing tools.
- **Seed generation nodes**: Generate seeds for complex workflows.
- **Selector nodes**: Resource selection widgets with metadata display for models.

To see some example workflow you can check the [example_workflows folder](example_workflows).

## Table of Contents

- [LF Nodes](#lf-nodes)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [ComfyUI Manager](#comfyui-manager)
    - [Manual](#manual)
      - [Method 1: Download ZIP](#method-1-download-zip)
      - [Method 2: Git Clone](#method-2-git-clone)
  - [Notes](#notes)
  - [Contributing](#contributing)
  - [License](#license)
  - [Documentation](#documentation)

## Installation

### ComfyUI Manager

- Open ComfyUI Manager.
- Search LF Nodes.
- Install the node suite and restart ComfyUI.

### Manual

#### Method 1: Download ZIP

- Go to the [releases page](https://github.com/lucafoscili/lf-nodes/releases).
- Download the latest release ZIP file.
- Extract the contents of the ZIP file into the `ComfyUI/custom_nodes` folder.
- Restart ComfyUI.

#### Method 2: Git Clone

- Go to the `ComfyUI/custom_nodes` folder.
- Open a terminal.
- Copy and paste this command `git clone https://github.com/lucafoscili/lf-nodes.git`.

## Notes

The LLM nodes were tested with [Koboldcpp](https://github.com/LostRuins/koboldcpp/tree/v1.73), but any Open AI-compatible endpoint that does not require authentication/an API key should work.
The model used in the workflows samples is [UCLA-AGI/Llama-3-Instruct-8B-SPPO-Iter3](https://huggingface.co/UCLA-AGI/Llama-3-Instruct-8B-SPPO-Iter3) with [ChaoticNeutrals/LLaVA-Llama-3-8B-mmproj-Updated](https://huggingface.co/ChaoticNeutrals/LLaVA-Llama-3-8B-mmproj-Updated).

## Contributing

Contributions to this repository are welcome, feel free to submit pull requests or open issues for discussion!
To setup the environment clone this repository, then from the root open a terminal and run the command

`pip install -r requirements.txt`

This will install all the required dependencies for the Python backend.

To build the frontend, you will need to have Node.js and Yarn installed, then run the command

`yarn setup`

This command will install all the dependencies.
_Note that the repository includes the compiled frontend sources, so you can skip this step if you don't plan to modify the frontend._

`yarn build`

This command will compile all the frontend sources and generate/refresh the actual web directory.

## License

MIT License

## Documentation

For an overview of how this nodes suite is structured and how it integrates with the UI, see:

- [Architecture](docs/ARCHITECTURE.md)
- [Frontend Proxy](docs/FRONTEND_PROXY.md)
- [Image Editor](docs/IMAGE_EDITOR.md)
- [Node Template](docs/NODE_TEMPLATE.md)
- [Proxy](docs/PROXY.md)
- [Workflow Runner](docs/WORKFLOW_RUNNER.md)

![Simple pipeline](https://github.com/lucafoscili/lucafoscili/blob/e988f5c1df6299e96f2bf6b164c3b99e6df841f7/lf-nodes/screenshots/Screenshot%202025-02-18%20094817.png "Simple pipeline")
