# admin_gui.py
import json
from pathlib import Path

import streamlit as st
import sqlite3

# Compatibility for older Streamlit versions
if not hasattr(st, "rerun"):
    try:
        st.rerun = st.experimental_rerun
    except AttributeError:
        # Fallback if neither exists (very old versions), though unlikely to work well
        pass

# --- CONFIG ---
st.set_page_config(
    page_title="JobFlow Admin Panel",
    layout="wide",
)

DB_PATH = Path(__file__).parent / "jobs.db"


# --- DB HELPERS ---
def get_conn():
    # افتح connection جديد في كل مرة، واسمح باستخدامه في Threads مختلفة
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(query, params=()):
    conn = get_conn()
    try:
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def exec_query(query, params=()):
    """Execute INSERT/UPDATE/DELETE."""
    conn = get_conn()
    try:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def edit_row(table_name, pk_name, row_dict, readonly_fields=None, extra_disable=None):
    """
    Generic editor for a single row.
    - table_name: name of the table in DB
    - pk_name: primary key column name
    - row_dict: dict(row)
    - readonly_fields: list of columns to show as disabled
    """
    if readonly_fields is None:
        readonly_fields = [pk_name]
    if extra_disable:
        readonly_fields = list(set(readonly_fields + extra_disable))

    pk_value = row_dict[pk_name]

    st.write("#### Edit row")

    new_values = {}
    for col, val in row_dict.items():
        key = f"{table_name}_{pk_name}_{pk_value}_{col}"
        str_val = "" if val is None else str(val)

        if col in readonly_fields:
            st.text_input(col, str_val, disabled=True, key=key)
        else:
            new_val = st.text_input(col, str_val, key=key)
            new_values[col] = new_val

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save changes", key=f"save_{table_name}_{pk_value}"):
            if new_values:
                set_clause = ", ".join([f"{c} = ?" for c in new_values.keys()])
                params = list(new_values.values()) + [pk_value]
                exec_query(
                    f"UPDATE {table_name} SET {set_clause} WHERE {pk_name} = ?",
                    params,
                )
                st.success("Row updated.")
                st.rerun()
    with col2:
        if st.button("🗑️ Delete row", key=f"delete_{table_name}_{pk_value}"):
            exec_query(
                f"DELETE FROM {table_name} WHERE {pk_name} = ?",
                (pk_value,),
            )
            st.warning("Row deleted.")
            st.rerun()


def create_row(table_name, row_data):
    """
    Insert a new row into the table.
    row_data: dict of {column: value}
    """
    keys = list(row_data.keys())
    vals = list(row_data.values())
    placeholders = ",".join(["?"] * len(keys))
    cols = ",".join(keys)
    
    query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    exec_query(query, vals)


# --- UI ---
st.title("🧠 Neuronix AI JobFlow – Admin Panel")
st.caption("Browse and edit data inside your AI-Based Job Recommendation database.")

# لاحظ إننا شلنا تاب Contact
tab_users, tab_searches, tab_results, tab_saved, tab_tokens = st.tabs(
    ["👤 Users", "🔍 Searches", "📄 Job Results", "⭐ Saved Jobs", "🔑 Reset Tokens"]
)

# ========== USERS ==========
with tab_users:
    st.subheader("Users")

    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            new_email = c1.text_input("Email")
            new_pass = c2.text_input("Password Hash", value="123456")
            new_name = st.text_input("Full Name")
            
            if st.form_submit_button("Create User"):
                if new_email and new_pass:
                    try:
                        create_row("users", {
                            "email": new_email,
                            "password_hash": new_pass,
                            "full_name": new_name,
                            "is_active": 1
                        })
                        st.success("User created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating user: {e}")
                else:
                    st.error("Email and Password are required.")

    users = run_query(
        "SELECT id, email, full_name, created_at, last_login, is_active "
        "FROM users ORDER BY created_at DESC"
    )

    if users:
        st.dataframe(users, use_container_width=True)

        user_ids = [u["id"] for u in users]
        selected_id = st.selectbox("Select user to inspect/edit:", user_ids)

        if selected_id:
            user = run_query("SELECT * FROM users WHERE id = ?", (selected_id,))
            if user:
                row = user[0]
                st.write("### User details (JSON view)")
                st.json(row)

                # Editable form
                edit_row(
                    table_name="users",
                    pk_name="id",
                    row_dict=row,
                    readonly_fields=["id", "created_at", "last_login"],
                )

                st.write("### User searches")
                user_searches = run_query(
                    "SELECT * FROM searches WHERE user_id = ? ORDER BY created_at DESC",
                    (selected_id,),
                )
                st.dataframe(user_searches, use_container_width=True)

                st.write("### User saved jobs")
                saved = run_query(
                    """
                    SELECT sj.id as saved_id, sj.saved_at, sj.notes,
                           jr.job_title, jr.company, jr.platform, jr.url
                    FROM saved_jobs sj
                    JOIN job_results jr ON sj.job_result_id = jr.id
                    WHERE sj.user_id = ?
                    ORDER BY sj.saved_at DESC
                    """,
                    (selected_id,),
                )
                st.dataframe(saved, use_container_width=True)
    else:
        st.info("No users found in the database.")


