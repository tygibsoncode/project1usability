import streamlit as st
import pandas as pd
import time
import os
import random

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode="w", header=True, index=False)
    else:
        df_new.to_csv(csv_file, mode="a", header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    return pd.DataFrame()


def generate_shoe_ids(n=10):
    colors = ["BLK", "WHT", "RED", "BLU", "GRY", "PNK", "TAN", "NVY"]
    shoe_ids = set()

    while len(shoe_ids) < n:
        num = random.randint(100000, 999999)
        color = random.choice(colors)
        shoe_ids.add(f"{num}{color}")

    return list(shoe_ids)


def main():
    st.set_page_config(page_title="Usability Testing Tool", layout="wide")
    st.title("Usability Testing Tool")

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = None
    if "task_duration" not in st.session_state:
        st.session_state["task_duration"] = None
    if "current_shoe_ids" not in st.session_state:
        st.session_state["current_shoe_ids"] = None
    if "target_shoe_id" not in st.session_state:
        st.session_state["target_shoe_id"] = None
    if "task_started" not in st.session_state:
        st.session_state["task_started"] = False

    home, consent, demographics, tasks, exit_tab, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"]
    )

    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool.

        This usability test is designed to evaluate how easily users can search for
        a shoe in a shoe inventory system by matching a shoe ID to the correct item.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Complete a shoe inventory lookup task.
        4. Answer an exit questionnaire about your experience.
        5. View a summary report of the collected data.
        """)

    with consent:
        st.header("Consent Form")

        st.write("""
        This usability test evaluates how easily users can locate a shoe in an inventory system
        by using a shoe ID.

        By participating in this study:
        - Your responses may be collected for academic purposes.
        - Your participation is voluntary.
        - You may stop at any time.
        - Your responses will only be used to evaluate usability.

        Please indicate your consent below.
        """)

        participant_name = st.text_input("Participant Name (optional)")
        consent_given = st.checkbox("I agree to participate in this usability test.")

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "participant_name": participant_name,
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Consent form submitted successfully.")

    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("Name (optional)")
            age = st.number_input("Age", min_value=1, max_value=120, step=1)
            occupation = st.text_input("Occupation")
            familiarity = st.selectbox(
                "How familiar are you with inventory or retail systems?",
                ["Not Familiar", "Somewhat Familiar", "Very Familiar"]
            )
            shopping_frequency = st.selectbox(
                "How often do you shop for shoes or browse shoe websites?",
                ["Rarely", "Sometimes", "Often", "Very Often"]
            )

            submitted = st.form_submit_button("Submit Demographics")

            if submitted:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name,
                    "age": age,
                    "occupation": occupation,
                    "familiarity": familiarity,
                    "shopping_frequency": shopping_frequency
                }
                save_to_csv(data_dict, DEMOGRAPHIC_CSV)
                st.success("Demographic data saved successfully.")

    with tasks:
        st.header("Task Page - Shoe Inventory Lookup")

        st.write("""
        In this task, you will simulate using a shoe inventory system.

        You will be given one shoe ID to search for.
        Your job is to locate the matching shoe ID from a list of 10 options
        as quickly and accurately as possible.
        """)

        if st.button("Generate New Task"):
            shoe_ids = generate_shoe_ids(10)
            target_id = random.choice(shoe_ids)

            st.session_state["current_shoe_ids"] = shoe_ids
            st.session_state["target_shoe_id"] = target_id
            st.session_state["start_time"] = None
            st.session_state["task_duration"] = None
            st.session_state["task_started"] = False

        if st.session_state["current_shoe_ids"] is not None:
            st.subheader("Find this Shoe ID:")
            st.code(st.session_state["target_shoe_id"])

            if st.button("Start Task Timer"):
                st.session_state["start_time"] = time.time()
                st.session_state["task_started"] = True
                st.success("Task timer started.")

            selected_shoe = st.radio(
                "Select the matching Shoe ID",
                st.session_state["current_shoe_ids"]
            )

            observer_notes = st.text_area("Observer Notes")

            if st.button("Submit Selection"):
                if st.session_state["start_time"] is not None:
                    duration = time.time() - st.session_state["start_time"]
                    st.session_state["task_duration"] = round(duration, 2)
                else:
                    st.session_state["task_duration"] = ""

                correct = selected_shoe == st.session_state["target_shoe_id"]

                if correct:
                    st.success("Correct shoe selected!")
                else:
                    st.error("Incorrect shoe selected.")

                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "target_shoe_id": st.session_state["target_shoe_id"],
                    "selected_shoe_id": selected_shoe,
                    "correct": correct,
                    "duration_seconds": st.session_state["task_duration"],
                    "notes": observer_notes
                }
                save_to_csv(data_dict, TASK_CSV)

                st.success("Task results saved successfully.")

                st.session_state["start_time"] = None
                st.session_state["task_duration"] = None
                st.session_state["task_started"] = False
        else:
            st.info("Click 'Generate New Task' to begin.")

    with exit_tab:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            ease_of_search = st.slider(
                "How easy was it to locate the correct shoe ID?",
                1, 5, 3
            )
            clarity = st.slider(
                "How clear was the interface for selecting shoe IDs?",
                1, 5, 3
            )
            efficiency = st.slider(
                "How satisfied were you with the speed of the task?",
                1, 5, 3
            )
            confidence = st.slider(
                "How confident are you that you could use this system again?",
                1, 5, 3
            )
            open_feedback = st.text_area(
                "What improvements would make this shoe lookup system easier to use?"
            )

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")

            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "ease_of_search": ease_of_search,
                    "clarity": clarity,
                    "efficiency": efficiency,
                    "confidence": confidence,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)
                st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")

        if not task_df.empty:
            st.subheader("Task Performance Summary")

            if "duration_seconds" in task_df.columns:
                task_df["duration_seconds"] = pd.to_numeric(
                    task_df["duration_seconds"], errors="coerce"
                )
                avg_time = task_df["duration_seconds"].mean()
                if pd.notna(avg_time):
                    st.write(f"**Average Task Completion Time:** {avg_time:.2f} seconds")

            if "correct" in task_df.columns:
                accuracy = task_df["correct"].astype(str).str.lower().map(
                    {"true": 1, "false": 0}
                ).mean() * 100
                if pd.notna(accuracy):
                    st.write(f"**Accuracy Rate:** {accuracy:.1f}%")

                st.subheader("Correct vs Incorrect Selections")
                correct_counts = task_df["correct"].astype(str).value_counts()
                st.bar_chart(correct_counts)

        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")

            for col in ["ease_of_search", "clarity", "efficiency", "confidence"]:
                if col in exit_df.columns:
                    exit_df[col] = pd.to_numeric(exit_df[col], errors="coerce")

            if all(col in exit_df.columns for col in ["ease_of_search", "clarity", "efficiency", "confidence"]):
                st.write(f"**Average Ease of Search:** {exit_df['ease_of_search'].mean():.2f}")
                st.write(f"**Average Clarity:** {exit_df['clarity'].mean():.2f}")
                st.write(f"**Average Efficiency:** {exit_df['efficiency'].mean():.2f}")
                st.write(f"**Average Confidence:** {exit_df['confidence'].mean():.2f}")

                st.subheader("Exit Ratings Overview")
                st.bar_chart(exit_df[["ease_of_search", "clarity", "efficiency", "confidence"]].mean())


if __name__ == "__main__":
    main()
