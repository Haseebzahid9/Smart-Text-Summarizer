"""
summarizer.py
-------------
Core AI summarization module for Smart Text Summarizer.

Handles:
    - Loading the Hugging Face tokenizer and model (facebook/bart-large-cnn)
    - Chunking long texts that exceed model token limits
    - Generating summaries at three length presets (short / medium / long)

The model is loaded once and cached by Streamlit to avoid reloading on
every button click.
"""

from __future__ import annotations

import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_NAME: str = "facebook/bart-large-cnn"

# BART's hard limit is 1 024 tokens; we stay a bit under to be safe.
MAX_INPUT_TOKENS: int = 900

# Summary length presets: (min_tokens, max_tokens)
LENGTH_PRESETS: dict[str, tuple[int, int]] = {
    "Short":  (40,  80),
    "Medium": (80,  180),
    "Long":   (150, 350),
}


# ---------------------------------------------------------------------------
# Model loading  (cached so it runs only once per Streamlit session)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def load_model() -> tuple[AutoTokenizer, AutoModelForSeq2SeqLM]:
    """
    Load the BART tokenizer and model from Hugging Face Hub.

    The first call downloads the model weights (~1.6 GB) and caches them
    locally.  Subsequent calls within the same Streamlit session return the
    cached objects instantly.

    Returns:
        tuple: (tokenizer, model) ready for inference.

    Example:
        >>> tokenizer, model = load_model()
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    # Move model to GPU if available, otherwise stay on CPU.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()          # inference mode — disables dropout etc.

    return tokenizer, model


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _chunk_text(text: str, tokenizer: AutoTokenizer) -> list[str]:
    """
    Split *text* into token-safe chunks so each chunk fits within
    MAX_INPUT_TOKENS.  Splitting is done at sentence boundaries (". ")
    to avoid cutting mid-sentence.

    Parameters:
        text (str): Raw input text.
        tokenizer (AutoTokenizer): The loaded BART tokenizer.

    Returns:
        list[str]: A list of text chunks, each within the token limit.

    Example:
        >>> chunks = _chunk_text(long_article, tokenizer)
    """
    sentences = text.replace("\n", " ").split(". ")
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_token_count: int = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        token_count = len(tokenizer.encode(sentence, add_special_tokens=False))

        if current_token_count + token_count > MAX_INPUT_TOKENS:
            # Flush the current chunk and start a new one.
            if current_chunk:
                chunks.append(". ".join(current_chunk) + ".")
            current_chunk = [sentence]
            current_token_count = token_count
        else:
            current_chunk.append(sentence)
            current_token_count += token_count

    # Flush any remaining sentences.
    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks if chunks else [text]


def _summarize_chunk(
    chunk: str,
    tokenizer: AutoTokenizer,
    model: AutoModelForSeq2SeqLM,
    min_length: int,
    max_length: int,
) -> str:
    """
    Generate a summary for a single text chunk.

    Parameters:
        chunk (str): A single text chunk within the token limit.
        tokenizer (AutoTokenizer): The loaded BART tokenizer.
        model (AutoModelForSeq2SeqLM): The loaded BART model.
        min_length (int): Minimum number of summary tokens.
        max_length (int): Maximum number of summary tokens.

    Returns:
        str: The generated summary text.

    Example:
        >>> summary = _summarize_chunk(chunk, tokenizer, model, 40, 80)
    """
    device = next(model.parameters()).device

    inputs = tokenizer(
        chunk,
        return_tensors="pt",
        max_length=MAX_INPUT_TOKENS,
        truncation=True,
        padding=True,
    ).to(device)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            num_beams=4,          # beam search for higher quality
            min_length=min_length,
            max_length=max_length,
            length_penalty=2.0,   # encourages longer, complete sentences
            early_stopping=True,
            no_repeat_ngram_size=3,  # avoids repetitive phrases
        )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarize_text(text: str, length_preset: str = "Medium") -> str:
    """
    Generate an AI summary of *text* using facebook/bart-large-cnn.

    Long documents are automatically chunked and each chunk is summarised
    independently; the partial summaries are then concatenated.

    Parameters:
        text (str): The input text to summarise.
        length_preset (str): One of "Short", "Medium", or "Long".
                             Defaults to "Medium".

    Returns:
        str: The generated summary.

    Raises:
        ValueError: If *length_preset* is not a valid key.
        RuntimeError: If the model fails to generate a summary.

    Example:
        >>> summary = summarize_text(article, length_preset="Short")
    """
    if length_preset not in LENGTH_PRESETS:
        raise ValueError(
            f"Invalid length_preset '{length_preset}'. "
            f"Choose from: {list(LENGTH_PRESETS.keys())}"
        )

    tokenizer, model = load_model()
    min_len, max_len = LENGTH_PRESETS[length_preset]

    chunks = _chunk_text(text, tokenizer)

    partial_summaries: list[str] = []
    for chunk in chunks:
        partial = _summarize_chunk(chunk, tokenizer, model, min_len, max_len)
        if partial:
            partial_summaries.append(partial)

    if not partial_summaries:
        raise RuntimeError("The model returned an empty summary. Please try again.")

    return " ".join(partial_summaries)
