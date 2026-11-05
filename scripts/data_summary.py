"""数据汇总脚本占位文件。

用于对收集的数据做汇总、分组和摘要展示。
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Any


def summarize_records(records: Iterable[Mapping[str, Any]], group_by: str) -> dict[str, int]:
    """按指定字段汇总记录数量。"""
    summary: dict[str, int] = defaultdict(int)
    for record in records:
        key = record.get(group_by, "unknown")
        summary[str(key)] += 1
    return dict(summary)


def build_summary_report(records: Iterable[Mapping[str, Any]], group_by: str) -> dict[str, Any]:
    """生成结构化汇总报告。"""
    grouped = summarize_records(records, group_by)
    return {
        "group_by": group_by,
        "total_records": sum(grouped.values()),
        "distribution": grouped,
        "summary": "按字段 {} 汇总完成，当前共有 {} 条记录。".format(group_by, sum(grouped.values())),
    }


if __name__ == "__main__":
    sample_records = [
        {"status": "active", "region": "东区"},
        {"status": "active", "region": "南区"},
        {"status": "pending", "region": "东区"},
    ]
    print(build_summary_report(sample_records, "status"))
