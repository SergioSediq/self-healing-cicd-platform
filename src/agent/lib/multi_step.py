"""Multi-step fixes: handle changes across multiple files. Stub for future expansion."""
from typing import List


def plan_multi_file_fix(analysis_results: List[dict]) -> List[dict]:
    """
    Stub: Given N analyses, return ordered list of (file, action).
    Future: dependency graph, topological sort.
    """
    return [{"file": a.get("file_path"), "action": "modify"} for a in analysis_results]
