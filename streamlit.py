import streamlit as st
import requests
from datetime import date
import pandas as pd


# =========================================================
# Configuration
# =========================================================

API_URL = "http://localhost:8000"


# =========================================================
# Categories
# =========================================================

categories = [
    "Food",
    "Rent",
    "Shopping",
    "Entertainment",
    "Other"
]


# =========================================================
# Page title
# =========================================================

st.title("Expense Management System")


# =========================================================
# Tabs
# =========================================================

tab1, tab2 = st.tabs([
    "Expense Management",
    "Analytics"
])


# =========================================================
# TAB 1: EXPENSE MANAGEMENT
# =========================================================

with tab1:

    st.header("Expense Management")


    # -----------------------------------------------------
    # Select date
    # -----------------------------------------------------

    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        key="expense_date"
    )

    selected_date_str = selected_date.strftime(
        "%Y-%m-%d"
    )


    # =====================================================
    # ADD EXPENSE
    # =====================================================

    st.subheader("Add Expense")


    with st.form("add_expense_form"):

        category = st.selectbox(
            "Category",
            categories,
            key="add_category"
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=1.0,
            key="add_amount"
        )

        notes = st.text_input(
            "Notes",
            key="add_notes"
        )

        add_button = st.form_submit_button(
            "Add Expense"
        )


    # -----------------------------------------------------
    # Add expense API call
    # -----------------------------------------------------

    if add_button:

        expense_data = {

            "expense_date": selected_date_str,

            "category": category,

            "amount": amount,

            "notes": notes
        }


        try:

            response = requests.post(
                f"{API_URL}/expenses",
                json=expense_data
            )


            if response.status_code == 200:

                st.success(
                    "Expense added successfully"
                )

                st.rerun()

            else:

                st.error(
                    f"Failed to add expense: "
                    f"{response.text}"
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI. "
                "Make sure the FastAPI server is running."
            )


    # =====================================================
    # FETCH EXPENSES
    # =====================================================

    st.subheader(
        f"Expenses for {selected_date_str}"
    )


    try:

        response = requests.get(
            f"{API_URL}/expenses/{selected_date_str}"
        )


        if response.status_code == 200:

            expenses = response.json()

        else:

            st.error(
                f"Failed to fetch expenses: "
                f"{response.text}"
            )

            expenses = []


    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to FastAPI."
        )

        expenses = []


    # =====================================================
    # DISPLAY EXPENSES
    # =====================================================

    if expenses:

        for expense in expenses:

            expense_id = expense["id"]


            st.markdown("---")


            # -------------------------------------------------
            # Expense information
            # -------------------------------------------------

            col1, col2, col3, col4 = st.columns(
                [1, 2, 1.5, 2]
            )


            with col1:

                st.write(
                    f"**ID:** {expense_id}"
                )


            with col2:

                st.write(
                    f"**Category:** "
                    f"{expense['category']}"
                )


            with col3:

                st.write(
                    f"**Amount:** "
                    f"₹{expense['amount']}"
                )


            with col4:

                st.write(
                    f"**Notes:** "
                    f"{expense['notes']}"
                )


            # -------------------------------------------------
            # Edit / Delete
            # -------------------------------------------------

            edit_col, delete_col = st.columns(2)


            # =================================================
            # EDIT BUTTON
            # =================================================

            with edit_col:

                if st.button(
                    "Edit",
                    key=f"edit_{expense_id}"
                ):

                    st.session_state[
                        f"editing_{expense_id}"
                    ] = True


            # =================================================
            # DELETE BUTTON
            # =================================================

            with delete_col:

                if st.button(
                    "Delete",
                    key=f"delete_{expense_id}"
                ):

                    try:

                        response = requests.delete(
                            f"{API_URL}/expenses/"
                            f"{expense_id}"
                        )


                        if response.status_code == 200:

                            st.success(
                                "Expense deleted successfully"
                            )

                            st.rerun()


                        else:

                            st.error(
                                f"Delete failed: "
                                f"{response.text}"
                            )


                    except requests.exceptions.ConnectionError:

                        st.error(
                            "Could not connect to FastAPI."
                        )


            # =================================================
            # EDIT FORM
            # =================================================

            if st.session_state.get(
                f"editing_{expense_id}",
                False
            ):

                st.markdown(
                    "### Edit Expense"
                )


                with st.form(
                    f"edit_form_{expense_id}"
                ):

                    # -----------------------------------------
                    # Category
                    # -----------------------------------------

                    current_category = expense[
                        "category"
                    ]

                    if current_category in categories:

                        category_index = categories.index(
                            current_category
                        )

                    else:

                        category_index = 0


                    edit_category = st.selectbox(
                        "Category",
                        categories,
                        index=category_index,
                        key=f"edit_category_{expense_id}"
                    )


                    # -----------------------------------------
                    # Amount
                    # -----------------------------------------

                    edit_amount = st.number_input(
                        "Amount",
                        min_value=0.0,
                        value=float(
                            expense["amount"]
                        ),
                        step=1.0,
                        key=f"edit_amount_{expense_id}"
                    )


                    # -----------------------------------------
                    # Notes
                    # -----------------------------------------

                    edit_notes = st.text_input(
                        "Notes",
                        value=expense["notes"],
                        key=f"edit_notes_{expense_id}"
                    )


                    # -----------------------------------------
                    # Update button
                    # -----------------------------------------

                    update_button = st.form_submit_button(
                        "Update Expense"
                    )


                # =================================================
                # UPDATE API CALL
                # =================================================

                if update_button:

                    updated_expense = {

                        "expense_date":
                            selected_date_str,

                        "category":
                            edit_category,

                        "amount":
                            edit_amount,

                        "notes":
                            edit_notes
                    }


                    try:

                        response = requests.put(

                            f"{API_URL}/expenses/"
                            f"{expense_id}",

                            json=updated_expense
                        )


                        if response.status_code == 200:

                            st.success(
                                "Expense updated successfully"
                            )

                            st.session_state[
                                f"editing_{expense_id}"
                            ] = False

                            st.rerun()


                        else:

                            st.error(
                                f"Update failed: "
                                f"{response.text}"
                            )


                    except requests.exceptions.ConnectionError:

                        st.error(
                            "Could not connect to FastAPI."
                        )


    else:

        st.info(
            "No expenses found for this date."
        )