# ========== SEARCHES ==========
with tab_searches:
    st.subheader("Search History")

    with st.expander("➕ Add New Search"):
        with st.form("add_search_form"):
            c1, c2 = st.columns(2)
            n_uid = c1.number_input("User ID", min_value=1, step=1)
            n_type = c2.selectbox("Search Type", ["form", "cv", "chat"])
            n_keywords = st.text_input("Keywords (comma separated)")
            n_data = st.text_area("Query Data (JSON)", value="{}")
            
            if st.form_submit_button("Create Search"):
                try:
                    create_row("searches", {
                        "user_id": n_uid,
                        "search_type": n_type,
                        "keywords": n_keywords,
                        "query_data": n_data
                    })
                    st.success("Search created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    search_type_filter = st.multiselect(
        "Filter by search type:",
        options=["form", "chat", "cv"],
        default=["form", "chat", "cv"],
    )

    if search_type_filter:
        placeholders = ",".join("?" * len(search_type_filter))
        searches = run_query(
            f"""
            SELECT s.*, u.email as user_email
            FROM searches s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE s.search_type IN ({placeholders})
            ORDER BY s.created_at DESC
            LIMIT 200
            """,
            tuple(search_type_filter),
        )
    else:
        searches = []

    if searches:
        st.dataframe(searches, use_container_width=True)

        search_ids = [s["id"] for s in searches]
        selected_search = st.selectbox("Select search to view/edit:", search_ids)

        if selected_search:
            s_row = [s for s in searches if s["id"] == selected_search][0]
            st.write("### Search details (JSON view)")
            s_display = dict(s_row)
            if s_display.get("query_data"):
                try:
                    s_display["query_data_parsed"] = json.loads(s_display["query_data"])
                except Exception:
                    pass
            st.json(s_display)

            # Load pure row from searches table (without joined user_email)
            pure_row = run_query("SELECT * FROM searches WHERE id = ?", (selected_search,))[0]
            edit_row(
                table_name="searches",
                pk_name="id",
                row_dict=pure_row,
                readonly_fields=["id", "created_at"],
            )

            st.write("### Job results for this search")
            res = run_query(
                """
                SELECT id, job_title, company, location,
                       match_score, platform, url, created_at
                FROM job_results
                WHERE search_id = ?
                ORDER BY match_score DESC
                """,
                (selected_search,),
            )
            st.dataframe(res, use_container_width=True)
    else:
        st.info("No searches found.")


