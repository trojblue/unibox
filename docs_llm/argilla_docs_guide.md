Here is a summary of the organizational structure, tone, and key examples from the Argilla documentation. This reference is designed to help you replicate their successful use of `mkdocs-material`.

### 1. Organizational Structure
The documentation follows the **Diátaxis framework** principles, separating content into four distinct modes of user needs. It is structured to guide users from "Hello World" to "Power User" and "Contributor."

*   **Getting Started (Onboarding):**
    *   Focuses on immediate gratification (Quickstart) and deployment.
    *   Separates deployment methods (Hugging Face vs. Docker) clearly using tabs.
*   **How-to Guides (Task-Oriented):**
    *   The core of the documentation.
    *   Organized by the object/entity the user interacts with (Users, Workspaces, Datasets, Records).
    *   Provides specific code snippets for distinct actions (Create, Read, Update, Delete).
*   **Reference (Information-Oriented):**
    *   Mirrors the Python SDK structure (`rg.Argilla`, `rg.Dataset`, etc.).
    *   Focuses on class signatures, parameters, and return types rather than long-form narratives.
*   **Tutorials (Learning-Oriented):**
    *   End-to-end workflows (e.g., "Text Classification").
    *   Converted from Jupyter Notebooks, ensuring code and narrative flow together sequentially.
*   **Community (Engagement):**
    *   Explicitly separates "Contributor" (process) from "Developer" (environment setup).

**MkDocs Features Used:**
*   **Navigation:** Hidden table of contents on landing pages to reduce clutter.
*   **Grids & Cards:** Used heavily in `index.md` files to visually route traffic to different sections.
*   **Admonitions:** Used frequently (Tips, Notes, Warnings) to break up text and highlight critical info.
*   **Tabs:** Used to show alternatives (e.g., "From SDK" vs "From UI", or "Docker" vs "Hugging Face").

---

### 2. Tone and Style
*   **Empowering & Direct:** The writing is active. Instead of "The dataset can be created by...", it uses "Create a dataset."
*   **Code-First:** Almost every concept is immediately followed by a Python code block. The code is realistic, not pseudo-code.
*   **Visual:** The docs rely heavily on screenshots (`.png`) and structural diagrams to explain UI concepts that are hard to grasp via text alone.
*   **Welcoming:** The community pages use emojis and encouraging language ("We are excited to have you on board! 🚀") to lower the barrier to entry.
*   **Modular:** Pages are kept relatively short and focused. If a topic gets too large, it links out to a specific sub-guide.

---

### 3. Key Examples (5 Templates)

Below are 5 examples representing different archetypes of documentation pages found in the site.

#### Example 1: The Landing Page (Routing & Value Prop)
**File:** `docs/index.md`
**Purpose:** High-level overview and routing users to the right section using visual cards.

```markdown
---
description: Argilla is a collaboration tool for AI engineers and domain experts to build high-quality datasets.
hide: navigation
---

# Welcome to Argilla

Argilla is a **collaboration tool for AI engineers and domain experts** to build high-quality datasets.

To get started:

<div class="grid cards" markdown>

-  __Get started in 5 minutes!__

    ---

    Deploy Argilla for free on the Hugging Face Hub or with `Docker`. Install the Python SDK with `pip` and create your first project.

    [:octicons-arrow-right-24: Quickstart](getting_started/quickstart.md)

-  __How-to guides__

    ---

    Get familiar with the basic workflows of Argilla. Learn how to manage `Users`, `Workspaces`, `Datasets`, and `Records` to set up your data annotation projects.

    [:octicons-arrow-right-24: Learn more](how_to_guides/index.md)

</div>

!!! INFO "Looking for Argilla 1.x?"
    Looking for documentation for Argilla 1.x? Visit [the latest release](https://docs.v1.argilla.io/en/latest/).

## Why use Argilla?

Argilla can be used for collecting human feedback for a wide variety of AI projects like traditional NLP (text classification, NER, etc.), LLMs (RAG, preference tuning, etc.), or multimodal models (text to image, etc.).

Argilla's programmatic approach lets you build workflows for continuous evaluation and model improvement. The goal of Argilla is to ensure **your data work pays off by quickly iterating on the right data and models**.
```

#### Example 2: The How-To Guide (Task-Based)
**File:** `docs/how_to_guides/workspace.md`
**Purpose:** Explains a specific concept and provides CRUD (Create, Read, Update, Delete) code snippets.

```markdown
---
description: In this section, we will provide a step-by-step guide to show how to manage workspaces.
---

# Workspace management

This guide provides an overview of workspaces, explaining how to set up and manage workspaces in Argilla.

A **workspace** is a *space* inside your Argilla instance where authorized users can collaborate on datasets. It is accessible through the Python SDK and the UI.

!!! info "Main Class"

    ```python
    rg.Workspace(
        name = "name",
        client=client
    )
```
    > Check the [Workspace - Python Reference](../reference/argilla/workspaces.md) to see the attributes, arguments, and methods of the `Workspace` class in detail.

## Create a new workspace

To create a new workspace in Argilla, you can define it in the `Workspace` class and then call the `create` method. This method is inherited from the `Resource` base class and operates without modifications.

> When you create a new workspace, it will be empty. To create and add a new dataset, check these [guides](dataset.md).

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace_to_create = rg.Workspace(name="my_workspace")

created_workspace = workspace_to_create.create()
```

