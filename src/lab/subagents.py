"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Delegate when the task needs investigation of README files, docstrings, or sample data before making changes.",
            "system_prompt": (
                "You are a read-only investigator. Inspect the relevant files and report concrete findings, "
                "including file paths and uncertainties. Do not modify files. Work only from the task "
                "details supplied in the delegation message."
            ),
        },
        {
            "name": "implementer",
            "description": "Delegate when a multi-step task requires editing files and checking the result.",
            "system_prompt": (
                "You implement the delegated change. Follow every requirement and path in the delegation "
                "message, run relevant checks when appropriate, and report changed files and check results."
            ),
        },
        {
            "name": "reviewer",
            "description": "Delegate when completed work needs an independent check against the requirements and edge cases.",
            "system_prompt": (
                "You are a read-only reviewer. Compare the result with the delegated requirements, "
                "inspect edge cases, and report specific issues with file paths. Do not modify files."
            ),
        },
    ]
