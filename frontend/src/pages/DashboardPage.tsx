import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useTaskStore } from "@/stores/taskStore";
import { useWebSocketStore } from "@/stores/websocketStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Pause, Play, Square, UserCheck, UserMinus, Send, ArrowRight, MessageCircle, BarChart3 } from "lucide-react";
import { Link } from "react-router-dom";

const emotionEmojis: Record<string, string> = {
  happy: "😊", sad: "😢", angry: "😠", surprised: "😲", neutral: "😐",
  thinking: "🤔", confused: "😕", excited: "🤩", worried: "😟", curious: "🧐",
  satisfied: "😌", dissatisfied: "😒",
};

export default function DashboardPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const { currentTask, sessionStatus, fetchTask, fetchStatus, pauseTask, resumeTask, stopTask } = useTaskStore();
  const { agentResponses, addMessage } = useWebSocketStore();
  const [isHumanModerator, setIsHumanModerator] = useState(false);

  // Human moderator state
  const [manualInput, setManualInput] = useState("");
  const [followUpTarget, setFollowUpTarget] = useState<string | null>(null);
  const [followUpInput, setFollowUpInput] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [lastQuestionText, setLastQuestionText] = useState("");

  const handleMessage = useCallback((message: any) => {
    if (message.type === "system_event") {
      if (message.event === "question_changed") {
        setQuestionIndex(message.data?.index ?? 0);
        setTotalQuestions(message.data?.total ?? 0);
        setLastQuestionText(message.data?.question_text ?? message.data?.question_id ?? "");
      } else if (message.event === "moderator_switched") {
        setIsHumanModerator(message.data?.type === "human");
      } else if (message.event === "question_answered") {
        const idx = message.data?.index ?? questionIndex;
        setQuestionIndex(idx);
      }
    }
    addMessage(message);
  }, [addMessage, questionIndex]);

  const { sendMessage } = useWebSocket({
    sessionId: taskId || "",
    onMessage: handleMessage,
  });

  useEffect(() => {
    if (taskId) { fetchTask(taskId); }
    const interval = setInterval(() => { if (taskId) fetchStatus(taskId); }, 3000);
    return () => clearInterval(interval);
  }, [taskId]);

  // Human: takeover/release
  const handleTakeover = () => {
    sendMessage({ type: "moderator_takeover", action: "takeover" });
    setIsHumanModerator(true);
  };
  const handleRelease = () => {
    sendMessage({ type: "moderator_takeover", action: "release" });
    setIsHumanModerator(false);
  };

  // Human: start current question
  const handleNextQuestion = () => {
    sendMessage({ type: "moderator_command", command: "next_question", index: questionIndex });
  };

  // Human: custom question to all
  const handleSendAll = () => {
    if (!manualInput.trim()) return;
    sendMessage({ type: "moderator_command", command: "ask_question", target: "all", question: manualInput.trim() });
    setManualInput("");
  };

  // Human: follow-up to specific agent
  const handleFollowUp = (agentId: string) => {
    if (!followUpInput.trim()) return;
    sendMessage({ type: "moderator_command", command: "follow_up", target: agentId, question: followUpInput.trim() });
    setFollowUpInput("");
    setFollowUpTarget(null);
  };

  const progress = sessionStatus?.progress;
  const status = currentTask?.status || sessionStatus?.status;

  const canStart = status === "running" || status === "pending";

  return (
    <div className="container mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{currentTask?.name || "实时监控"}</h2>
          <p className="text-gray-500 text-sm mt-1">
            {status === "running" && `运行中 · 进度 ${questionIndex + 1}/${totalQuestions || progress?.total || "?"}`}
            {status === "pending" && "待启动"}
            {status === "completed" && (
              <span className="flex items-center gap-2">
                已完成
                <Link to={`/tasks/${taskId}/results`}>
                  <Badge className="bg-green-600 cursor-pointer hover:bg-green-700">
                    <BarChart3 className="w-3 h-3 mr-1" />查看结果
                  </Badge>
                </Link>
              </span>
            )}
            {status === "paused" && "已暂停"}
          </p>
        </div>
        <div className="flex gap-2">
          {status === "running" && (
            <Button variant="outline" size="sm" onClick={() => pauseTask(taskId!)}><Pause className="w-4 h-4 mr-1" />暂停</Button>
          )}
          {status === "paused" && (
            <Button variant="outline" size="sm" onClick={() => resumeTask(taskId!)}><Play className="w-4 h-4 mr-1" />继续</Button>
          )}
          {(status === "running" || status === "paused") && (
            <Button variant="outline" size="sm" onClick={() => stopTask(taskId!)}><Square className="w-4 h-4 mr-1" />停止</Button>
          )}
        </div>
      </div>

      {/* Moderator toggle */}
      <div className="mb-4 flex items-center gap-3">
        <Badge variant={isHumanModerator ? "default" : "outline"} className="text-sm py-1">
          {isHumanModerator ? "人工主持中" : "AI 主持中"}
        </Badge>
        {canStart && (
          isHumanModerator ? (
            <Button size="sm" variant="outline" onClick={handleRelease}>
              <UserMinus className="w-3 h-3 mr-1" />交回 AI
            </Button>
          ) : (
            <Button size="sm" variant="outline" onClick={handleTakeover}>
              <UserCheck className="w-3 h-3 mr-1" />接管主持人
            </Button>
          )
        )}
      </div>

      {/* Human Moderator Panel */}
      {isHumanModerator && status !== "pending" && (
        <Card className="mb-4 border-blue-200 bg-blue-50/30">
          <CardContent className="p-4 space-y-3">
            {/* Question controls */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="text-sm">第 {questionIndex + 1} / {totalQuestions || "?"} 题</Badge>
                {lastQuestionText && <span className="text-sm text-gray-600 truncate">{lastQuestionText}</span>}
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleNextQuestion} className="gap-1">
                  <ArrowRight className="w-3 h-3" />
                  {questionIndex === 0 && !agentResponses.length ? "开始本题" : "开始本题（重新回答）"}
                </Button>
              </div>
            </div>

            {/* Custom broadcast question */}
            <div>
              <Label className="text-xs text-gray-500 mb-1 block">群发提问（可选）</Label>
              <div className="flex gap-2">
                <Input
                  size={40}
                  value={manualInput}
                  onChange={(e) => setManualInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendAll()}
                  placeholder="向全体参与者提问..."
                />
                <Button size="sm" onClick={handleSendAll}><Send className="w-3 h-3" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Agent Responses */}
      <div className="grid grid-cols-1 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center justify-between">
              <span>参与者回答</span>
              <Badge variant="secondary">{agentResponses.length} 条</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[50vh]">
              {agentResponses.length === 0 ? (
                <p className="text-gray-400 text-center py-8">等待参与者回答...</p>
              ) : (
                <div className="space-y-3">
                  {[...agentResponses].reverse().map((msg, i) => (
                    <div key={i} className="border rounded-lg p-3 bg-white">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600">
                          {msg.agent_name?.charAt(0)}
                        </div>
                        <span className="font-medium text-sm">{msg.agent_name}</span>
                        <Badge variant="outline" className="text-xs">{emotionEmojis[msg.emotion] || "😐"} {msg.emotion}</Badge>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{msg.content}</p>
                      {isHumanModerator && (
                        <div className="mt-2">
                          {followUpTarget === msg.agent_id ? (
                            <div className="flex gap-2">
                              <Input
                                size={30}
                                value={followUpInput}
                                onChange={(e) => setFollowUpInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleFollowUp(msg.agent_id)}
                                placeholder="输入追问内容..."
                                autoFocus
                              />
                              <Button size="sm" onClick={() => handleFollowUp(msg.agent_id)}>发送</Button>
                              <Button size="sm" variant="ghost" onClick={() => { setFollowUpTarget(null); setFollowUpInput(""); }}>取消</Button>
                            </div>
                          ) : (
                            <Button size="sm" variant="ghost" className="text-xs" onClick={() => setFollowUpTarget(msg.agent_id)}>
                              <MessageCircle className="w-3 h-3 mr-1" />追问
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Label({ className, children, htmlFor }: { className?: string; children: React.ReactNode; htmlFor?: string }) {
  return <label htmlFor={htmlFor} className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className || ""}`}>{children}</label>;
}
