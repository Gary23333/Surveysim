import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTaskStore } from "@/stores/taskStore";
import { surveysApi } from "@/api/surveys";
import { personasApi } from "@/api/personas";
import { providersApi } from "@/api/providers";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import {
  Dialog, DialogContent, DialogDescription,
  DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { ArrowLeft, ArrowRight, Brain, Check, FolderOpen, Plus, Trash2 } from "lucide-react";
import type { ScenarioType, AgentConfig, TaskCreate, Survey, PersonaSummary, Provider, BehaviorPrompt, PersonaGroup, ModeratorConfig } from "@/types";
import { behaviorPromptsApi } from "@/api/providers";

const steps = [
  { title: "基本信息", description: "设置任务名称和类型" },
  { title: "选择问卷", description: "选择或创建问卷" },
  { title: "配置参与者", description: "设置AI参与者" },
  { title: "确认创建", description: "检查并创建任务" },
];

export default function TaskCreatePage() {
  const navigate = useNavigate();
  const { createTask } = useTaskStore();
  const { toast } = useToast();

  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // 表单数据
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [scenarioType, setScenarioType] = useState<ScenarioType>("survey");
  const [surveyId, setSurveyId] = useState("");
  const [agents, setAgents] = useState<AgentConfig[]>([]);

  // 主持人配置
  const [moderatorType, setModeratorType] = useState<"ai" | "human">("ai");
  const [moderatorProvider, setModeratorProvider] = useState("");
  const [moderatorModel, setModeratorModel] = useState("");
  const [moderatorBehaviorPrompt, setModeratorBehaviorPrompt] = useState("neutral");
  const [humanModeratorName, setHumanModeratorName] = useState("主持人");

  // 选项数据
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [personas, setPersonas] = useState<PersonaSummary[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [behaviorPrompts, setBehaviorPrompts] = useState<BehaviorPrompt[]>([]);
  const [personaGroups, setPersonaGroups] = useState<PersonaGroup[]>([]);
  const [showGroupImport, setShowGroupImport] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);

  // 获取第一个已配置的供应商（有 API Key 的）
  const getConfiguredProvider = () => providers.find(p => p.configured) || providers[0];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setDataLoading(true);
    try {
      const [surveysData, personasData, providersData, promptsData, groupsData] = await Promise.all([
        surveysApi.list(),
        personasApi.list(),
        providersApi.list(),
        behaviorPromptsApi.list(),
        personasApi.listGroups(),
      ]);
      setSurveys(surveysData);
      setPersonas(personasData);
      setProviders(providersData);
      setBehaviorPrompts(promptsData);
      setPersonaGroups(groupsData);
    } catch (error) {
      console.error("Failed to load data:", error);
      toast({ title: "数据加载失败", description: "请刷新页面重试", variant: "destructive" });
    } finally {
      setDataLoading(false);
    }
  };

  const addAgent = () => {
    const defaultProvider = getConfiguredProvider();
    const newAgent: AgentConfig = {
      id: `agent_${Date.now()}`,
      name: `参与者 ${agents.length + 1}`,
      persona_id: "",
      provider_pack: defaultProvider?.name || "",
      model: defaultProvider?.models[0]?.id || "",
      behavior_prompt_id: behaviorPrompts[0]?.id || "",
    };
    setAgents([...agents, newAgent]);
  };

  const updateAgent = (index: number, updates: Partial<AgentConfig>) => {
    const updated = [...agents];
    updated[index] = { ...updated[index], ...updates };
    setAgents(updated);
  };

  const removeAgent = (index: number) => {
    setAgents(agents.filter((_, i) => i !== index));
  };

  const importFromGroup = async (groupId: string) => {
    try {
      const groupPersonas = await personasApi.getGroupPersonas(groupId);
      const defaultProvider = getConfiguredProvider();
      const newAgents: AgentConfig[] = groupPersonas.map((p: PersonaSummary) => ({
        id: `agent_${Date.now()}_${p.id}`,
        name: p.name,
        persona_id: p.id,
        provider_pack: defaultProvider?.name || "",
        model: defaultProvider?.models?.[0]?.id || "",
        behavior_prompt_id: behaviorPrompts[0]?.id || "",
      }));
      setAgents([...agents, ...newAgents]);
      setShowGroupImport(false);
    } catch (error) {
      console.error("Failed to import group:", error);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setFormError(null);
    try {
      const moderator: ModeratorConfig = moderatorType === "human"
        ? { type: "human", behavior_prompt_id: "neutral", human_name: humanModeratorName }
        : {
            type: "ai",
            provider_pack: moderatorProvider && moderatorProvider !== "__default" ? moderatorProvider : undefined,
            model: moderatorModel || undefined,
            behavior_prompt_id: moderatorBehaviorPrompt,
          };

      const taskData: TaskCreate = {
        name,
        description,
        scenario_type: scenarioType,
        survey_id: surveyId,
        agents,
        moderator,
      };

      const task = await createTask(taskData);
      toast({ title: "任务创建成功", description: `任务 "${name}" 已创建` });
      navigate(`/tasks/${task.id}/dashboard`);
    } catch (error: any) {
      const msg = error?.response?.data?.detail || error?.message || "创建任务失败";
      setFormError(typeof msg === "string" ? msg : JSON.stringify(msg));
      toast({ title: "创建失败", description: String(msg), variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return name.trim() && scenarioType;
      case 1:
        return surveyId;
      case 2:
        return agents.length > 0 && agents.every((a) => a.persona_id && a.provider_pack && a.model);
      case 3:
        return true;
      default:
        return false;
    }
  };

  // 检查是否有未配置的供应商
  const hasUnconfiguredProvider = agents.some(a => {
    const p = providers.find(pp => pp.name === a.provider_pack);
    return p && p.configured === false;
  });

  return (
    <div className="container mx-auto max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">创建调研任务</h2>
        <p className="text-gray-500 mt-1">按照向导完成任务配置</p>
      </div>

      {/* 步骤指示器 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                  index < currentStep
                    ? "bg-blue-600 text-white"
                    : index === currentStep
                    ? "bg-blue-100 text-blue-600 border-2 border-blue-600"
                    : "bg-gray-100 text-gray-500"
                }`}
              >
                {index < currentStep ? <Check className="w-5 h-5" /> : index + 1}
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">{step.title}</p>
                <p className="text-xs text-gray-500">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-24 h-0.5 mx-4 ${index < currentStep ? "bg-blue-600" : "bg-gray-200"}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 步骤内容 */}
      <Card className="mb-8">
        <CardContent className="p-6">
          {/* Step 1: 基本信息 */}
          {currentStep === 0 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="name">任务名称</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="例如：Q2客户满意度调查"
                />
              </div>

              <div>
                <Label htmlFor="description">任务描述</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
                  placeholder="描述本次调研的目的和背景"
                />
              </div>

              <div>
                <Label>场景类型</Label>
                <RadioGroup
                  value={scenarioType}
                  onValueChange={(value: string) => setScenarioType(value as ScenarioType)}
                  className="grid grid-cols-2 gap-4 mt-2"
                >
                  {[
                    { value: "survey", label: "问卷调查", emoji: "📋", desc: "标准化问题收集" },
                    { value: "focus_group", label: "焦点小组", emoji: "👥", desc: "多人自由讨论" },
                    { value: "idi", label: "深度访谈", emoji: "🎙️", desc: "一对一深入挖掘" },
                    { value: "debate", label: "辩论讨论", emoji: "⚖️", desc: "正反方观点碰撞" },
                  ].map((item) => (
                    <div key={item.value}>
                      <RadioGroupItem value={item.value} id={item.value} className="peer sr-only" />
                      <Label
                        htmlFor={item.value}
                        className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                      >
                        <span className="text-3xl mb-2">{item.emoji}</span>
                        <span className="text-sm font-medium">{item.label}</span>
                        <span className="text-xs text-muted-foreground">{item.desc}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              {/* 主持人配置 */}
              <div>
                <Label>主持人类型</Label>
                <RadioGroup
                  value={moderatorType}
                  onValueChange={(value: string) => setModeratorType(value as "ai" | "human")}
                  className="grid grid-cols-2 gap-4 mt-2"
                >
                  <div>
                    <RadioGroupItem value="ai" id="mod-ai" className="peer sr-only" />
                    <Label
                      htmlFor="mod-ai"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-3xl mb-2">🤖</span>
                      <span className="text-sm font-medium">AI 主持人</span>
                      <span className="text-xs text-muted-foreground">自动引导、追问</span>
                    </Label>
                  </div>
                  <div>
                    <RadioGroupItem value="human" id="mod-human" className="peer sr-only" />
                    <Label
                      htmlFor="mod-human"
                      className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                    >
                      <span className="text-3xl mb-2">🧑‍💼</span>
                      <span className="text-sm font-medium">人工主持人</span>
                      <span className="text-xs text-muted-foreground">全程手动控制</span>
                    </Label>
                  </div>
                </RadioGroup>

                {/* AI 主持人配置 */}
                {moderatorType === "ai" && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
                    <p className="text-xs text-gray-500">AI 主持人配置（可选，未配置时自动复用第一个参与者的 LLM）</p>
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <Label className="text-xs">LLM 配置</Label>
                        <Select
                          value={moderatorProvider}
                          onValueChange={(v) => { setModeratorProvider(v); setModeratorModel(""); }}
                        >
                          <SelectTrigger><SelectValue placeholder="默认" /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="__default">默认（复用参与者）</SelectItem>
                            {providers.map((p) => (
                              <SelectItem key={p.name} value={p.name}>{p.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label className="text-xs">模型</Label>
                        <Select
                          value={moderatorModel}
                          onValueChange={setModeratorModel}
                        >
                          <SelectTrigger><SelectValue placeholder="默认" /></SelectTrigger>
                          <SelectContent>
                            {(providers.find((p) => p.name === moderatorProvider)?.models || []).map((m) => (
                              <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label className="text-xs">行为模式</Label>
                        <Select value={moderatorBehaviorPrompt} onValueChange={setModeratorBehaviorPrompt}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            {behaviorPrompts.map((bp) => (
                              <SelectItem key={bp.id} value={bp.id}>{bp.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                )}

                {/* 人工主持人配置 */}
                {moderatorType === "human" && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
                    <p className="text-xs text-gray-500">人工主持人配置</p>
                    <div>
                      <Label className="text-xs">主持人名称</Label>
                      <Input
                        value={humanModeratorName}
                        onChange={(e) => setHumanModeratorName(e.target.value)}
                        placeholder="主持人"
                        className="w-48"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: 选择问卷 */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <Label>选择问卷</Label>
              {surveys.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>暂无问卷</p>
                  <Button variant="link" className="mt-2">
                    去创建问卷
                  </Button>
                </div>
              ) : (
                <div className="grid gap-3">
                  {surveys.map((survey) => (
                    <div
                      key={survey.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        surveyId === survey.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => setSurveyId(survey.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{survey.name}</h4>
                          <p className="text-sm text-gray-500">
                            {survey.question_count ?? survey.questions?.length ?? 0} 个问题
                          </p>
                        </div>
                        {surveyId === survey.id && (
                          <Check className="w-5 h-5 text-blue-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 3: 配置参与者 */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">配置参与者</h3>
                  <p className="text-sm text-gray-500">为每个参与者选择人格、LLM和行为模式</p>
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => setShowGroupImport(true)} variant="outline" size="sm" disabled={dataLoading}>
                    <FolderOpen className="w-4 h-4 mr-2" />
                    从分组导入
                  </Button>
                  <Button onClick={addAgent} variant="outline" size="sm" disabled={dataLoading}>
                    <Plus className="w-4 h-4 mr-2" />
                    添加参与者
                  </Button>
                </div>
              </div>

              {agents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>{dataLoading ? "正在加载数据..." : "还没有添加参与者"}</p>
                  {!dataLoading && (
                    <Button onClick={addAgent} variant="link" className="mt-2">
                      点击添加第一个参与者
                    </Button>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {/* 未配置供应商警告 */}
                  {hasUnconfiguredProvider && (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
                      ⚠️ 部分参与者使用的 LLM 供应商未配置 API Key，请先到「供应商配置」页面填写，否则任务创建会失败。
                    </div>
                  )}
                  {agents.map((agent, index) => (
                    <Card key={agent.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-4">
                          <Input
                            value={agent.name}
                            onChange={(e) => updateAgent(index, { name: e.target.value })}
                            placeholder="参与者名称"
                            className="w-48"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeAgent(index)}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <Label>人格模板</Label>
                            <Select
                              value={agent.persona_id}
                              onValueChange={(value) => updateAgent(index, { persona_id: value })}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="选择人格" />
                              </SelectTrigger>
                              <SelectContent>
                                {personas.map((persona) => (
                                  <SelectItem key={persona.id} value={persona.id}>
                                    {persona.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div>
                            <Label>LLM配置</Label>
                            <Select
                              value={agent.provider_pack}
                              onValueChange={(value) => {
                                const provider = providers.find((p) => p.name === value);
                                updateAgent(index, {
                                  provider_pack: value,
                                  model: provider?.models[0]?.id || "",
                                });
                              }}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="选择LLM" />
                              </SelectTrigger>
                              <SelectContent>
                                {providers.map((provider) => (
                                  <SelectItem key={provider.name} value={provider.name}>
                                    {provider.name}{provider.configured === false ? " ⚠️ 未配置" : ""}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div>
                            <Label>模型</Label>
                            <Select
                              value={agent.model}
                              onValueChange={(value) => updateAgent(index, { model: value })}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="选择模型" />
                              </SelectTrigger>
                              <SelectContent>
                                {providers
                                  .find((p) => p.name === agent.provider_pack)
                                  ?.models.map((model) => (
                                    <SelectItem key={model.id} value={model.id}>
                                      {model.name}
                                    </SelectItem>
                                  ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div>
                            <Label>行为模式</Label>
                            <Select
                              value={agent.behavior_prompt_id}
                              onValueChange={(value) => updateAgent(index, { behavior_prompt_id: value })}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="选择行为模式" />
                              </SelectTrigger>
                              <SelectContent>
                                {behaviorPrompts.map((prompt) => (
                                  <SelectItem key={prompt.id} value={prompt.id}>
                                    {prompt.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        {/* Thinking mode */}
                        {(() => {
                          const prov = providers.find((p) => p.name === agent.provider_pack);
                          const modelInfo = prov?.models?.find((m) => m.id === agent.model);
                          const tc = prov?.thinking_config;
                          if (!modelInfo?.supports_thinking || !tc || tc.mode === "none") return null;
                          return (
                            <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center gap-2">
                                  <Brain className="w-4 h-4 text-purple-600" />
                                  <Label className="text-sm font-medium text-purple-800">思考模式</Label>
                                </div>
                                <Switch
                                  checked={agent.thinking_enabled || false}
                                  onCheckedChange={(v) => updateAgent(index, { thinking_enabled: v, thinking_intensity: v ? (agent.thinking_intensity || tc.effort_values?.[0] || "medium") : "medium" })}
                                />
                                {agent.thinking_enabled && tc.mode !== "toggle" && tc.effort_values && tc.effort_values.length > 0 && (
                                  <Select
                                    value={agent.thinking_intensity || tc.effort_values[0]}
                                    onValueChange={(v) => updateAgent(index, { thinking_intensity: v })}
                                  >
                                    <SelectTrigger className="w-28 h-8 text-xs">
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {tc.effort_values.map((v: string) => (
                                        <SelectItem key={v} value={v}>{v}</SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                )}
                                {tc.mode === "toggle" && agent.thinking_enabled && (
                                  <span className="text-xs text-purple-600">已启用</span>
                                )}
                              </div>
                            </div>
                          );
                        })()}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 4: 确认创建 */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center">
                <Check className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium">确认任务配置</h3>
                <p className="text-sm text-gray-500">请检查以下配置信息，确认无误后点击创建</p>
              </div>

              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">基本信息</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="space-y-2">
                      <div className="flex justify-between">
                        <dt className="text-gray-500">任务名称</dt>
                        <dd>{name}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">场景类型</dt>
                        <dd>{scenarioType}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-gray-500">主持人</dt>
                        <dd>
                          {moderatorType === "ai" ? "🤖 AI 主持人" : `🧑‍💼 ${humanModeratorName}`}
                          {moderatorType === "ai" && moderatorProvider && moderatorProvider !== "__default" && (
                            <span className="text-xs text-gray-400 ml-2">({moderatorProvider})</span>
                          )}
                        </dd>
                      </div>
                    </dl>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">参与者</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {agents.map((agent) => (
                        <div key={agent.id} className="flex items-center gap-2">
                          <span className="text-sm font-medium">{agent.name}</span>
                          <span className="text-sm text-gray-500">
                            {personas.find((p) => p.id === agent.persona_id)?.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 错误提示 */}
      {formError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          ❌ {formError}
        </div>
      )}

      {/* 导航按钮 */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={() => setCurrentStep(currentStep - 1)}
          disabled={currentStep === 0}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          上一步
        </Button>

        <div className="flex items-center gap-3">
          {/* 验证提示 */}
          {currentStep === 2 && !canProceed() && (
            <span className="text-xs text-amber-600">
              请确保所有参与者的「人格模板」「LLM配置」「模型」都已选择
            </span>
          )}
          {currentStep === 0 && !canProceed() && (
            <span className="text-xs text-amber-600">
              请填写任务名称
            </span>
          )}
          {currentStep === 1 && !canProceed() && (
            <span className="text-xs text-amber-600">
              请选择一份问卷
            </span>
          )}

          {currentStep < steps.length - 1 ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed()}
            >
              下一步
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={!canProceed() || loading}
            >
              {loading ? "创建中..." : "创建任务"}
            </Button>
          )}
        </div>
      </div>

      {/* Group Import Dialog */}
      <Dialog open={showGroupImport} onOpenChange={setShowGroupImport}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>从分组导入参与者</DialogTitle>
            <DialogDescription>选择一个分组，该分组内的所有人格将自动添加为参与者。</DialogDescription>
          </DialogHeader>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {personaGroups.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">暂无分组，请先在人格管理中创建分组</p>
            ) : (
              personaGroups.map((g) => (
                <Card key={g.id} className="cursor-pointer hover:bg-gray-50" onClick={() => importFromGroup(g.id)}>
                  <CardContent className="p-3 flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-sm">{g.name}</h4>
                      <p className="text-xs text-gray-500">{g.description}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">{g.persona_ids?.length || 0} 人</Badge>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowGroupImport(false)}>取消</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
