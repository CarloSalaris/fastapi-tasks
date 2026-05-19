from typing import Literal

from pydantic import BaseModel

from app.models import Task

# Query parameters for filtering and sorting.
#
# How to add a new filter:
# 1. Add the field with type | None = None
# 2. Add the field name to `filter_fields` in the apply() method
# 3. The field name must match a column name in the model


class TaskFilters(BaseModel):
    # --- Filters (must match Task column names) ---
    project_id: int | None = None
    user_id: int | None = None  # Filtro pensato per utente admin
    completed: bool | None = None

    # --- Sorting ---
    sort: Literal[
        "created_at",
        "updated_at",
        "due_date",
        "title",
        "completed",
        "project_id",
        "user_id",
    ] = "created_at"
    order: Literal["asc", "desc"] = "desc"

    # --- Pagination ---
    skip: int = 0
    limit: int = 20

    def apply(self, query):
        # Fields that map 1:1 to Task columns.
        # Add new filter field names here — no router changes needed.
        filter_fields = {"completed", "project_id", "user_id"}

        for field_name in filter_fields:
            value = getattr(self, field_name)
            if value is not None:
                query = query.where(getattr(Task, field_name) == value)

        sort_column = getattr(Task, self.sort)
        query = query.order_by(
            sort_column.desc() if self.order == "desc" else sort_column.asc()
        )

        return query.offset(self.skip).limit(self.limit)
