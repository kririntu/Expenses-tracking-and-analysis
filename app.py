from fastapi import FastAPI
from pydantic import BaseModel
from logger import setup_logger

from crud import (
    fetch_expenses_for_date,
    insert_expense,
    update_expense,
    delete_expense,
    get_expense_analytics
)


app = FastAPI()

logger = setup_logger("logger")


# =========================================================
# Expense model
# =========================================================

class Expense(BaseModel):

    expense_date: str
    category: str
    amount: float
    notes: str = ""


# =========================================================
# Analytics model
# =========================================================

class AnalyticsRequest(BaseModel):

    start_date: str
    end_date: str


# =========================================================
# GET expenses for a particular date
# =========================================================

@app.get("/expenses/{expense_date}")
def get_expenses(expense_date: str):

    logger.info(
        f"GET request for expenses on {expense_date}"
    )

    return fetch_expenses_for_date(expense_date)


# =========================================================
# ADD new expense
# =========================================================

@app.post("/expenses")
def add_expense(expense: Expense):

    logger.info(
        f"POST request to add expense: {expense}"
    )

    insert_expense(
        expense.model_dump()
    )

    return {
        "message": "Expense added successfully"
    }


# =========================================================
# UPDATE existing expense
# =========================================================

@app.put("/expenses/{expense_id}")
def edit_expense(
    expense_id: int,
    expense: Expense
):

    logger.info(
        f"PUT request to update expense {expense_id}: {expense}"
    )

    expense_data = expense.model_dump()

    expense_data["id"] = expense_id

    update_expense(expense_data)

    return {
        "message": "Expense updated successfully"
    }


# =========================================================
# DELETE expense
# =========================================================

@app.delete("/expenses/{expense_id}")
def remove_expense(expense_id: int):

    logger.info(
        f"DELETE request for expense {expense_id}"
    )

    delete_expense(expense_id)

    return {
        "message": "Expense deleted successfully"
    }


# =========================================================
# ANALYTICS
# =========================================================

@app.post("/analytics/")
def analytics(data: AnalyticsRequest):

    logger.info(
        f"Analytics request from {data.start_date} "
        f"to {data.end_date}"
    )

    result = get_expense_analytics(
        data.start_date,
        data.end_date
    )

    return result
