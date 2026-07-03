# 📚 Smart Text Summarizer

> Generate concise AI-powered summaries from long documents — instantly.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Hugging Face](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)](https://huggingface.co/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Haseebzahid9-181717?logo=github)](https://github.com/Haseebzahid9/Smart-Text-Summarizer)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone the Repository](#2-clone-the-repository)
  - [3. Create a Virtual Environment](#3-create-a-virtual-environment)
  - [4. Install Dependencies](#4-install-dependencies)
  - [5. Run the App](#5-run-the-app)
- [How to Use](#how-to-use)
- [Example](#example)
- [Architecture](#architecture)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## About

**Smart Text Summarizer** is an AI-powered web application that condenses long articles, essays, research papers, blog posts, and reports into short, readable summaries in seconds.

It uses **`facebook/bart-large-cnn`** — a pre-trained sequence-to-sequence model from Hugging Face, fine-tuned for summarization. No custom training is required. The model downloads automatically on first run.

**Great for:**
- Students and researchers reviewing long papers quickly
- Journalists and writers digesting news articles
- Professionals summarizing lengthy business reports
- Developers learning Hugging Face + Streamlit integration

---

## Features

| Feature | Details |
|---|---|
| AI Summarization | `facebook/bart-large-cnn` via Hugging Face Transformers |
| Three Length Modes | Short · Medium · Long |
| Live Input Stats | Word count, character count, estimated reading time |
| Summary Stats | Original words, summary words, compression % |
| Download | Export summary as `.txt` file |
| Copy to Clipboard | One-click copy button |
| Clear Input | Reset text area instantly |
| Long Document Support | Auto-chunks text beyond BART's token limit |
| Session Caching | Model loads once — no repeated downloads per session |
| Error Handling | User-friendly messages for all edge cases |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web Framework | Streamlit 1.35+ |
| AI / NLP | Hugging Face Transformers 4.40+ |
| Deep Learning | PyTorch 2.2+ |
| Model | facebook/bart-large-cnn |
| Tokenizer | AutoTokenizer (Hugging Face) |
| Utilities | sentencepiece · pathlib · datetime |

---

## Project Structure

```
Smart-Text-Summarizer/
│
├── app.py                  ← Streamlit UI and user interaction logic
├── summarizer.py           ← Model loading, chunking, and summarization
├── utils.py                ← Word count, validation, stats, download helpers
│
├── requirements.txt        ← All Python dependencies
├── README.md               ← This file
├── LICENSE                 ← MIT License
├── .gitignore              ← Excluded files and folders
│
├── assets/
│   ├── logo.png            ← Project logo
│   └── screenshot.png      ← App screenshot
│
├── examples/
│   ├── sample_article.txt  ← Sample input article (681 words)
│   └── sample_summary.txt  ← Expected output for the sample
│
└── .streamlit/
    └── config.toml         ← Streamlit theme and server config
```

---

## Quick Start

Follow these steps in order to get the app running on your machine.

### 1. Prerequisites

Make sure these are installed before you begin:

- [Python 3.12+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- An internet connection *(to download the BART model ~1.6 GB on first run)*

---

### 2. Clone the Repository

```bash
git clone https://github.com/Haseebzahid9/Smart-Text-Summarizer.git
cd Smart-Text-Summarizer
```

---

### 3. Create a Virtual Environment

A virtual environment keeps dependencies isolated from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You will see `(venv)` at the start of your terminal prompt when it is active.

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `transformers` | Hugging Face model library |
| `torch` | PyTorch deep learning backend |
| `sentencepiece` | Tokenizer dependency for BART |

> **GPU users:** The default `pip install torch` installs the CPU version.
> For CUDA support, visit: [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/)

---

### 5. Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

> **First run:** The app downloads `facebook/bart-large-cnn` (~1.6 GB) from Hugging Face Hub.
> This happens **once only** — every run after that uses the local cache.

---

## How to Use

Once the app is open in your browser:

1. **Paste your text** into the left-side text area — any article, essay, or report.
2. **Check live stats** — word count, character count, and reading time update as you type.
3. **Choose a summary length** — Short, Medium, or Long.
4. **Click "✨ Generate Summary"** — the AI processes your text and shows the summary on the right.
5. **Read the statistics cards** — see original words, summary words, and compression percentage.
6. **Download or copy** — save the summary as a `.txt` file or copy it to your clipboard.
7. **Clear** — click the 🗑️ Clear button to reset and start over.

---

## Example

**Input** — `examples/sample_article.txt` (681 words, AI & Healthcare):

```
Artificial intelligence is rapidly transforming the healthcare industry,
offering new tools and capabilities that were once thought impossible.
From diagnosing diseases with remarkable accuracy to predicting patient
outcomes and personalizing treatment plans...
```

**Output** — Medium summary (~97 words · 85.7% compression):

```
Artificial intelligence is transforming healthcare in several key areas.
AI-powered imaging tools can detect cancers with accuracy rivaling expert
radiologists. Predictive models flag high-risk patients before symptoms appear.
In drug discovery, AI reduces costly late-stage failures. Personalized medicine
uses genomic and real-time data to tailor treatments. Despite these advances,
challenges around data privacy, algorithmic bias, and clinician training must
be addressed for safe and equitable deployment.
```

---

## Architecture

```
User Input (Streamlit UI)
        │
        ▼
  validate_input()          ← utils.py: checks empty / too-short input
        │
        ▼
  summarize_text()          ← summarizer.py: main entry point
        │
        ├── _chunk_text()   ← splits text at sentence boundaries if > 900 tokens
        │
        └── _summarize_chunk()  ← runs BART inference (beam search) per chunk
                │
                ▼
        format_stats()      ← utils.py: word count, compression %
                │
                ▼
    Streamlit UI — Display Summary + Stats
```

**How BART processes your text:**
1. Text is tokenized using `AutoTokenizer`.
2. If it exceeds 900 tokens, it is split at sentence boundaries into safe chunks.
3. Each chunk is passed through `facebook/bart-large-cnn` with beam search decoding.
4. Partial summaries are joined into one final output.
5. Statistics are computed and shown in styled cards.

---

## Future Improvements

| Planned Feature | Description |
|---|---|
| PDF Summarization | Upload and summarize `.pdf` files |
| DOCX Summarization | Upload and summarize `.docx` Word documents |
| URL Summarization | Paste a URL — app fetches and summarizes the page |
| YouTube Summarization | Summarize videos via transcript extraction |
| Gemini API | Google Gemini as an alternative AI backend |
| OpenAI API | GPT-4o as an alternative AI backend |
| Multi-language | Summarize and translate in multiple languages |
| Keyword Extraction | Extract key topics and named entities |
| Text-to-Speech | Read the summary aloud |
| Summary History | Store past summaries in a local database |
| User Authentication | Login system for personal history |

---

## Contributing

Contributions are welcome!

```bash
# 1. Fork the repo on GitHub
# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Commit your changes
git commit -m "Add: your feature description"

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Open a Pull Request on GitHub
```

**Please ensure your code:**
- Follows PEP 8 style guidelines
- Includes docstrings for all new functions
- Does not break existing functionality

---

## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full details.

---

## Author

**Haseeb Zahid**

- GitHub: [@Haseebzahid9](https://github.com/Haseebzahid9)
- Repository: [Smart-Text-Summarizer](https://github.com/Haseebzahid9/Smart-Text-Summarizer)

---

`python` `streamlit` `huggingface` `transformers` `nlp` `text-summarization`
`bart` `pytorch` `ai` `machine-learning` `deep-learning` `natural-language-processing`
`summarizer` `portfolio-project` `beginner-friendly`

---

*Built with ❤️ using Python, Streamlit & Hugging Face Transformers*
