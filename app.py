import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

APP_TITLE = "Taifa Teule"
DB = "taifa_teule.db"

FIELDS = [
    "week", "class_name", "senior_facilitator", "facilitators_present",
    "facilitators_absent", "expected_members", "present_members",
    "energy_rating", "engagement_rating", "what_went_well",
    "challenges", "action_taken", "areas_for_improvement",
    "member_participation", "next_week_action_plan", "submitted_by"
]

def db():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_at TEXT,
            week TEXT,
            class_name TEXT,
            senior_facilitator TEXT,
            facilitators_present TEXT,
            facilitators_absent TEXT,
            expected_members INTEGER,
            present_members INTEGER,
            energy_rating INTEGER,
            engagement_rating INTEGER,
            what_went_well TEXT,
            challenges TEXT,
            action_taken TEXT,
            areas_for_improvement TEXT,
            member_participation TEXT,
            next_week_action_plan TEXT,
            submitted_by TEXT
        )
    """)
    con.commit()
    return con

def get_reports():
    con = db()
    df = pd.read_sql_query("SELECT * FROM reports ORDER BY id DESC", con)
    con.close()
    return df

def add_report(values):
    con = db()
    cols = ["submitted_at"] + FIELDS
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO reports ({','.join(cols)}) VALUES ({placeholders})"
    con.execute(sql, [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + values)
    con.commit()
    con.close()

def excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reports")
    output.seek(0)
    return output

st.set_page_config(
    page_title="Taifa Teule | Weekly Reporting",
    page_icon="🇰🇪",
    layout="wide"
)

st.markdown("""
<style>
.main-title {font-size: 42px; font-weight: 800; margin-bottom: 0;}
.subtitle {font-size: 20px; color: #666; margin-top: 0;}
.card {padding: 18px; border-radius: 12px; border: 1px solid #ddd;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🇰🇪 Taifa Teule</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Cluster 2 Weekly Reporting App</div>', unsafe_allow_html=True)
st.divider()

menu = st.sidebar.radio(
    "Navigation",
    ["Submit Weekly Report", "Dashboard", "All Reports"]
)

if menu == "Submit Weekly Report":
    st.header("Weekly Class Report")
    st.caption("Complete one report for each class/session.")

    with st.form("weekly_report", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            week = st.text_input("Week", placeholder="e.g. Week 2")
            class_name = st.text_input("Class / Location", placeholder="e.g. Ngara")
            sf = st.text_input("Senior Facilitator (SF)")
            present_fac = st.text_area(
                "Facilitators Present",
                placeholder="List names, separated by commas"
            )
            absent_fac = st.text_area(
                "Facilitators Absent",
                placeholder="List names, separated by commas"
            )
        with c2:
            expected = st.number_input("Expected Members", min_value=0, step=1)
            present = st.number_input("Members Present", min_value=0, step=1)
            energy = st.slider("Class Energy", 1, 10, 7)
            engagement = st.slider("Member Engagement", 1, 10, 7)
            submitted_by = st.text_input("Report Submitted By")

        st.subheader("Class Experience")
        what_went_well = st.text_area(
            "What went well?",
            placeholder="Describe the strongest parts of the session."
        )
        challenges = st.text_area(
            "Challenges Encountered",
            placeholder="Attendance, facilitation, time management, technology, participation, etc."
        )
        action_taken = st.text_area(
            "Action Taken",
            placeholder="What did the facilitation team do about the challenges?"
        )
        areas = st.text_area(
            "Areas for Improvement",
            placeholder="What should the team improve?"
        )

        st.subheader("Member Participation")
        participation = st.text_area(
            "Member Participation Observations",
            placeholder="Mention quieter members, highly engaged members, participation gaps, etc."
        )
        next_plan = st.text_area(
            "Next-Week Action Plan",
            placeholder="Specific actions for the next session."
        )

        submitted = st.form_submit_button(
            "Submit Taifa Teule Weekly Report",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not week or not class_name or not sf or not submitted_by:
                st.error("Please complete Week, Class/Location, SF and Submitted By.")
            elif present > expected and expected > 0:
                st.warning("Members present cannot normally exceed expected members. Please check the figures.")
            else:
                add_report([
                    week, class_name, sf, present_fac, absent_fac,
                    int(expected), int(present), int(energy), int(engagement),
                    what_went_well, challenges, action_taken, areas,
                    participation, next_plan, submitted_by
                ])
                st.success("Report submitted successfully to Taifa Teule.")
                st.balloons()

elif menu == "Dashboard":
    st.header("Taifa Teule Dashboard")
    df = get_reports()

    if df.empty:
        st.info("No reports have been submitted yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Reports", len(df))
        c2.metric("Members Expected", int(df["expected_members"].sum()))
        c3.metric("Members Present", int(df["present_members"].sum()))
        c4.metric("Average Engagement", f'{df["engagement_rating"].mean():.1f}/10')

        st.divider()

        weeks = ["All"] + sorted(df["week"].dropna().unique().tolist())
        classes = ["All"] + sorted(df["class_name"].dropna().unique().tolist())

        f1, f2 = st.columns(2)
        selected_week = f1.selectbox("Filter by Week", weeks)
        selected_class = f2.selectbox("Filter by Class", classes)

        filtered = df.copy()
        if selected_week != "All":
            filtered = filtered[filtered["week"] == selected_week]
        if selected_class != "All":
            filtered = filtered[filtered["class_name"] == selected_class]

        if filtered.empty:
            st.warning("No reports match the selected filters.")
        else:
            a, b = st.columns(2)
            with a:
                st.subheader("Attendance by Class")
                attendance = filtered.groupby("class_name", as_index=False)[
                    ["expected_members", "present_members"]
                ].sum()
                st.bar_chart(attendance.set_index("class_name"))
            with b:
                st.subheader("Energy & Engagement")
                ratings = filtered.groupby("class_name", as_index=False)[
                    ["energy_rating", "engagement_rating"]
                ].mean()
                st.bar_chart(ratings.set_index("class_name"))

            st.subheader("Reports Summary")
            summary = filtered[[
                "week", "class_name", "senior_facilitator",
                "expected_members", "present_members",
                "energy_rating", "engagement_rating"
            ]]
            st.dataframe(summary, use_container_width=True, hide_index=True)

            st.subheader("Common Challenge Notes")
            for _, row in filtered.iterrows():
                with st.expander(f'{row["week"]} — {row["class_name"]}'):
                    st.write("**Challenges:**", row["challenges"] or "None recorded")
                    st.write("**Action Taken:**", row["action_taken"] or "Not recorded")
                    st.write("**Improvement:**", row["areas_for_improvement"] or "Not recorded")

else:
    st.header("All Submitted Reports")
    df = get_reports()

    if df.empty:
        st.info("No reports have been submitted yet.")
    else:
        search = st.text_input("Search reports", placeholder="Search class, SF, week, facilitator...")
        view = df.copy()

        if search:
            mask = view.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            view = view[mask]

        st.write(f"Showing **{len(view)}** report(s).")
        st.dataframe(view, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download CSV",
                view.to_csv(index=False).encode("utf-8"),
                "taifa_teule_cluster2_reports.csv",
                "text/csv",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "Download Excel",
                excel_bytes(view),
                "taifa_teule_cluster2_reports.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.sidebar.divider()
st.sidebar.caption("Taifa Teule • Cluster 2 Weekly Reporting")
