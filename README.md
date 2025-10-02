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

Whether you're after quality-of-life improvements or specific functionalities, LF Nodes has you covered. The nodes are designed to be user-friendly and intuitive, making them accessible to users of all skill levels.

Most UI elements used by the frontend belong to the [LF Widgets webcomponents library](https://github.com/lucafoscili/lf-widgets), a modern collection of modular and customizable webcomponents built on Stencil.js specifically to integrate with LF Nodes.
  
![Histograms and compares](https://github.com/lucafoscili/lucafoscili/blob/97bfd28ca4ea3c0ecf6a6990fbbd467ab394c2cc/lf-nodes/screenshots/Screenshot%202025-02-18%20094817.png "Histograms and compares")

## What kind of nodes does it offer?

That's a tough one—the nodes span quite a few categories. Here's a quick breakdown:

- **Analytics nodes**: Visualize and track data, like checkpoint/LoRA usage or image histograms.
- **Configuration nodes**: Manage CivitAI metadata, and control the suite via the Control Panel.
- **Image manipulation nodes**: Tools to manipulate images, such as filter and resize nodes.
- **IO Operations nodes**: Load and save files to/from the file system.
- **JSON nodes**: Tools to manipulate and display JSON data.
- **LLM nodes**: Interface with locally running LLMs, like the Messenger node, which also manages characters.
- **Logic nodes**: Control flow using simple switches.
- **Primitive nodes**: Work with primitive data types, offering features like history.
- **Seed generation nodes**: Generate seeds for complex workflows.
- **Selector nodes**: Resource selection widgets with metadata display for models.

## Table of Contents

- [LF Nodes](#lf-nodes)
  - [Overview](#overview)
  - [What kind of nodes does it offer?](#what-kind-of-nodes-does-it-offer)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Using ComfyUI Manager](#using-comfyui-manager)
    - [Manual](#manual)
  - [Workflow samples](#workflow-samples)
    - [Image 2 Image (ControlNet + Editing breakpoint + WD14Tagger)](#image-2-image-controlnet--editing-breakpoint--wd14tagger)
    - [Caption dataset (WD14)](#caption-dataset-wd14)
    - [Resize image for training](#resize-image-for-training)
    - [Compare images](#compare-images)
    - [e2e](#e2e)
    - [Flux + LLM Character manager](#flux--llm-character-manager)
    - [I2I (Refine)](#i2i-refine)
    - [LLM Chat](#llm-chat)
    - [LoRA tester](#lora-tester)
    - [Markdown documentation](#markdown-documentation)
    - [Multiple prompt from JSON](#multiple-prompt-from-json)
    - [Resize for web + blurred placeholder](#resize-for-web--blurred-placeholder)
  - [Notes](#notes)
  - [Contributing](#contributing)
  - [License](#license)
  - [Documentation](#documentation)

## Installation

### Using ComfyUI Manager

- Open ComfyUI Manager.
- Search LF Nodes.
- Install the node suite and restart ComfyUI.

### Manual

- Go to the `ComfyUI/custom_nodes` folder.
- Open a terminal.
- Copy and paste this command `git clone https://github.com/lucafoscili/lf-nodes.git`.

## Workflow samples

### [Image 2 Image (ControlNet + Editing breakpoint + WD14Tagger)](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Image%202%20Image%20(with%20ControlNet%2C%20editing%20breakpoint%20and%20WD14%20tagger).json)

![Image 2 Image (ControlNet + Editing breakpoint + WD14Tagger)](https://github.com/lucafoscili/lucafoscili/blob/c581de007c088e84a7cb78c64431b7263622ff0f/lf-nodes/screenshots/Image%202%20Image%20(with%20ControlNet%2C%20editing%20breakpoint%20and%20WD14%20tagger).png)

### [Caption dataset (WD14)](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Caption%20dataset%20(WD14).json)

![Caption dataset (WD14)](https://github.com/lucafoscili/lucafoscili/blob/dd5c3f0fd525ff4cf5b99a940562faa4b7d0135e/lf-nodes/screenshots/Caption%20dataset%20(WD14).png)

### [Resize image for training](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Resize%20image%20for%20training.json)

![Resize image for training](https://github.com/lucafoscili/lucafoscili/blob/743c982169cb6a8981b14a13dd65b1016fc84028/lf-nodes/screenshots/Resize%20image%20for%20training.png)

### [Compare images](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Compare%20images.json)

![Compare images](https://github.com/lucafoscili/lucafoscili/blob/3c8e1c3b4d802115a0cd03c29eb71db0ba698a89/lf-nodes/screenshots/Compare%20images.png)

### [e2e](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/workflows/E2E.json)

![e2e](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/E2E.png)

### [Flux + LLM Character manager](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Flux%20%2B%20LLM%20Character%20manager.json)

![Flux + LLM Character manager](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/Flux%20%2B%20LLM%20Character%20manager.png)

### [I2I (Refine)](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/workflows/Image%202%20Image%20(Refine).json)

![I2I (Refine)](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/Image%202%20Image%20(Refine).png)

### [LLM Chat](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/LLM%20Chat.json)

![LLM Chat](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/LLM%20Chat.png)

### [LoRA tester](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/LoRa%20tester.json)

![LoRA tester](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/Lora%20tester.png)

### [Markdown documentation](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Markdown%20documentation.json)

![Markdown documentation](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/Markdown%20documentation.png)

### [Multiple prompt from JSON](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Multiple%20prompt%20from%20JSON.json)

![Multiple prompt from JSON](https://github.com/lucafoscili/lucafoscili/blob/b919d07e84881210b41e8ceba6126f0b01e50f38/lf-nodes/screenshots/Multiple%20prompt%20from%20JSON.png)

### [Resize for web + blurred placeholder](https://github.com/lucafoscili/lf-nodes/blob/929fdb5a982c2c2192932f27782bf2a41a92e428/example_workflows/Multiple%20image%20resize%20for%20web%20%2B%20blurred%20placeholder.json)

![Resize for web + blurred placeholder](https://github.com/lucafoscili/lucafoscili/blob/a42765fc6ef9a394deeb695e4c31eaf3c5ec6139/lf-nodes/screenshots/Multiple%20image%20resize%20for%20web%20%2B%20blurred%20placeholder.png)

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
- [Image Editor](docs/IMAGE_EDITOR.md)
- [Node Template](docs/NODE_TEMPLATE.md)
