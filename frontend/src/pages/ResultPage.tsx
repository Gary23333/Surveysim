import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useTaskStore } from "@/stores/taskStore";
import { tasksApi } from "@/api/tasks";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, Sparkles } from "lucide-react";
import StatsOverview, { EmotionChart, ScaleScorePanel, SurveyFeedbackPanel } from "@/components/results/StatsOverview";
import QuestionResultCard from "@/components/results/QuestionResultCard";

const scenarioLabels: Record<string, string> = {
  survey: "问卷调查", focus_group: "焦点小组", idi: "深度访谈", debate: "辩论讨论",
};
const scenarioEmojis: Record<string, string> = {
  survey: "📋", focus_group: "👥", idi: "🎙️", debate: "⚔️",
};

export default function ResultPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const { results, currentTask, loading, fetchTask, fetchResults } = useTaskStore();
  const [summarizing, setSummarizing] = useState(false);

  useEffect(() => {
    if (taskId) { fetchTask(taskId); fetchResults(taskId); }
  }, [taskId]);

  const handleExport = async (format: string) => {
    if (!taskId) return;
    try {
      if (format === "csv") {
        const blob = await tasksApi.exportResults(taskId, "csv");
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = `results_${taskId.slice(0, 8)}.csv`; a.click();
        URL.revokeObjectURL(url);
      } else {
        const data = await tasksApi.exportResults(taskId, "json");
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = `results_${taskId.slice(0, 8)}.json`; a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) { console.error("Export failed:", error); }
  };

  const handleGenerateSummaries = async () => {
    if (!taskId || summarizing) return;
    setSummarizing(true);
    try {
      const result = await tasksApi.generateSummaries(taskId);
      if (result.summaries) {
        useTaskStore.getState().applySummaries(result.summaries);
      }
    } catch (error) {
      console.error("Failed to generate summaries:", error);
    } finally {
      setSummarizing(false);
    }
  };

  const r = results;

  return (
    <div className="container mx-auto max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Link to="/tasks" className="text-gray-400 hover:text-gray-600"><ArrowLeft className="w-5 h-5" /></Link>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {currentTask?.name || "结果查看"}
          </h2>
          <p className="text-gray-500 text-sm mt-1">
            {r && <>{scenarioEmojis[r.scenario_type]} {scenarioLabels[r.scenario_type] || r.scenario_type} · {r.total_responses} 条回答 · <Badge variant="outline" className="text-xs bg-green-50 text-green-700">已完成</Badge></>}
          </p>
        </div>
        <div className="flex-1" />
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => handleExport("json")}>
            <Download className="w-3 h-3 mr-1" />导出 JSON
          </Button>
          <Button size="sm" variant="outline" onClick={() => handleExport("csv")}>
            <Download className="w-3 h-3 mr-1" />导出 CSV
          </Button>
        </div>
      </div>

      {loading || !r ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
          <p className="text-gray-500 mt-4">加载结果中...</p>
        </div>
      ) : (
        <>
          {/* Stats overview */}
          <StatsOverview results={r} />

          {/* Participant agents list */}
          {r.agents && r.agents.length > 0 && (
            <Card className="mb-6">
              <CardContent className="p-6">
                <h3 className="font-semibold text-sm text-gray-600 mb-3">参与者配置</h3>
                <div className="grid grid-cols-2 gap-3">
                  {r.agents.map((a) => (
                    <div key={a.agent_id} className="border rounded-lg p-3 bg-gray-50/50">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600">
                          {a.agent_name?.charAt(0)}
                        </div>
                        <div>
                          <span className="font-medium text-sm">{a.agent_name}</span>
                          <span className="text-xs text-gray-500 ml-2">{a.occupation}</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 mt-2 text-xs text-gray-500">
                        <span>人格：<span className="text-gray-700 font-medium">{a.persona_name}</span></span>
                        <span>行为：<span className="text-gray-700 font-medium">{a.behavior_prompt_id}</span></span>
                        <span>LLM：<span className="text-gray-700 font-medium">{a.provider_pack}</span></span>
                        <span>模型：<span className="text-gray-700 font-medium">{a.model}</span></span>
                      </div>
                      {a.thinking_enabled && (
                        <Badge variant="outline" className="text-xs mt-1 bg-purple-50 text-purple-700">
                          思考模式: {a.thinking_intensity}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Emotion chart */}
          {Object.keys(r.emotion_distribution || {}).length > 0 && (
            <Card className="mb-6">
              <CardContent className="p-6">
                <EmotionChart distribution={r.emotion_distribution} />
              </CardContent>
            </Card>
          )}

          {/* Scale Score Panel */}
          <ScaleScorePanel question_results={r.question_results} />

          {/* Survey Feedback */}
          <SurveyFeedbackPanel feedback={r.survey_feedback} />

          {/* AI Summary */}
          {r.summary && (
            <Card className="mb-6">
              <CardContent className="p-6">
                <h3 className="font-semibold text-sm text-gray-600 mb-2">AI 主持总结</h3>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{r.summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Question results */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-sm text-gray-600">
                逐题结果（{r.question_results?.length || 0} 题）
              </h3>
              <Button size="sm" variant="outline" onClick={handleGenerateSummaries} disabled={summarizing}>
                <Sparkles className="w-3 h-3 mr-1" />
                {summarizing ? "分析中..." : "AI 分析每题"}
              </Button>
            </div>
            <div className="space-y-3">
              {r.question_results?.map((qr, i) => (
                <QuestionResultCard key={qr.question_id} qr={qr} index={i} />
              ))}
            </div>
          </div>

          {/* Timeline summary */}
          <Card className="mt-6">
            <CardContent className="p-6">
              <h3 className="font-semibold text-sm text-gray-600 mb-3">回答时间线</h3>
              <div className="space-y-2">
                {r.question_results?.flatMap(qr =>
                  qr.responses.map(resp => ({ ...resp, question: qr.question_text }))
                ).sort((a, b) => a.timestamp?.localeCompare(b.timestamp || "") || 0).slice(0, 20).map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-16 shrink-0">{item.timestamp?.slice(11, 19) || ""}</span>
                    <span className="font-medium text-gray-700">{item.agent_name}</span>
                    <span>回答了「{item.question?.slice(0, 20)}...」</span>
                    <span className="ml-auto">{item.emotion}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
