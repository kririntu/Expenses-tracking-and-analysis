from contextlib import contextmanager
from logger import setup_logger
import mysql.connector


logger = setup_logger('logger')


def create_database():
    connection = mysql.connector.connect(
        host='localhost',
        user='krishnendu',
        password='test123'
    )

    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")

    cursor.close()
    connection.close()


def create_table():
    create_database()

    connection = mysql.connector.connect(
        host='localhost',
        user='krishnendu',
        password='test123',
        database='mydatabase'
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT PRIMARY KEY AUTO_INCREMENT,
            expense_date DATE,
            amount FLOAT,
            category VARCHAR(255),
            notes TEXT
        )
    """)

    cursor.close()
    connection.close()


@contextmanager
def get_db_cursor(commit=False):

    create_table()

    connection = mysql.connector.connect(
        host='localhost',
        user='krishnendu',
        password='test123',
        database='mydatabase'
    )

    cursor = connection.cursor(dictionary=True)

    try:
        yield cursor

        if commit:
            connection.commit()

    finally:
        cursor.close()
        connection.close()


def fetch_expenses_for_date(expense_date):

    logger.info(f"fetch_expenses_for_date called with {expense_date}")

    with get_db_cursor() as cursor:

        cursor.execute(
            "SELECT * FROM expenses WHERE expense_date = %s",
            (expense_date,)
        )

        expenses = cursor.fetchall()

        return expenses


def insert_expense(expense):

    logger.info(f"insert_expense called with {expense}")

    with get_db_cursor(commit=True) as cursor:

        cursor.execute(
            """
            INSERT INTO expenses
            (expense_date, category, amount, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (
                expense['expense_date'],
                expense['category'],
                expense['amount'],
                expense['notes']
            )
        )


def update_expense(expense):

    logger.info(f"update_expense called with {expense['id']}")

    with get_db_cursor(commit=True) as cursor:

        cursor.execute(
            """
            UPDATE expenses
            SET expense_date = %s,
                category = %s,
                amount = %s,
                notes = %s
            WHERE id = %s
            """,
            (
                expense['expense_date'],
                expense['category'],
                expense['amount'],
                expense['notes'],
                expense['id']
            )
        )


def delete_expense(expense_id):

    logger.info(f"delete_expense called with {expense_id}")

    with get_db_cursor(commit=True) as cursor:

        cursor.execute(
            "DELETE FROM expenses WHERE id = %s",
            (expense_id,)
        )


def get_expense_analytics(start_date, end_date):

    logger.info(
        f"get_expense_analytics called from {start_date} to {end_date}"
    )

    with get_db_cursor() as cursor:

        # -----------------------------------------
        # Overall summary
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_expense,
                COALESCE(AVG(amount), 0) AS average_expense,
                COUNT(*) AS transaction_count,
                COALESCE(MAX(amount), 0) AS highest_expense
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            """,
            (start_date, end_date)
        )

        summary = cursor.fetchone()


        # -----------------------------------------
        # Category-wise expense
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                category,
                SUM(amount) AS total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date)
        )

        category_summary = cursor.fetchall()


        # -----------------------------------------
        # Daily expense
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                expense_date,
                SUM(amount) AS total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY expense_date
            ORDER BY expense_date
            """,
            (start_date, end_date)
        )

        daily_summary = cursor.fetchall()


        # -----------------------------------------
        # Monthly expense
        # -----------------------------------------

        cursor.execute(
            """
            SELECT
                DATE_FORMAT(expense_date, '%Y-%m') AS month,
                SUM(amount) AS total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(expense_date, '%Y-%m')
            ORDER BY month
            """,
            (start_date, end_date)
        )

        monthly_summary = cursor.fetchall()


        # -----------------------------------------
        # Most expensive category
        # -----------------------------------------

        top_category = None

        if category_summary:
            top_category = category_summary[0]["category"]


        # -----------------------------------------
        # Return everything
        # -----------------------------------------

        return {
            "summary": summary,
            "top_category": top_category,
            "category_summary": category_summary,
            "daily_summary": daily_summary,
            "monthly_summary": monthly_summary
        }
