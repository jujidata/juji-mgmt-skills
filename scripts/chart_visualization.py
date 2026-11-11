"""将据吉企业角色汇总或项目统计响应绘制为柱状图。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


def build_enterprise_user_chart_data(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """把 /enterprise/users/summary 响应转换为角色人数图表数据。"""
    by_role = payload.get("by_role")
    if not isinstance(by_role, Mapping):
        raise ValueError("by_role 必须是对象")
    data: list[dict[str, Any]] = []
    for role, count in sorted(by_role.items(), key=lambda item: str(item[0])):
        if not isinstance(role, str) or not role:
            raise ValueError("角色名必须是非空字符串")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"角色 {role} 的人数必须是非负整数")
        data.append({"label": role, "value": count})
    return data


def build_project_statistics_chart_data(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """把 /projects/{projectId}/statistics 响应转换为指标图表数据。"""
    fields = (
        ("任务总数", "total_tasks"),
        ("已完成", "completed_tasks"),
        ("待审核", "pending_review_tasks"),
        ("已有标注", "tasks_with_annotations"),
        ("跳过标注", "skipped_annotations"),
    )
    data: list[dict[str, Any]] = []
    for label, field in fields:
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field} 必须是非负整数")
        data.append({"label": label, "value": value})
    return data


def save_bar_chart(
    chart_data: list[dict[str, Any]], output_path: str, title: str
) -> str:
    """保存柱状图并返回输出路径。"""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("请安装 matplotlib 以支持绘图功能") from exc

    labels = [str(row["label"]) for row in chart_data]
    values = [int(row["value"]) for row in chart_data]
    figure, axes = plt.subplots()
    axes.bar(labels, values)
    axes.set_title(title)
    axes.set_ylabel("数量")
    axes.tick_params(axis="x", labelrotation=25)
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)
    return output_path


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
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--title", help="图表标题")
    args = parser.parse_args()

    payload = _load_json(args.input)
    if args.kind == "enterprise-users":
        data = build_enterprise_user_chart_data(payload)
        default_title = "企业成员角色分布"
    else:
        data = build_project_statistics_chart_data(payload)
        default_title = "项目任务统计"
    print(save_bar_chart(data, args.output, args.title or default_title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
