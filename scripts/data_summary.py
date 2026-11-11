"""将据吉只读开放 API 响应转换为结构化中文摘要。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


def _non_negative_int(payload: Mapping[str, Any], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} 必须是非负整数")
    return value


def summarize_enterprise_users(payload: Mapping[str, Any]) -> dict[str, Any]:
    """汇总 /enterprise/users/summary 响应。"""
    total_count = _non_negative_int(payload, "total_count")
    by_role_raw = payload.get("by_role")
    if not isinstance(by_role_raw, Mapping):
        raise ValueError("by_role 必须是对象")

    by_role: dict[str, int] = {}
    distribution: list[dict[str, Any]] = []
    for role, raw_count in sorted(by_role_raw.items(), key=lambda item: str(item[0])):
        if not isinstance(role, str) or not role:
            raise ValueError("by_role 的角色名必须是非空字符串")
        if isinstance(raw_count, bool) or not isinstance(raw_count, int) or raw_count < 0:
            raise ValueError(f"角色 {role} 的人数必须是非负整数")
        by_role[role] = raw_count
        distribution.append(
            {
                "role": role,
                "count": raw_count,
                "percentage": round(raw_count / total_count * 100, 2)
                if total_count
                else 0.0,
            }
        )

    counted_total = sum(by_role.values())
    return {
        "total_count": total_count,
        "counted_total": counted_total,
        "distribution": distribution,
        "summary": f"企业共有 {total_count} 名成员，服务端返回 {len(by_role)} 个角色分组。",
        "count_matches_total": counted_total == total_count,
    }


def summarize_project_statistics(payload: Mapping[str, Any]) -> dict[str, Any]:
    """汇总 /projects/{projectId}/statistics 响应。"""
    project_id = _non_negative_int(payload, "project_id")
    total_tasks = _non_negative_int(payload, "total_tasks")
    completed_tasks = _non_negative_int(payload, "completed_tasks")
    pending_review_tasks = _non_negative_int(payload, "pending_review_tasks")
    tasks_with_annotations = _non_negative_int(payload, "tasks_with_annotations")
    skipped_annotations = _non_negative_int(payload, "skipped_annotations")

    completion_rate = payload.get("completion_rate")
    if isinstance(completion_rate, bool) or not isinstance(completion_rate, (int, float)):
        raise ValueError("completion_rate 必须是 0 到 1 之间的数字")
    if not 0 <= float(completion_rate) <= 1:
        raise ValueError("completion_rate 必须是 0 到 1 之间的数字")

    completion_percentage = round(float(completion_rate) * 100, 2)
    return {
        "project_id": project_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_review_tasks": pending_review_tasks,
        "tasks_with_annotations": tasks_with_annotations,
        "skipped_annotations": skipped_annotations,
        "completion_rate": float(completion_rate),
        "completion_percentage": completion_percentage,
        "summary": (
            f"项目 {project_id} 共 {total_tasks} 个任务，已完成 {completed_tasks} 个，"
            f"完成率 {completion_percentage:.2f}%，待审核 {pending_review_tasks} 个。"
        ),
    }


def _load_json(path: str) -> Mapping[str, Any]:
    if path == "-":
        payload = json.load(sys.stdin)
    else:
        with Path(path).open("r", encoding="utf-8") as file:
            payload = json.load(file)
    if not isinstance(payload, Mapping):
        raise ValueError("输入 JSON 必须是对象")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        required=True,
        choices=("enterprise-users", "project-statistics"),
        help="API 响应类型",
    )
    parser.add_argument("--input", default="-", help="JSON 文件路径；默认从标准输入读取")
    args = parser.parse_args()

    payload = _load_json(args.input)
    if args.kind == "enterprise-users":
        result = summarize_enterprise_users(payload)
    else:
        result = summarize_project_statistics(payload)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