# ========== JOB RESULTS ==========
with tab_results:
    st.subheader("Job Results")

    with st.expander("➕ Add New Job Result"):
        with st.form("add_job_form"):
            c1, c2 = st.columns(2)
            j_search_id = c1.number_input("Search ID", min_value=1, step=1)
            j_score = c2.number_input("Match Score", min_value=0.0, max_value=100.0, step=0.1)
            
            j_title = st.text_input("Job Title")
            j_company = st.text_input("Company")
            j_loc = st.text_input("Location")
            j_plat = st.text_input("Platform", value="LinkedIn")
            j_url = st.text_input("URL")
            
            if st.form_submit_button("Create Job Result"):
                try:
                    create_row("job_results", {
                        "search_id": j_search_id,
                        "job_title": j_title,
                        "company": j_company,
                        "location": j_loc,
                        "match_score": j_score,
                        "platform": j_plat,
                        "url": j_url
                    })
                    st.success("Job result created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # Optional filters
    col1, col2 = st.columns(2)
    with col1:
        platform_like = st.text_input("Filter by platform contains:")
    with col2:
        company_like = st.text_input("Filter by company contains:")

    query = """
        SELECT jr.id, jr.job_title, jr.company, jr.location,
               jr.match_score, jr.platform, jr.url,
               s.search_type, s.user_id
        FROM job_results jr
        LEFT JOIN searches s ON jr.search_id = s.id
        WHERE 1=1
    """
    params = []

    if platform_like:
        query += " AND jr.platform LIKE ?"
        params.append(f"%{platform_like}%")

    if company_like:
        query += " AND jr.company LIKE ?"
        params.append(f"%{company_like}%")

    query += " ORDER BY jr.created_at DESC LIMIT 300"

    jobs = run_query(query, tuple(params))

    if jobs:
        st.dataframe(jobs, use_container_width=True)

        ids = [j["id"] for j in jobs]
        selected_job = st.selectbox("Select job to inspect/edit:", ids)

        if selected_job:
            j_row = run_query("SELECT * FROM job_results WHERE id = ?", (selected_job,))[0]
            j_display = dict(j_row)
            if j_display.get("skills"):
                try:
                    j_display["skills_parsed"] = json.loads(j_display["skills"])
                except Exception:
                    pass
            st.write("### Job details (JSON view)")
            st.json(j_display)

            # Edit real columns only
            edit_row(
                table_name="job_results",
                pk_name="id",
                row_dict=j_row,
                readonly_fields=["id", "created_at"],
            )
    else:
        st.info("No job results found.")


# ========== SAVED JOBS ==========
with tab_saved:
    st.subheader("Saved Jobs (Bookmarks)")

    with st.expander("➕ Add Saved Job"):
        with st.form("add_saved_form"):
            c1, c2 = st.columns(2)
            s_uid = c1.number_input("User ID", min_value=1, step=1, key="saved_uid")
            s_jid = c2.number_input("Job Result ID", min_value=1, step=1, key="saved_jid")
            s_notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Job"):
                try:
                    create_row("saved_jobs", {
                        "user_id": s_uid,
                        "job_result_id": s_jid,
                        "notes": s_notes
                    })
                    st.success("Job saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    saved = run_query(
        """
        SELECT sj.id as saved_id, sj.saved_at, sj.notes,
               u.email as user_email,
               jr.job_title, jr.company, jr.platform, jr.url
        FROM saved_jobs sj
        JOIN users u ON sj.user_id = u.id
        JOIN job_results jr ON sj.job_result_id = jr.id
        ORDER BY sj.saved_at DESC
        """
    )

    if saved:
        st.dataframe(saved, use_container_width=True)

        saved_ids = [s["saved_id"] for s in saved]
        selected_saved = st.selectbox("Select saved job to edit:", saved_ids)

        if selected_saved:
            pure_row = run_query(
                "SELECT * FROM saved_jobs WHERE id = ?",
                (selected_saved,),
            )[0]
            st.write("### Saved job row (JSON view)")
            st.json(pure_row)

            edit_row(
                table_name="saved_jobs",
                pk_name="id",
                row_dict=pure_row,
                readonly_fields=["id"],
            )
    else:
        st.info("No saved jobs yet.")


# ========== PASSWORD RESET TOKENS ==========
with tab_tokens:
    st.subheader("Password Reset Tokens")

    with st.expander("➕ Add Reset Token"):
        with st.form("add_token_form"):
            t_uid = st.number_input("User ID", min_value=1, step=1, key="token_uid")
            t_token = st.text_input("Token")
            # Default expires in 1 hour
            
            if st.form_submit_button("Create Token"):
                import datetime
                expires = datetime.datetime.now() + datetime.timedelta(hours=1)
                try:
                    create_row("password_reset_tokens", {
                        "user_id": t_uid,
                        "token": t_token,
                        "expires_at": expires,
                        "used": 0
                    })
                    st.success("Token created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    tokens = run_query(
        """
        SELECT t.*, u.email as user_email
        FROM password_reset_tokens t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
        LIMIT 200
        """
    )

    if tokens:
        st.dataframe(tokens, use_container_width=True)

        token_ids = [t["id"] for t in tokens]
        selected_token = st.selectbox("Select token to view/edit:", token_ids)

        if selected_token:
            pure_row = run_query(
                "SELECT * FROM password_reset_tokens WHERE id = ?",
                (selected_token,),
            )[0]
            st.write("### Token row (JSON view)")
            st.json(pure_row)

            edit_row(
                table_name="password_reset_tokens",
                pk_name="id",
                row_dict=pure_row,
                readonly_fields=["id", "created_at"],
            )
    else:
        st.info("No reset tokens found.")
