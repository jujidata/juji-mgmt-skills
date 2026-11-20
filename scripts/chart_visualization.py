"""将据吉企业角色、项目进度或项目工作统计绘制为图表。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping


WORK_METRICS = {
    "annotated": "标注",
    "reviewed": "审核",
    "returned": "打回",
    "collected": "采集",
}


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


def _get_pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("请安装 matplotlib 以支持绘图功能") from exc
    return plt


def save_bar_chart(
    chart_data: list[dict[str, Any]], output_path: str, title: str
) -> str:
    """保存柱状图并返回输出路径。"""
    plt = _get_pyplot()

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


def build_project_work_chart_data(
    payload: Mapping[str, Any],
) -> tuple[dict[str, dict[str, int]], set[int]]:
    """从同一日期范围的员工响应汇总所选项目，并记录实际覆盖的项目。"""
    date_range = payload["range"]
    start = date.fromisoformat(date_range["start_date"])
    end = date.fromisoformat(date_range["end_date"])
    day_count = (end - start).days + 1
    if date_range["timezone"] != "Asia/Shanghai" or not 1 <= day_count <= 31:
        raise ValueError("日期范围必须为 1 至 31 个上海自然日")

    project_ids = set(payload["project_ids"])
    daily_counts = {
        (start + timedelta(days=offset)).isoformat(): dict.fromkeys(WORK_METRICS, 0)
        for offset in range(day_count)
    }
    employee_ids: set[int] = set()
    covered_projects: set[int] = set()
    for employee in payload["employees"]:
        employee_id = employee["employee_id"]
        if employee_id in employee_ids:
            raise ValueError(f"员工 {employee_id} 的响应重复")
        employee_ids.add(employee_id)
        if employee["range"] != date_range:
            raise ValueError(f"员工 {employee_id} 的统计区间不一致")

        days = employee["daily"]
        if len(days) != day_count or {day["date"] for day in days} != daily_counts.keys():
            raise ValueError(f"员工 {employee_id} 的每日统计不完整或重复")
        for day in days:
            seen_projects: set[int] = set()
            for project in day["projects"]:
                project_id = project["project_id"]
                if project_id not in project_ids:
                    continue
                if project_id in seen_projects:
                    raise ValueError(f"员工 {employee_id} 在 {day['date']} 的项目 {project_id} 重复")
                seen_projects.add(project_id)
                covered_projects.add(project_id)
                for metric in WORK_METRICS:
                    count = project[metric]
                    if type(count) is not int or count < 0:
                        raise ValueError(f"{metric} 必须是非负整数")
                    daily_counts[day["date"]][metric] += count
    return daily_counts, covered_projects


def save_project_work_chart(
    payload: Mapping[str, Any], output_path: str, title: str, chart_type: str
) -> str:
    """按日期绘制标注、审核、打回和采集的独立序列。"""
    daily_counts, covered_projects = build_project_work_chart_data(payload)
    if not covered_projects:
        raise ValueError("所选项目没有可用的员工工作统计数据")
    failed_employee_count = payload.get("failed_employee_count", 0)
    if type(failed_employee_count) is not int or failed_employee_count < 0:
        raise ValueError("failed_employee_count 必须是非负整数")

    plt = _get_pyplot()
    from matplotlib import font_manager
    from matplotlib.ticker import MaxNLocator

    dates = list(daily_counts)
    positions = list(range(len(dates)))
    tick_step = (len(dates) + 11) // 12
    ticks = sorted({*positions[::tick_step], positions[-1]})
    project_count = len(set(payload["project_ids"]))
    subtitle = (
        f"{dates[0]} 至 {dates[-1]}（上海）  |  所管理员工"
        f"  |  覆盖 {len(covered_projects)}/{project_count} 个项目"
    )
    if failed_employee_count:
        subtitle += f"  |  {failed_employee_count} 名员工查询失败"

    preferred_fonts = (
        "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei", "Droid Sans Fallback"
    )
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    chinese_fonts = [
        font for font in preferred_fonts if font in available_fonts
    ]
    font_options = {"font.family": [*chinese_fonts, *plt.rcParams["font.family"]]}
    with plt.rc_context(font_options):
        figure, axes = plt.subplots(figsize=(10.5, 5.2), layout="constrained")
        try:
            bar_width = 0.8 / len(WORK_METRICS)
            line_styles = ("-", "--", ":", "-.")
            for index, (metric, label) in enumerate(WORK_METRICS.items()):
                values = [counts[metric] for counts in daily_counts.values()]
                if chart_type == "line":
                    axes.plot(
                        positions, values, linestyle=line_styles[index], marker="o",
                        markersize=4, label=label,
                    )
                else:
                    offset = (index - (len(WORK_METRICS) - 1) / 2) * bar_width
                    axes.bar(
                        [position + offset for position in positions], values, bar_width, label=label
                    )
            figure.suptitle(title, fontsize=16)
            axes.set_title(subtitle, fontsize=10)
            axes.set_xticks(ticks, [dates[index][5:] for index in ticks])
            axes.set_xlabel("日期（月-日）")
            axes.set_ylabel("数量")
            axes.set_ylim(bottom=0, top=max(1, axes.get_ylim()[1]))
            axes.yaxis.set_major_locator(MaxNLocator(integer=True))
            axes.grid(axis="y", alpha=0.2)
            axes.set_axisbelow(True)
            axes.legend(
                loc="upper center", bbox_to_anchor=(0.5, -0.15),
                ncol=len(WORK_METRICS), frameon=False,
            )
            figure.savefig(output_path, dpi=150)
        finally:
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
        choices=("enterprise-users", "project-statistics", "project-work-statistics"),
        help="图表数据类型",
    )
    parser.add_argument("--chart-type", choices=("bar", "line"), default="bar", help="图表类型，默认 bar")
    parser.add_argument("--input", default="-", help="JSON 文件路径；默认从标准输入读取")
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--title", help="图表标题")
    args = parser.parse_args()

    if args.chart_type == "line" and args.kind != "project-work-statistics":
        parser.error("折线图仅支持项目工作统计")
    payload = _load_json(args.input)
    if args.kind == "project-work-statistics":
        try:
            output = save_project_work_chart(
                payload, args.output, args.title or "项目工作统计", args.chart_type
            )
        except (KeyError, TypeError, ValueError, RuntimeError) as exc:
            parser.error(str(exc))
        print(output)
        return 0
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
