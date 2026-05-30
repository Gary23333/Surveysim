"""任务结果导出：JSON / CSV"""

import csv
import json
import io
from typing import Any, Dict, List


class ResultExporter:
    """结果导出器"""

    @staticmethod
    def to_json(results: Dict[str, Any]) -> str:
        return json.dumps(results, ensure_ascii=False, indent=2)

    @staticmethod
    def to_json_dict(results: Dict[str, Any]) -> Dict[str, Any]:
        return results

    @staticmethod
    def to_csv(results: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["题号", "问题", "Agent", "回答", "评分", "情绪", "情绪强度", "时间戳", "类型"])

        for qr in results.get("question_results", []):
            q_idx = qr.get("question_id", "")
            q_text = qr.get("question_text", "")

            for resp in qr.get("responses", []):
                score_str = str(resp.get("score", "")) if resp.get("score") is not None else ""
                writer.writerow([
                    q_idx, q_text, resp.get("agent_name", ""),
                    resp.get("content", ""), score_str,
                    resp.get("emotion", ""), resp.get("emotion_intensity", ""),
                    resp.get("timestamp", ""), "回答",
                ])

            for fu in qr.get("follow_ups", []):
                fu_resp = fu.get("response") or {}
                writer.writerow([
                    q_idx,
                    f"[追问] {fu.get('question', '')}",
                    fu_resp.get("agent_name", ""),
                    "",
                    fu_resp.get("content", ""),
                    fu_resp.get("emotion", ""),
                    "",
                    "",
                    f"追问(深度{fu.get('depth', 1)})",
                ])

        return output.getvalue()

    @staticmethod
    def to_csv_stream(results: Dict[str, Any]) -> io.StringIO:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["题号", "问题", "Agent名称", "回答内容", "情绪", "情绪强度", "时间戳", "问题类型"])

        for qr in results.get("question_results", []):
            q_id = qr.get("question_id", "")
            q_text = qr.get("question_text", "")
            for resp in qr.get("responses", []):
                writer.writerow([
                    q_id, q_text, resp.get("agent_name", ""),
                    resp.get("content", ""), resp.get("emotion", ""),
                    resp.get("emotion_intensity", ""), resp.get("timestamp", ""), "回答",
                ])

        return output
