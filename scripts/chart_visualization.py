"""可视化脚本占位文件。

用于根据业务数据输出柱状图、折线图等图表。实际接入时可替换为真实数据源。
"""

from __future__ import annotations

from typing import Iterable, Mapping, Any


def build_chart_data(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """将原始记录转换为图表所需的结构化数据。"""
    data = []
    for item in records:
        data.append({
            "label": item.get("label", "未命名"),
            "value": item.get("value", 0),
        })
    return data


def save_bar_chart(chart_data: list[dict[str, Any]], output_path: str, title: str = "数据概览") -> str:
    """保存柱状图；在真实环境里可接入 matplotlib 等库。"""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("请安装 matplotlib 以支持绘图功能。") from exc

    labels = [row["label"] for row in chart_data]
    values = [row["value"] for row in chart_data]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel("数量")
    fig.tight_layout()
    fig.savefig(output_path)
    return output_path


if __name__ == "__main__":
    sample_data = [
        {"label": "已完成", "value": 20},
        {"label": "进行中", "value": 12},
        {"label": "待处理", "value": 8},
    ]
    print(save_bar_chart(sample_data, "output_chart.png", title="示例进度图"))
