import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, Sparkles } from "lucide-react";
import type { QuestionResult } from "@/types";

const emotionEmojis: Record<string, string> = {
  happy: "😊", sad: "😢", angry: "😠", surprised: "😲", neutral: "😐",
  thinking: "🤔", confused: "😕", excited: "🤩", worried: "😟", curious: "🧐",
  satisfied: "😌", dissatisfied: "😒",
};

interface Props {
  qr: QuestionResult;
  index: number;
}

export default function QuestionResultCard({ qr, index }: Props) {
  const [expanded, setExpanded] = useState(index === 0);

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center gap-2 px-4 py-3 bg-gray-50 hover:bg-gray-100 text-left"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
        <span className="text-sm font-medium text-gray-700 flex-1 truncate">
          第{index + 1}题：{qr.question_text}
        </span>
        <Badge variant="secondary" className="text-xs shrink-0">{qr.responses.length}回答</Badge>
        {qr.follow_ups.length > 0 && (
          <Badge variant="outline" className="text-xs shrink-0">{qr.follow_ups.length}追问</Badge>
        )}
      </button>
      {expanded && (
        <div className="divide-y">
          {qr.ai_summary && (
            <div className="px-4 py-3 bg-blue-50/70 border-b border-blue-100">
              <div className="flex items-center gap-1.5 mb-2">
                <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                <span className="text-xs font-semibold text-blue-600">AI 总结</span>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{qr.ai_summary}</p>
            </div>
          )}
          {qr.responses.map((resp, i) => (
            <div key={i} className="px-4 py-3">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">
                  {resp.agent_name?.charAt(0)}
                </div>
                <span className="text-sm font-medium">{resp.agent_name}</span>
                <span className="text-xs">{emotionEmojis[resp.emotion] || "😐"}</span>
                <span className="text-xs text-gray-400">{resp.emotion}</span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap ml-9">{resp.content}</p>
              {resp.score != null && (
                <span className="inline-block ml-9 mt-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded font-medium">
                  {resp.score} / 10
                </span>
              )}
            </div>
          ))}
          {qr.follow_ups.map((fu, j) => (
            <div key={j} className="px-4 py-3 bg-amber-50/50">
              <div className="ml-9">
                <Badge variant="outline" className="text-xs mb-1">追问 {fu.depth}</Badge>
                <p className="text-xs text-amber-700 font-medium mb-2">Q: {fu.question}</p>
                {fu.response && (
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">{fu.response.agent_name}</span>
                      <span className="text-xs">{emotionEmojis[fu.response.emotion] || "😐"}</span>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{fu.response.content}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