## List workspaces

You can list all the existing workspaces in Argilla by calling the `workspaces` attribute on the `Argilla` class and iterating over them. You can also use `len(client.workspaces)` to get the number of workspaces.

```python
import argilla as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspaces = client.workspaces

for workspace in workspaces:
    print(workspace)
```
```

#### Example 3: The Reference Page (Technical/API)
**File:** `docs/reference/argilla/settings/settings.md`
**Purpose:** Technical documentation for a specific class, focusing on usage examples and parameters.

```markdown
---
hide: footer
---
# `rg.Settings`

`rg.Settings` is used to define the settings of an Argilla `Dataset`. The settings can be used to configure the
behavior of the dataset, such as the fields, questions, guidelines, metadata, and vectors. The `Settings` class is
passed to the `Dataset` class and used to create the dataset on the server. Once created, the settings of a dataset
cannot be changed.

## Usage Examples

### Creating a new dataset with settings

To create a new dataset with settings, instantiate the `Settings` class and pass it to the `Dataset` class.

```python
import argilla as rg

settings = rg.Settings(
    guidelines="Select the sentiment of the prompt.",
    fields=[rg.TextField(name="prompt", use_markdown=True)],
    questions=[rg.LabelQuestion(name="sentiment", labels=["positive", "negative"])],
)

dataset = rg.Dataset(name="sentiment_analysis", settings=settings)

# Create the dataset on the server
dataset.create()

```

### Creating settings using built in templates

Argilla provides built-in templates for creating settings for common dataset types. To use a template, use the class methods of the `Settings` class.

#### Classification Task

You can define a classification task using the `rg.Settings.for_classification` class method. This will create a dataset with a text field and a label question.

```python
settings = rg.Settings.for_classification(labels=["positive", "negative"]) # (1)
```

---

::: src.argilla.settings._resource.Settings
```

#### Example 4: The Community Guide (Process & Tone)
**File:** `docs/community/contributor.md`
**Purpose:** Onboarding new contributors with a very welcoming tone and clear formatting for processes.

```markdown
---
description: This is a step-by-step guide to help you contribute to the Argilla project. We are excited to have you on board! 🚀
hide:
  - footer
---

Thank you for investing your time in contributing to the project! Any contribution you make will be reflected in the most recent version of Argilla 🤩.

??? Question "New to contributing in general?"
    If you're a new contributor, read the [README](https://github.com/argilla-io/argilla/blob/develop/README.md) to get an overview of the project. In addition, here are some resources to help you get started with open-source contributions:

    * **Discord**: You are welcome to join the [Argilla Discord community](http://hf.co/join/discord).
    * **Git**: This is a very useful tool to keep track of the changes in your files.

## First Contact in Discord

Discord is a handy tool for more casual conversations and to answer day-to-day questions. As part of Hugging Face, we have set up some Argilla channels on the server. Click [here](http://hf.co/join/discord) to join the Hugging Face Discord community effortlessly.

* **#argilla-announcements**: 📢 Important announcements and updates.
* **#argilla-distilabel-general**: 💬 General discussions about Argilla and Distilabel.
* **#argilla-distilabel-help**: 🙋‍♀️ Need assistance? We're always here to help. Select the appropriate label (`argilla` or `distilabel`) for your issue and post it.

So now there is only one thing left to do: introduce yourself and talk to the community. You'll always be welcome! 🤗👋
```

#### Example 5: The Tutorial (Narrative Workflow)
**File:** `docs/tutorials/text_classification.ipynb` (Text representation)
**Purpose:** A step-by-step story solving a specific real-world problem.

```markdown
# Text classification

- **Goal**: Show a standard workflow for a text classification task, including zero-shot suggestions and model fine-tuning.
- **Dataset**: [IMDB](https://huggingface.co/datasets/stanfordnlp/imdb), a dataset of movie reviews that need to be classified as positive or negative.
- **Components**: [TextField], [LabelQuestion], [Suggestion]

## Getting started

### Deploy the Argilla server

If you already have deployed Argilla, you can skip this step. Otherwise, you can quickly deploy Argilla following [this guide](../getting_started/quickstart.md).

### Set up the environment

To complete this tutorial, you need to install the Argilla SDK and a few third-party libraries via `pip`.

```bash
!pip install argilla
!pip install setfit==1.0.3 transformers==4.40.2
```

Let's make the required imports:

```python
import argilla as rg
from datasets import load_dataset, Dataset
from setfit import SetFitModel, Trainer, get_templated_dataset, sample_dataset
```

## Configure and create the Argilla dataset

Now, we will need to configure the dataset. In the settings, we can specify the guidelines, fields, and questions.

!!! note
    Check this [how-to guide](../how_to_guides/dataset.md) to know more about configuring and creating a dataset.

```python
labels = ["positive", "negative"]

settings = rg.Settings(
    guidelines="Classify the reviews as positive or negative.",
    fields=[
        rg.TextField(
            name="review",
            title="Text from the review",
            use_markdown=False,
        ),
    ],
    questions=[
        rg.LabelQuestion(
            name="sentiment_label",
            title="In which category does this article fit?",
            labels=labels,
        )
    ],
)
```
```