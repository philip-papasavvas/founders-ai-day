"""Simple PDF export for the weekly household meal plan."""

from __future__ import annotations

import textwrap

from meal_planning.catalog import get_meal_details
from meal_planning.planner import (
    DailyMealPlan,
    MealPlannerPreferences,
    WeeklyMealPlan,
    shopping_list_rows,
    unique_meals_from_plan,
)

PDF_WIDTH = 612
PDF_HEIGHT = 792
LINES_PER_PAGE = 48
WRAP_WIDTH = 88


def _escape_pdf_text(text: str) -> str:
    """Escape raw text for a PDF text stream."""

    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _page_stream(lines: list[str]) -> bytes:
    """Render a list of lines into a single PDF content stream."""

    stream_lines = ["BT", "/F1 10 Tf", "48 760 Td", "13 TL"]
    for line in lines:
        stream_lines.append(f"({_escape_pdf_text(line)}) Tj")
        stream_lines.append("T*")
    stream_lines.append("ET")
    return "\n".join(stream_lines).encode("latin-1", errors="replace")


def _build_pdf_document(pages: list[list[str]]) -> bytes:
    """Build a minimal multi-page PDF from text pages."""

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    page_object_numbers = [4 + index * 2 for index in range(len(pages))]
    content_object_numbers = [number + 1 for number in page_object_numbers]
    page_refs = " ".join(f"{number} 0 R" for number in page_object_numbers)
    objects.append(f"<< /Type /Pages /Count {len(pages)} /Kids [{page_refs}] >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page_number, content_number, page_lines in zip(
        page_object_numbers, content_object_numbers, pages, strict=False
    ):
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PDF_WIDTH} {PDF_HEIGHT}] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_number} 0 R >>"
            ).encode()
        )
        content_stream = _page_stream(page_lines)
        objects.append(
            b"<< /Length "
            + str(len(content_stream)).encode()
            + b" >>\nstream\n"
            + content_stream
            + b"\nendstream"
        )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, object_body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode())
        pdf.extend(object_body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode()
    )
    return bytes(pdf)


def build_weekly_plan_pdf(
    plan: WeeklyMealPlan,
    preferences: MealPlannerPreferences,
    daily_schedule: tuple[DailyMealPlan, ...],
) -> bytes:
    """Export the current weekly plan as a compact PDF summary."""

    lines: list[str] = [
        "Mitchell family meal plan",
        "",
        (
            f"Budget GBP {preferences.weekly_budget_gbp:.0f} | Office days {preferences.office_days} "
            f"| Hosted dinners {preferences.hosted_dinners}"
        ),
        f"Estimated spend GBP {plan.estimated_cost_gbp:.2f} | {plan.budget_status}",
        "",
        "Weekly schedule",
    ]

    for day in daily_schedule:
        lines.append(
            (
                f"{day.day}: breakfast {day.breakfast.meal.name}; "
                f"lunch {day.lunch.meal.name} ({day.lunch.servings} portions); "
                f"dinner {day.dinner.meal.name} ({day.dinner.servings} servings)"
            )
        )

    lines.extend(["", "Shopping list"])
    for row in shopping_list_rows(plan):
        lines.append(f"{row['Category']}: {row['Item']} - {row['Quantity']}")

    lines.extend(["", "Recipe summaries"])
    for meal in unique_meals_from_plan(plan):
        details = get_meal_details(meal.key)
        lines.append("")
        lines.append(meal.name)
        for step in details.method_summary:
            lines.append(f"- {step}")

    wrapped_lines: list[str] = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=WRAP_WIDTH) or [""])

    pages = [
        wrapped_lines[index : index + LINES_PER_PAGE]
        for index in range(0, len(wrapped_lines), LINES_PER_PAGE)
    ]
    return _build_pdf_document(pages)
