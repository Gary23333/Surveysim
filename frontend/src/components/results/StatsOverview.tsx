import type { TaskResult } from "@/types";

interface Props {
  results: TaskResult;
}

const emotionLabels: Record<string, string> = {
  happy: "😊 开心", sad: "😢 难过", angry: "😠 生气", surprised: "😲 惊讶",
  neutral: "😐 中立", thinking: "🤔 思考", confused: "😕 困惑", excited: "🤩 兴奋",
  worried: "😟 担忧", curious: "🧐 好奇", satisfied: "😌 满意", dissatisfied: "😒 不满",
};

export default function StatsOverview({ results }: Props) {
  const cards = [
    { label: "总题数", value: results.total_questions, color: "bg-blue-50 text-blue-700" },
    { label: "总回答", value: results.total_responses, color: "bg-green-50 text-green-700" },
    { label: "追问数", value: results.total_follow_ups, color: "bg-amber-50 text-amber-700" },
    { label: "平均回答长度", value: `${Math.round(results.avg_response_length)}字`, color: "bg-purple-50 text-purple-700" },
  ];

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {cards.map((c) => (
        <div key={c.label} className={`rounded-xl p-4 ${c.color}`}>
          <div className="text-sm opacity-70">{c.label}</div>
          <div className="text-2xl font-bold mt-1">{c.value}</div>
        </div>
      ))}
    </div>
  );
}

export function EmotionChart({ distribution }: { distribution: Record<string, number> }) {
  const entries = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
  const colors: Record<string, string> = {
    happy: "bg-emerald-400", sad: "bg-blue-400", angry: "bg-red-400",
    surprised: "bg-amber-400", neutral: "bg-gray-400", thinking: "bg-indigo-400",
    confused: "bg-orange-400", excited: "bg-pink-400", worried: "bg-violet-400",
    curious: "bg-teal-400", satisfied: "bg-green-400", dissatisfied: "bg-rose-400",
  };

  if (entries.length === 0) return null;

  return (
    <div className="space-y-2 mb-6">
      <h3 className="font-semibold text-sm text-gray-600 mb-3">情绪分布</h3>
      {entries.map(([emotion, pct]) => (
        <div key={emotion} className="flex items-center gap-3">
          <span className="w-20 text-xs text-gray-600 shrink-0">{emotionLabels[emotion] || emotion}</span>
          <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${colors[emotion] || "bg-gray-400"}`}
              style={{ width: `${Math.round(pct * 100)}%` }}
            />
          </div>
          <span className="text-xs text-gray-500 w-10 text-right">{Math.round(pct * 100)}%</span>
        </div>
      ))}
    </div>
  );
}

export function ScaleScorePanel({ question_results }: { question_results: any[] }) {
  const scored = question_results.filter((qr: any) => qr.responses.some((r: any) => r.score != null));
  if (scored.length === 0) return null;

  return (
    <div className="space-y-3 mb-6">
      <h3 className="font-semibold text-sm text-gray-600">评分一览</h3>
      {scored.map((qr: any) => {
        const scores = qr.responses.filter((r: any) => r.score != null).map((r: any) => r.score);
        const avg = scores.reduce((a: number, b: number) => a + b, 0) / scores.length;
        return (
          <div key={qr.question_id} className="flex items-center gap-3">
            <span className="w-32 text-xs text-gray-600 truncate shrink-0">{qr.question_text.slice(0, 12)}</span>
            <div className="flex-1 bg-gray-100 rounded-full h-5 relative overflow-visible">
              <div className="absolute inset-0 bg-gradient-to-r from-red-300 via-amber-300 to-emerald-400 rounded-full" style={{
                width: `${(avg / 10) * 100}%`,
                opacity: 0.3,
              }} />
              <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 flex justify-between px-1">
                {scores.map((s: number, i: number) => (
                  <div key={i} className="w-2.5 h-2.5 rounded-full bg-blue-600 border border-white shadow-sm"
                    style={{ marginLeft: `${((s - 1) / 9) * 100}%`, position: 'absolute', left: `${((s - 1) / 9) * 100}%` }} />
                ))}
              </div>
            </div>
            <span className="text-xs font-medium w-8 text-right">{avg.toFixed(1)}</span>
          </div>
        );
      })}
    </div>
  );
}

export function SurveyFeedbackPanel({ feedback }: { feedback: any[] }) {
  if (!feedback || feedback.length === 0) return null;

  const dims = [
    { key: "length_rating", label: "问卷长度", desc: "↓越低越好（适中）" },
    { key: "difficulty_rating", label: "回答难度", desc: "↓越低越好" },
    { key: "clarity_rating", label: "问题清晰度", desc: "↑越高越好" },
    { key: "fatigue_rating", label: "疲劳感受", desc: "↓越低越好" },
    { key: "interest_rating", label: "兴趣程度", desc: "↑越高越好" },
  ];

  return (
    <div className="space-y-3 mb-6">
      <h3 className="font-semibold text-sm text-gray-600 mb-3">问卷体验反馈</h3>
      {dims.map((dim) => {
        const values = feedback.map((f: any) => f[dim.key] || 5);
        const avg = values.reduce((a: number, b: number) => a + b, 0) / values.length;
        const isPositive = ["clarity_rating", "interest_rating"].includes(dim.key);
        const color = isPositive ? "from-red-300 via-amber-300 to-emerald-400" : "from-emerald-400 via-amber-300 to-red-300";
        return (
          <div key={dim.key}>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-gray-600 w-20">{dim.label}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-4 relative">
                <div className={`absolute inset-0 bg-gradient-to-r ${color} rounded-full opacity-30`} />
                {feedback.map((f: any, i: number) => {
                  const pct = ((f[dim.key] - 1) / 9) * 100;
                  return (
                    <div key={i} className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-600 border border-white"
                      style={{ left: `${pct}%` }} title={`${f.agent_name}: ${f[dim.key]}`} />
                  );
                })}
              </div>
              <span className="text-xs font-medium w-8 text-right">{avg.toFixed(1)}</span>
              <span className="text-xs text-gray-400 w-24">{dim.desc}</span>
            </div>
            <div className="flex gap-3 ml-20 text-xs text-gray-400">
              {feedback.map((f: any, i: number) => (
                <span key={i}>{f.agent_name}:{f[dim.key]}</span>
              ))}
            </div>
          </div>
        );
      })}
      <div className="border rounded-lg p-3 bg-gray-50 max-h-40 overflow-y-auto">
        <h4 className="text-xs font-medium text-gray-500 mb-1">评语</h4>
        {feedback.map((f: any, i: number) => (
          <div key={i} className="text-xs text-gray-600 mb-1">
            <span className="font-medium">{f.agent_name}：</span>{f.comment}
          </div>
        ))}
      </div>
    </div>
  );
}
