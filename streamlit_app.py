import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from token_estimator import (
    DEFAULT_CONTEXT_LIMIT,
    estimate_file,
    estimate_prompt,
    summarize,
)

st.set_page_config(
    page_title="Son Spectacles Context Budget Estimator",
    layout="wide",
)

st.title("Son Spectacles Context Budget Estimator")

st.caption(
    "Estimate parsed/extracted text tokens for a Son Spectacles prompt and "
    "its reference files. Supports the project file types: PDF, DOCX, PPTX, "
    "XLSX, CSV, TXT, JSON, PY, MD, HTML, and XML. This is an approximation "
    "and may differ from the exact tokenizer used by the target model."
)

context_limit = st.number_input(
    "Context limit",
    value=DEFAULT_CONTEXT_LIMIT,
    step=10_000,
    min_value=10_000,
)

prompt_text = st.text_area(
    "Paste prompt text here",
    height=180,
    placeholder="Optional: paste the turn prompt to include it in the budget.",
)

files = st.file_uploader(
    "Upload files to estimate",
    type=[
        "pdf",
        "docx",
        "pptx",
        "xlsx",
        "csv",
        "txt",
        "json",
        "py",
        "md",
        "html",
        "xml",
    ],
    accept_multiple_files=True,
)

st.caption(f"Reference files selected: {len(files)} / 20")

if len(files) > 20:
    st.error(
        "Son Spectacles allows at most 20 reference files. "
        "The estimator can still calculate the token total, but the task "
        "itself should be reduced to 20 files or fewer."
    )

if st.button("Estimate context budget", type="primary"):
    estimates = []

    if prompt_text.strip():
        estimates.append(
            estimate_prompt(
                prompt_text,
                int(context_limit),
            )
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        for uploaded in files:
            safe_name = Path(uploaded.name).name
            tmp_path = Path(tmpdir) / safe_name

            tmp_path.write_bytes(uploaded.getvalue())

            estimates.append(
                estimate_file(
                    tmp_path,
                    int(context_limit),
                )
            )

    if not estimates:
        st.warning("Add a prompt and/or upload files first.")

    else:
        summary = summarize(
            estimates,
            int(context_limit),
        )

        st.subheader("Estimated turn budget")

        st.metric(
            "Estimated tokens",
            f"{summary['total_estimated_tokens']:,}",
            f"{summary['percent_of_limit']}% of limit",
        )

        progress_value = min(
            summary["total_estimated_tokens"] / int(context_limit),
            1.0,
        )

        st.progress(progress_value)

        status = summary["status"]

        if status == "SAFE":
            st.success("Status: SAFE")

        elif status == "CLOSE_TO_LIMIT":
            st.warning("Status: CLOSE TO LIMIT")

        elif status == "LIKELY_OVER_LIMIT_SOON":
            st.warning("Status: LIKELY OVER LIMIT SOON")

        elif status == "CRITICAL":
            st.error("Status: CRITICAL")

        else:
            st.error(f"Status: {status}")

        rows = []

        for estimate in sorted(
            estimates,
            key=lambda item: item.estimated_tokens,
            reverse=True,
        ):
            rows.append(
                {
                    "File": Path(estimate.file).name,
                    "Type": estimate.extension,
                    "Size MB": estimate.size_mb,
                    "Characters": estimate.characters,
                    "Words": estimate.words,
                    "Estimated tokens": estimate.estimated_tokens,
                    "% of limit": round(
                        estimate.estimated_tokens
                        / int(context_limit)
                        * 100,
                        1,
                    ),
                    "Risk": estimate.risk_band,
                    "Notes": estimate.extraction_notes,
                }
            )

        dataframe = pd.DataFrame(rows)

        st.subheader("Per-file estimates")

        st.dataframe(
            dataframe,
            width="stretch",
            hide_index=True,
        )

        st.subheader("Largest contributors")

        for item in summary["largest_contributors"]:
            filename = Path(item["file"]).name
            tokens = item["estimated_tokens"]

            st.write(
                f"- **{filename}** — {tokens:,} tokens"
            )

        csv_report = dataframe.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download CSV report",
            data=csv_report,
            file_name="son_spectacles_context_budget_report.csv",
            mime="text/csv",
        )

st.divider()

st.markdown(
    """
**Interpretation:** File size in MB is not the most important metric. The relevant estimate is the amount of extracted text after the files are parsed. A small but text-dense PDF can use more context than a larger image-heavy PDF.

**Supported extraction:** PDF, DOCX, PPTX, XLSX, CSV, TXT, JSON, PY, MD, HTML, and XML. Image-only content is not OCR-scanned in this prototype.

**Reference-file check:** Son Spectacles tasks allow 1–20 reference files. The prompt is counted separately.

**Recommended bands:** Under 70% of the selected context limit is usually safer, 70–85% requires caution, 85–95% is risky, and above 95% is critical because hidden system and response overhead may also consume context.
"""
)

st.markdown(
    """
    <div style="
        text-align: center;
        color: #888;
        font-size: 0.85rem;
        margin-top: 2rem;
    ">
        Kenneth Pedersen · 2026
    </div>
    """,
    unsafe_allow_html=True,
)