# =========================================================
# TAB 2: ANALYTICS
# =========================================================

with tab2:

    st.header("Expense Analytics")


    # =====================================================
    # Date range
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
            key="analytics_start"
        )

    with col2:

        end_date = st.date_input(
            "End Date",
            value=date.today(),
            key="analytics_end"
        )


    # =====================================================
    # Generate Analytics
    # =====================================================

    if st.button(
        "Generate Analytics",
        key="generate_analytics"
    ):

        if start_date > end_date:

            st.error(
                "Start date cannot be after end date."
            )

        else:

            analytics_data = {

                "start_date":
                    start_date.strftime("%Y-%m-%d"),

                "end_date":
                    end_date.strftime("%Y-%m-%d")
            }


            try:

                response = requests.post(
                    f"{API_URL}/analytics/",
                    json=analytics_data
                )


                if response.status_code == 200:

                    result = response.json()


                    # =================================================
                    # Total Expense
                    # =================================================

                    total_expense = result.get(
                        "total_expense",
                        0
                    )

                    st.subheader("Summary")

                    st.metric(
                        "Total Expense",
                        f"₹{total_expense:,.2f}"
                    )


                    # =================================================
                    # Category-wise Analysis
                    # =================================================

                    category_summary = result.get(
                        "category_summary",
                        []
                    )


                    if category_summary:

                        st.subheader(
                            "Category-wise Expenses"
                        )


                        category_df = pd.DataFrame(
                            category_summary
                        )


                        # ---------------------------------------------
                        # Table
                        # ---------------------------------------------

                        st.dataframe(
                            category_df,
                            use_container_width=True,
                            hide_index=True
                        )


                        # ---------------------------------------------
                        # Bar Chart
                        # ---------------------------------------------

                        st.subheader(
                            "Expense by Category"
                        )


                        chart_df = category_df.set_index(
                            "category"
                        )


                        st.bar_chart(
                            chart_df["total"]
                        )


                        # ---------------------------------------------
                        # Pie Chart
                        # ---------------------------------------------

                        st.subheader(
                            "Expense Distribution"
                        )


                        st.plotly_chart(
                            {
                                "data": [{
                                    "labels":
                                        category_df["category"].tolist(),

                                    "values":
                                        category_df["total"].tolist(),

                                    "type":
                                        "pie"
                                }]
                            },
                            use_container_width=True
                        )


                    # =================================================
                    # Daily Analysis
                    # =================================================

                    daily_summary = result.get(
                        "daily_summary",
                        []
                    )


                    if daily_summary:

                        st.subheader(
                            "Daily Expenses"
                        )


                        daily_df = pd.DataFrame(
                            daily_summary
                        )


                        daily_df["expense_date"] = pd.to_datetime(
                            daily_df["expense_date"]
                        )


                        daily_df = daily_df.sort_values(
                            "expense_date"
                        )


                        # ---------------------------------------------
                        # Table
                        # ---------------------------------------------

                        st.dataframe(
                            daily_df,
                            use_container_width=True,
                            hide_index=True
                        )


                        # ---------------------------------------------
                        # Line Chart
                        # ---------------------------------------------

                        st.subheader(
                            "Daily Expense Trend"
                        )


                        line_df = daily_df.set_index(
                            "expense_date"
                        )


                        st.line_chart(
                            line_df["total"]
                        )


                else:

                    st.error(
                        f"Analytics failed: "
                        f"{response.text}"
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the server is running."
                )
