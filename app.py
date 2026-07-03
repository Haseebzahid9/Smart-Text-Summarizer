"""
app.py
------
Streamlit front-end for Smart Text Summarizer.

Responsibilities:
    - Render the full UI (header, input form, results, statistics, footer)
    - Validate user input via utils.validate_input()
    - Call summarizer.summarize_text() to generate the summary
    - Display statistics cards (word count, compression %, reading time)
    - Provide download and copy functionality

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from summarizer import summarize_text, load_model
from utils import (
    count_words,
    count_characters,
    estimate_reading_time,
    validate_input,
    get_download_content,
    format_stats,
)


# ---------------------------------------------------------------------------
# Page configuration  (must be the very first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Text Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Custom CSS — minimal, clean styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        /* ---- Global font ---- */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* ---- Stat cards ---- */
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 18px 20px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .stat-card .label {
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.85;
            margin-bottom: 6px;
        }
        .stat-card .value {
            font-size: 1.65rem;
            font-weight: 700;
            line-height: 1.1;
        }

        /* ---- Section headers ---- */
        .section-header {
            color: #4a4a8a;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        /* ---- Footer ---- */
        .footer {
            text-align: center;
            color: #888;
            font-size: 0.83rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
            margin-top: 3rem;
        }

        /* ---- Hide Streamlit hamburger menu (cleaner look) ---- */
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper: render a single stat card
# ---------------------------------------------------------------------------

def _stat_card(label: str, value: str) -> str:
    """Return the HTML for one statistics card."""
    return (
        f'<div class="stat-card">'
        f'  <div class="label">{label}</div>'
        f'  <div class="value">{value}</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div style="text-align:center; padding: 1.5rem 0 0.5rem;">
        <h1 style="font-size:2.6rem; font-weight:800; color:#4a4a8a; margin-bottom:0;">
            📚 Smart Text Summarizer
        </h1>
        <p style="font-size:1.1rem; color:#666; margin-top:0.4rem;">
            Generate concise AI-powered summaries from long documents.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ---------------------------------------------------------------------------
# Warm-up: load model in the background on first visit so the first click
# is fast.  We display a small notice while it loads.
# ---------------------------------------------------------------------------

with st.spinner("🤖 Loading AI model (one-time download on first run)…"):
    try:
        load_model()
        model_ready = True
    except Exception as exc:
        model_ready = False
        st.error(
            f"❌ Failed to load the AI model.\n\n"
            f"**Error:** {exc}\n\n"
            "Please check your internet connection and try again."
        )


# ---------------------------------------------------------------------------
# Two-column layout: left = input, right = output
# ---------------------------------------------------------------------------

col_left, col_right = st.columns([1, 1], gap="large")

# ---- LEFT COLUMN: Input form ----
with col_left:
    st.markdown('<p class="section-header">✏️ Input Text</p>', unsafe_allow_html=True)

    input_text: str = st.text_area(
        label="Paste your article, essay, or document here:",
        height=320,
        placeholder=(
            "Paste a long article, blog post, essay, report, or any document "
            "here…\n\n"
            "Tip: aim for at least 100 words for the best results."
        ),
        key="input_text",
    )

    # Live statistics beneath the text area
    if input_text.strip():
        word_c = count_words(input_text)
        char_c = count_characters(input_text)
        read_t = estimate_reading_time(input_text)
        st.caption(
            f"📊 **{word_c:,} words** &nbsp;|&nbsp; "
            f"**{char_c:,} characters** &nbsp;|&nbsp; "
            f"⏱ Est. reading time: **{read_t}**"
        )

    # Summary length selector
    st.markdown('<p class="section-header" style="margin-top:1rem;">📏 Summary Length</p>', unsafe_allow_html=True)
    length_preset: str = st.radio(
        label="Choose how long the summary should be:",
        options=["Short", "Medium", "Long"],
        index=1,          # default = Medium
        horizontal=True,
        help=(
            "Short ≈ 40–80 tokens · "
            "Medium ≈ 80–180 tokens · "
            "Long ≈ 150–350 tokens"
        ),
    )

    # Action buttons
    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        generate_clicked = st.button(
            "✨ Generate Summary",
            type="primary",
            use_container_width=True,
            disabled=not model_ready,
        )
    with btn_col2:
        clear_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
        )

    # Clear button: reset the text area via session state
    if clear_clicked:
        st.session_state["input_text"] = ""
        st.rerun()


# ---- RIGHT COLUMN: Output / Results ----
with col_right:
    st.markdown('<p class="section-header">📝 Summary</p>', unsafe_allow_html=True)

    # Placeholder message when no summary has been generated yet
    if "summary" not in st.session_state:
        st.info(
            "Your AI-generated summary will appear here after you click "
            "**✨ Generate Summary**.",
            icon="💡",
        )

    # ---- Generate Summary ----
    if generate_clicked:
        is_valid, error_msg = validate_input(input_text)

        if not is_valid:
            st.warning(f"⚠️ {error_msg}", icon="⚠️")
        else:
            with st.spinner("🔄 Generating summary… this may take a moment."):
                try:
                    summary = summarize_text(input_text, length_preset)
                    st.session_state["summary"] = summary
                    st.session_state["original"] = input_text
                    st.session_state["preset"] = length_preset
                    st.success("✅ Summary generated successfully!", icon="✅")
                except ValueError as ve:
                    st.error(f"❌ Configuration error: {ve}")
                except RuntimeError as re_err:
                    st.error(f"❌ Model error: {re_err}")
                except Exception as exc:
                    st.error(
                        f"❌ An unexpected error occurred: {exc}\n\n"
                        "Please try again with different text."
                    )

    # ---- Display summary if available ----
    if "summary" in st.session_state and st.session_state["summary"]:
        summary_text    = st.session_state["summary"]
        original_text   = st.session_state.get("original", input_text)
        used_preset     = st.session_state.get("preset", length_preset)

        # Summary output box (non-editable styled text area)
        st.text_area(
            label="Generated Summary:",
            value=summary_text,
            height=200,
            key="summary_output",
        )

        # Copy  +  Download buttons
        dl_col, copy_col = st.columns(2)

        with dl_col:
            download_content = get_download_content(
                original_text, summary_text, used_preset
            )
            st.download_button(
                label="⬇️ Download as TXT",
                data=download_content,
                file_name="summary.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with copy_col:
            # Streamlit doesn't have a native clipboard button; we use a
            # small HTML/JS snippet instead.
            copy_js = f"""
                <button onclick="navigator.clipboard.writeText(`{summary_text.replace('`', "'")}`).then(()=>{{
                    this.innerText='✅ Copied!';
                    setTimeout(()=>this.innerText='📋 Copy Summary', 2000);
                }})"
                style="
                    width:100%; padding:0.5rem 1rem;
                    background:#4a4a8a; color:white;
                    border:none; border-radius:6px;
                    font-size:0.9rem; cursor:pointer;
                ">
                📋 Copy Summary
                </button>
            """
            st.markdown(copy_js, unsafe_allow_html=True)

        st.divider()

        # ---- Statistics cards ----
        st.markdown('<p class="section-header">📊 Statistics</p>', unsafe_allow_html=True)
        stats = format_stats(original_text, summary_text)

        c1, c2, c3 = st.columns(3)
        c1.markdown(_stat_card("Original Words", stats["original_words"]), unsafe_allow_html=True)
        c2.markdown(_stat_card("Summary Words",  stats["summary_words"]),  unsafe_allow_html=True)
        c3.markdown(_stat_card("Compression",    stats["compression"]),    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        c4, c5 = st.columns(2)
        c4.markdown(_stat_card("Characters",   stats["original_chars"]), unsafe_allow_html=True)
        c5.markdown(_stat_card("Reading Time", stats["reading_time"]),   unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Expandable sections ----
        with st.expander("📄 View Original Text"):
            st.write(original_text)

        with st.expander("🔍 View Summary (formatted)"):
            st.markdown(f"> {summary_text}")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Built with ❤️ using Python, Streamlit &amp; Hugging Face Transformers
        &nbsp;·&nbsp;
        Model: <strong>facebook/bart-large-cnn</strong>
        &nbsp;·&nbsp;
        <a href="https://github.com/Haseebzahid9/Smart-Text-Summarizer" target="_blank">
            GitHub
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
