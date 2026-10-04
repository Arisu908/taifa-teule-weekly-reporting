# Taifa Teule — Cluster 2 Weekly Reporting App

## Run on your computer

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run:

    pip install -r requirements.txt

4. Start the app:

    streamlit run app.py

The browser will open the Taifa Teule reporting app.

## Put it online

The easiest option is Streamlit Community Cloud:
1. Create a GitHub repository.
2. Upload `app.py` and `requirements.txt`.
3. Connect the repository to Streamlit Community Cloud.
4. Select `app.py` as the main file.
5. Deploy.

Important: the included SQLite database is suitable for a simple/local deployment. For a multi-user public deployment, use a cloud database such as PostgreSQL so reports are safely shared and persistent.
