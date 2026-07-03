"""
utils.py
--------
Utility / helper functions for Smart Text Summarizer.

All pure-Python helpers live here so that app.py and summarizer.py stay
focused on their own responsibilities.

Functions:
    count_words          -- Count the number of words in a string.
    count_characters     -- Count the number of characters in a string.
    estimate_reading_time -- Estimate how long it takes to read a text.
    compression_percentage -- Calculate how much the text was compressed.
    validate_input       -- Validate user input before summarisation.
    get_download_content -- Prepare plain-text content for file download.
    format_stats         -- Return a dict of formatted statistics.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Text statistics
# ---------------------------------------------------------------------------

def count_words(text: str) -> int:
    """
    Count the number of words in *text*.

    Words are defined as sequences of non-whitespace characters.

    Parameters:
        text (str): Input text.

    Returns:
        int: Number of words.

    Example:
        >>> count_words("Hello world")
        2
    """
    return len(text.split()) if text.strip() else 0


def count_characters(text: str) -> int:
    """
    Count the total number of characters in *text*, including spaces.

    Parameters:
        text (str): Input text.

    Returns:
        int: Character count.

    Example:
        >>> count_characters("Hello")
        5
    """
    return len(text)


def estimate_reading_time(text: str, wpm: int = 200) -> str:
    """
    Estimate how long a human would take to read *text*.

    Based on an average adult reading speed of 200 words per minute.

    Parameters:
        text (str): Input text.
        wpm  (int): Words-per-minute reading speed. Defaults to 200.

    Returns:
        str: Human-readable reading time, e.g. "3 min 20 sec".

    Example:
        >>> estimate_reading_time("word " * 400)
        '2 min 0 sec'
    """
    words = count_words(text)
    if words == 0:
        return "0 sec"

    total_seconds = int((words / wpm) * 60)
    minutes, seconds = divmod(total_seconds, 60)

    if minutes == 0:
        return f"{seconds} sec"
    return f"{minutes} min {seconds} sec"


def compression_percentage(original: str, summary: str) -> float:
    """
    Calculate how much shorter the summary is compared to the original.

    Parameters:
        original (str): Original text.
        summary  (str): Generated summary.

    Returns:
        float: Compression percentage rounded to one decimal place.
               Returns 0.0 if the original text is empty.

    Example:
        >>> compression_percentage("word " * 100, "word " * 20)
        80.0
    """
    original_words = count_words(original)
    summary_words = count_words(summary)

    if original_words == 0:
        return 0.0

    reduction = original_words - summary_words
    return round((reduction / original_words) * 100, 1)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_input(text: str, min_words: int = 30) -> tuple[bool, str]:
    """
    Validate the user's input text before sending it to the model.

    Checks performed (in order):
        1. Text must not be empty or whitespace-only.
        2. Text must contain at least *min_words* words.

    Parameters:
        text      (str): The raw input text from the user.
        min_words (int): Minimum word count required. Defaults to 30.

    Returns:
        tuple[bool, str]:
            - (True, "")              -- input is valid.
            - (False, error_message)  -- input is invalid; message explains why.

    Example:
        >>> ok, msg = validate_input("Hello world")
        >>> print(ok, msg)
        False  Text is too short. Please enter at least 30 words.
    """
    if not text or not text.strip():
        return False, "Please paste or type some text before generating a summary."

    word_count = count_words(text)
    if word_count < min_words:
        return False, (
            f"Your text is too short ({word_count} words). "
            f"Please enter at least {min_words} words for a meaningful summary."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Download helper
# ---------------------------------------------------------------------------

def get_download_content(original_text: str, summary: str, length_preset: str) -> str:
    """
    Build a plain-text string that bundles the summary with metadata for
    the downloadable .txt file.

    Parameters:
        original_text (str): The original input text.
        summary       (str): The AI-generated summary.
        length_preset (str): The selected summary length (Short/Medium/Long).

    Returns:
        str: Formatted text file content ready for st.download_button.

    Example:
        >>> content = get_download_content(article, summary, "Medium")
        >>> print(content[:40])
        ============================
         Smart Text Summarizer
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 60

    return (
        f"{separator}\n"
        f"  Smart Text Summarizer — AI-Generated Summary\n"
        f"{separator}\n\n"
        f"Generated : {timestamp}\n"
        f"Length    : {length_preset}\n"
        f"Original  : {count_words(original_text)} words\n"
        f"Summary   : {count_words(summary)} words\n"
        f"Compressed: {compression_percentage(original_text, summary)}%\n\n"
        f"{separator}\n"
        f"SUMMARY\n"
        f"{separator}\n\n"
        f"{summary}\n\n"
        f"{separator}\n"
        f"ORIGINAL TEXT\n"
        f"{separator}\n\n"
        f"{original_text}\n"
    )


# ---------------------------------------------------------------------------
# Formatted statistics dict
# ---------------------------------------------------------------------------

def format_stats(original: str, summary: str) -> dict[str, str]:
    """
    Build a dictionary of display-ready statistics about the original text
    and its summary.

    Parameters:
        original (str): Original input text.
        summary  (str): AI-generated summary.

    Returns:
        dict[str, str]: Keys and their formatted string values:
            - original_words
            - original_chars
            - reading_time
            - summary_words
            - compression

    Example:
        >>> stats = format_stats(article, summary)
        >>> print(stats["compression"])
        '73.5%'
    """
    return {
        "original_words":  f"{count_words(original):,}",
        "original_chars":  f"{count_characters(original):,}",
        "reading_time":    estimate_reading_time(original),
        "summary_words":   f"{count_words(summary):,}",
        "compression":     f"{compression_percentage(original, summary)}%",
    }
