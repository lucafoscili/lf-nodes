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
  - [Workflow Runner](#workflow-runner)
    - [Adding New Workflows](#adding-new-workflows)
  - [Image editor](#image-editor)
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

## Workflow Runner

The Workflow Runner miniapp is included in this package but is disabled by default.
To enable it you must set the environment variable `WORKFLOW_RUNNER_ENABLED=true` before starting ComfyUI.

By default the runner will not register its HTTP routes or static frontend when `WORKFLOW_RUNNER_ENABLED` is not set or set to a false value. This makes the runner opt-in and prevents accidental exposure of the runner endpoints.

Configuration is loaded from the repository-level `.env` file (at the project root).
Set `WORKFLOW_RUNNER_ENABLED=true` to enable the runner.

If you do enable it, ensure authentication/allowed-users are configured (see `docs/WORKFLOW_RUNNER.md`) to avoid unauthorised access.

![Workflow Runner UI](https://github.com/lucafoscili/lucafoscili/blob/c105d85a06460433607f22e5027cfd97a75a33b4/lf-nodes/screenshots/WorkflowRunnerUI.png "Workflow Runner UI")

### Adding New Workflows

To add a new workflow to the Workflow Runner, follow these steps:

1. **Create the workflow JSON file**  
   Export your ComfyUI workflow and save it as `modules/workflow_runner/workflows/<workflow_name>.json`

2. **Create the workflow Python module**  
   Create a corresponding Python file `modules/workflow_runner/workflows/<workflow_name>.py` with:
   - **Workflow configuration function**: `_configure(prompt, inputs)` that maps user inputs to workflow node inputs
   - **Input cells**: Define `WorkflowCell` objects for each user input (uploads, text fields, checkboxes, etc.)
   - **Output cells**: Define `WorkflowCell` objects for each output (images, strings, JSON, etc.)
   - **Workflow definition**: Create a `WorkflowNode` object with metadata and export it as `WORKFLOW`

3. **Register the workflow**  
   Add your workflow module name to the `_WORKFLOW_MODULES` tuple in `modules/workflow_runner/workflows/__init__.py`

4. **Update frontend types** (if adding new output types)  
   If your workflow produces new output types:
   - Add the output interface to `web/workflow-runner/src/types/api.ts`
   - Update `WorkflowNodeOutputs` interface to include your new type
   - Update output rendering in `web/workflow-runner/src/elements/components.ts` and `main.outputs.ts`

5. **Update node outputs** (if needed)  
   If using custom nodes, ensure they return data in the expected format:
   - Set `OUTPUT_IS_LIST` appropriately for batch/list outputs
   - Return structured data via `ui.lf_output` for frontend consumption

**Example commit:** See commit `2fbb49e` which adds the `caption_image_vision` workflow, demonstrating all these steps including updating `LF_DisplayString` to support string outputs and frontend components to render them.

## Image editor

The image editor node (`LF_LoadAndEditImages`) allows users to load images from disk and perform editing operations such as inpainting, adjusting saturations, brightness, contrast, and more, all through an interactive interface.
It's possible to select the images from the file system tree and then send them downstream to other nodes for further processing.

![Load and Edit Images](https://github.com/lucafoscili/lucafoscili/blob/e59725f22c9d0c965a291fd735729d0b57166199/lf-nodes/screenshots/LoadAndEditImages.png "Load and Edit Images")

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
