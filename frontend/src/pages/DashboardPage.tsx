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
import { Label } from "@/components/ui/label";
import {
  Pause, Play, Square, UserCheck, UserMinus, Send, ArrowRight,
  MessageCircle, BarChart3, Wifi, WifiOff, SkipForward, Mic, BookOpen, FileText, ClipboardList,
} from "lucide-react";
import { Link } from "react-router-dom";

const emotionEmojis: Record<string, string> = {
  happy: "😊", sad: "😢", angry: "😠", surprised: "😲", neutral: "😐",
  thinking: "🤔", confused: "😕", excited: "🤩", worried: "😟", curious: "🧐",
  satisfied: "😌", dissatisfied: "😒",
};

/** 等待类型对应的中文标签和图标 */
const awaitingLabels: Record<string, { label: string; icon: React.ReactNode }> = {
  opening: { label: "等待开场白", icon: <Mic className="w-4 h-4" /> },
  guidance: { label: "等待引导语", icon: <BookOpen className="w-4 h-4" /> },
  summary: { label: "等待总结", icon: <FileText className="w-4 h-4" /> },
  next_question: { label: "等待推进下一题", icon: <ArrowRight className="w-4 h-4" /> },
  decision: { label: "等待追问决策", icon: <MessageCircle className="w-4 h-4" /> },
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

  // Awaiting moderator input state
  const [awaitingInput, setAwaitingInput] = useState<string | null>(null);
  const [awaitingContext, setAwaitingContext] = useState<Record<string, any>>({});

  // Human input for opening/guidance/summary
  const [humanInputText, setHumanInputText] = useState("");

  const handleMessage = useCallback((message: any) => {
    if (message.type === "system_event") {
      if (message.event === "question_changed") {
        setQuestionIndex(message.data?.index ?? 0);
        setTotalQuestions(message.data?.total ?? 0);
        setLastQuestionText(message.data?.question_text ?? message.data?.question_id ?? "");
        // 题目已开始回答，清除等待状态
        setAwaitingInput(null);
      } else if (message.event === "moderator_switched") {
        setIsHumanModerator(message.data?.type === "human");
        if (message.data?.type !== "human") {
          setAwaitingInput(null);
        }
      } else if (message.event === "question_answered") {
        const idx = message.data?.index ?? questionIndex;
        setQuestionIndex(idx);
      } else if (message.event === "awaiting_moderator_input") {
        setAwaitingInput(message.data?.input_type ?? null);
        setAwaitingContext(message.data ?? {});
      }
    }
    // 当收到 agent 回答时，如果当前在等待 decision（追问决策），可以清除
    if (message.type === "agent_response" && awaitingInput === "decision") {
      // 不自动清除，等后端发新的 awaiting 事件
    }
    addMessage(message);
  }, [addMessage, questionIndex, awaitingInput]);

  const { sendMessage, connected } = useWebSocket({
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
  };
  const handleRelease = () => {
    sendMessage({ type: "moderator_takeover", action: "release" });
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

  // Human: send opening/guidance/summary
  const handleSendModeratorText = (inputType: string) => {
    if (!humanInputText.trim()) return;
    sendMessage({ type: "moderator_command", command: `moderator_${inputType}`, content: humanInputText.trim() });
    setHumanInputText("");
    setAwaitingInput(null);
  };

  // Human: send follow-up decision (continue / follow_up)
  const handleModeratorDecision = (action: string, followUpQuestion?: string) => {
    sendMessage({
      type: "moderator_command",
      command: "moderator_decision",
      action,
      follow_up_question: followUpQuestion,
      content: followUpQuestion,
      target: awaitingContext.agent_name,
    });
    setAwaitingInput(null);
  };

  // Human: end session
  const handleEndSession = () => {
    sendMessage({ type: "moderator_command", command: "end" });
    if (taskId) stopTask(taskId);
  };

  // Human: skip current waiting
  const handleSkip = () => {
    // Send a default decision to unblock
    if (awaitingInput === "opening" || awaitingInput === "guidance" || awaitingInput === "summary") {
      sendMessage({ type: "moderator_command", command: `moderator_${awaitingInput}`, content: "" });
    } else if (awaitingInput === "decision") {
      handleModeratorDecision("continue");
    } else if (awaitingInput === "next_question") {
      handleNextQuestion();
    }
    setAwaitingInput(null);
  };

  const progress = sessionStatus?.progress;
  const status = currentTask?.status || sessionStatus?.status;
  const canStart = status === "running" || status === "pending";

  const awaiting = awaitingInput ? awaitingLabels[awaitingInput] : null;

  return (
    <div className="container mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{currentTask?.name || "实时监控"}</h2>
          <div className="flex items-center gap-3 mt-1">
            <p className="text-gray-500 text-sm">
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
              {status === "stopped" && "已停止"}
              {status === "error" && "出错"}
            </p>
            {/* WebSocket 连接状态 */}
            <Badge variant={connected ? "outline" : "destructive"} className="text-xs gap-1">
              {connected ? <><Wifi className="w-3 h-3" /> 已连接</> : <><WifiOff className="w-3 h-3" /> 断开</>}
            </Badge>
          </div>
        </div>
        <div className="flex gap-2">
          {status === "running" && (
            <Button variant="outline" size="sm" onClick={() => pauseTask(taskId!)}><Pause className="w-4 h-4 mr-1" />暂停</Button>
          )}
          {status === "paused" && !isHumanModerator && (
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
          {isHumanModerator ? "🧑‍💼 人工主持中" : "🤖 AI 主持中"}
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

      {/* Awaiting moderator input indicator */}
      {isHumanModerator && awaiting && (
        <Card className="mb-4 border-amber-300 bg-amber-50/50">
          <CardContent className="p-3 flex items-center gap-3">
            <div className="animate-pulse">{awaiting.icon}</div>
            <span className="font-medium text-amber-800">{awaiting.label}</span>
            {awaitingInput === "decision" && awaitingContext.agent_name && (
              <span className="text-sm text-amber-600">— {awaitingContext.agent_name}</span>
            )}
            {awaitingInput === "decision" && awaitingContext.question && (
              <span className="text-xs text-amber-500 truncate max-w-md">问题：{awaitingContext.question}</span>
            )}
            <Button size="sm" variant="ghost" className="ml-auto text-xs" onClick={handleSkip}>
              <SkipForward className="w-3 h-3 mr-1" />跳过
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Human Moderator Panel */}
      {isHumanModerator && status !== "pending" && (
        <Card className="mb-4 border-blue-200 bg-blue-50/30">
          <CardContent className="p-4 space-y-3">
            {/* Opening / Guidance / Summary input */}
            {awaitingInput && ["opening", "guidance", "summary"].includes(awaitingInput) && (
              <div className="bg-white rounded-lg p-3 border border-blue-200">
                <Label className="text-sm font-medium text-blue-800 mb-2 block">
                  {awaitingInput === "opening" && "🎤 输入开场白"}
                  {awaitingInput === "guidance" && "📖 输入引导语"}
                  {awaitingInput === "summary" && "📝 输入总结"}
                </Label>
                {awaitingInput === "guidance" && awaitingContext.topic && (
                  <p className="text-xs text-gray-500 mb-2">主题：{awaitingContext.topic} · 第 {(awaitingContext.round ?? 0) + 1} 轮</p>
                )}
                {awaitingInput === "summary" && awaitingContext.response_count !== undefined && (
                  <p className="text-xs text-gray-500 mb-2">共 {awaitingContext.response_count} 条回答</p>
                )}
                <div className="flex gap-2">
                  <textarea
                    className="flex-1 min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={humanInputText}
                    onChange={(e) => setHumanInputText(e.target.value)}
                    placeholder={
                      awaitingInput === "opening" ? "输入开场白内容，介绍调研主题和参与者..." :
                      awaitingInput === "guidance" ? "输入引导语，推动讨论深入..." :
                      "输入总结内容..."
                    }
                  />
                  <div className="flex flex-col gap-2">
                    <Button size="sm" onClick={() => handleSendModeratorText(awaitingInput)}>
                      <Send className="w-3 h-3 mr-1" />发送
                    </Button>
                    <Button size="sm" variant="ghost" onClick={handleSkip}>
                      <SkipForward className="w-3 h-3 mr-1" />跳过
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Decision input (follow-up evaluation) */}
            {awaitingInput === "decision" && (
              <div className="bg-white rounded-lg p-3 border border-blue-200">
                <Label className="text-sm font-medium text-blue-800 mb-2 block">
                  🤔 是否需要追问？
                </Label>
                {awaitingContext.agent_name && (
                  <p className="text-xs text-gray-500 mb-1">回答者：{awaitingContext.agent_name}</p>
                )}
                {awaitingContext.question && (
                  <p className="text-xs text-gray-500 mb-2">问题：{awaitingContext.question}</p>
                )}
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => handleModeratorDecision("continue")}>
                    ✅ 继续下一题
                  </Button>
                  <div className="flex-1 flex gap-2">
                    <Input
                      value={followUpInput}
                      onChange={(e) => setFollowUpInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleModeratorDecision("follow_up", followUpInput)}
                      placeholder="输入追问内容..."
                    />
                    <Button size="sm" onClick={() => handleModeratorDecision("follow_up", followUpInput)}>
                      <MessageCircle className="w-3 h-3 mr-1" />追问
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Question controls */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="text-sm">
                  <ClipboardList className="w-3 h-3 mr-1" />
                  第 {questionIndex + 1} / {totalQuestions || "?"} 题
                </Badge>
                {lastQuestionText && <span className="text-sm text-gray-600 truncate">{lastQuestionText}</span>}
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleNextQuestion} className="gap-1">
                  <ArrowRight className="w-3 h-3" />
                  {questionIndex === 0 && !agentResponses.length ? "开始本题" : "开始本题（重新回答）"}
                </Button>
                <Button size="sm" variant="outline" onClick={handleEndSession}>
                  <Square className="w-3 h-3 mr-1" />结束调研
                </Button>
              </div>
            </div>

            {/* Custom broadcast question */}
            <div>
              <Label className="text-xs text-gray-500 mb-1 block">群发提问（可选）</Label>
              <div className="flex gap-2">
                <Input
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
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          msg.agent_id === "moderator" ? "bg-purple-100 text-purple-600" : "bg-blue-100 text-blue-600"
                        }`}>
                          {msg.agent_id === "moderator" ? "🎤" : msg.agent_name?.charAt(0)}
                        </div>
                        <span className="font-medium text-sm">{msg.agent_name}</span>
                        {msg.agent_id !== "moderator" && (
                          <Badge variant="outline" className="text-xs">{emotionEmojis[msg.emotion] || "😐"} {msg.emotion}</Badge>
                        )}
                        {msg.score !== undefined && msg.score !== null && (
                          <Badge variant="secondary" className="text-xs">⭐ {msg.score}/10</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{msg.content}</p>
                      {isHumanModerator && msg.agent_id !== "moderator" && (
                        <div className="mt-2">
                          {followUpTarget === msg.agent_id ? (
                            <div className="flex gap-2">
                              <Input
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
