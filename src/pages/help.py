import streamlit as st
import pandas as pd


def render_help_page() -> None:
    """
    Render the Help & Documentation page for the Solar PV Fault Detection system.
    """

    st.title("📖 Help & Documentation")
    st.markdown("Everything you need to get up and running with the Solar PV Fault Detection system.")

    st.divider()

    with st.expander("🚀 Getting Started", expanded=True):  # Occupy the space
        st.markdown(
            """
            Welcome! This system helps you detect faults in your solar PV installation
            using electrical sensor data or thermal images.

            Follow these steps to begin:

            **1. Log In**
            - Navigate to the **Login** page.
            - Enter your username and password.
            - Your session will be active until you log out.

            **2. Configure Your PV System** *(optional but recommended)*
            - Go to **PV System Configuration**.
            - Choose your system type (Solar Farm, Grid-Tied, Off-Grid, or Hybrid).
            - Set the number of modules per string.
            - Click **Save PV System**.

            **3. Run a Fault Detection**

            You have two options depending on your data type:

            | Mode | Tab | Input |
            |------|-----|-------|
            | Electrical (CSV) | 📄 CSV Batch Analysis | Upload a `.csv` file |
            | Thermal (Image) | 🖼️ Thermal Vision | Upload a `.jpg` or `.png` |

            **4. Read Your Results**
            - The system will display a **fault type** and a **confidence score**.
            - In CSV mode, click a row in the results table to get an **AI explanation**
              of why that string was flagged.
            """
        )


    with st.expander("📄 Using CSV Batch Analysis"):
        st.markdown(
            """
            This mode processes multiple solar strings at once from a single CSV file.

            **Required Columns**

            Your CSV must contain these columns (column names are case-sensitive):
            """
        )

        col_data = {
            "Column": ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"],
            "Description": [
                "DC voltage — String 1 (V)",
                "DC voltage — String 2 (V)",
                "DC current — String 1 (A)",
                "DC current — String 2 (A)",
                "Solar irradiance (W/m²)",
                "Module temperature (°C)",
            ],
        }

        st.table(pd.DataFrame(col_data))

        st.markdown(
            """
            **Steps**
            1. Click **Browse files** and upload your `.csv`.
            2. Expand **Preview Uploaded Data** to verify the file loaded correctly.
            3. Click **Analyze CSV Data**.
            4. Review the per-string results table.
            5. Tick a row checkbox and scroll down to see the **AI Explanation** for that string.

            > 💡 The AI explanation shows which sensor readings had the biggest influence
            > on the fault prediction, helping you prioritise where to inspect first.
            """
        )

    with st.expander("🖼️ Using Thermal Vision"):
        st.markdown(
            """
            This mode analyses a thermal camera image of your panels to detect hotspots.

            **Supported formats:** `.jpg`, `.jpeg`, `.png`

            **Steps**
            1. Switch to the **🖼️ Thermal Vision** tab.
            2. Upload a thermal image of your panels.
            3. Confirm the image looks correct in the preview.
            4. Click **Scan for Hotspots**.
            5. The system will return a **fault classification** and **confidence score**.

            **Fault types detected**
            - `Healthy` — No hotspot anomalies found.
            - `Hotspot` — Detected a single heating/hotspot on one cell.

            > 💡 For best results, capture images under consistent irradiance.
            """
        )

    with st.expander("❓ Frequently Asked Questions"):
        faqs = [
            (
                "Why is my CSV being rejected?",
                "The most common cause is missing or misspelled column names. "
                "Check that your file contains all six required columns: "
                "`vdc1`, `vdc2`, `idc1`, `idc2`, `irradiance`, `temperature`. "
                "Column names are case-sensitive.",
            ),
            (
                "What does the confidence score mean?",
                "Confidence is a percentage representing how certain the model is about "
                "its prediction. A score above 85% is considered high confidence. "
                "Scores below 60% suggest the reading is borderline — consider manual inspection.",
            ),
            (
                "Why does the AI Explanation only appear after I select a row?",
                "Generating an explanation is computationally intensive. "
                "It runs on-demand for a single selected string rather than for all rows at once, "
                "which keeps response times fast.",
            ),
            (
                "Can I upload multiple thermal images at once?",
                "Not currently. The Thermal Vision tab processes one image per submission. "
                "For bulk thermal analysis, please use the CSV mode with electrical sensor data.",
            ),
            (
                "How do I save my PV system settings?",
                "Go to **PV System Configuration**, fill in your system type and modules per string, "
                "then click **Save PV System**. Your settings will pre-populate on your next visit.",
            ),
        ]

        for question, answer in faqs:
            st.markdown(f"**Q: {question}**")
            st.markdown(f"A: {answer}")
            st.markdown("")

    st.divider()
    st.caption("Still stuck? Contact your system administrator.")
