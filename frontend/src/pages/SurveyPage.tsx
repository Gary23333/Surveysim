import { useState, useEffect, useRef } from "react";
import { surveysApi } from "@/api/surveys";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Plus, Edit, Trash2, Download, Upload, FileText, FileDown } from "lucide-react";
import type { Survey, SurveyTemplate, ScenarioType } from "@/types";

const QUESTION_TYPES: Record<string, string> = {
  single_choice: "单选题", multiple_choice: "多选题", open_ended: "开放题", scale: "量表", ranking: "排序",
};
const MODES: Record<string, string> = { global: "全局", sequential: "顺序", open: "开放" };

const scenarioLabels: Record<string, string> = {
  survey: "问卷调查", focus_group: "焦点小组", idi: "深度访谈", debate: "辩论讨论",
};

const TEMPLATE_JSON = {
  name: "示例问卷",
  description: "这是一个示例模板",
  version: "1.0",
  questions: [
    { id: "q1", type: "single_choice", text: "单选题示例", options: ["选项A", "选项B", "选项C"], required: true, mode: "global", visibility: "isolated", enable_text: true, enable_rating: false },
    { id: "q2", type: "open_ended", text: "开放题示例", required: true, mode: "sequential", visibility: "open", enable_text: true, enable_rating: false },
    { id: "q3", type: "open_ended", text: "程度评分示例", required: true, mode: "global", visibility: "isolated", enable_text: true, enable_rating: true, rating_config: { min_value: 1, max_value: 10, min_label: "非常不满意", max_label: "非常满意" } },
  ],
};

export default function SurveyPage() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [templates, setTemplates] = useState<SurveyTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [editingSurvey, setEditingSurvey] = useState<Survey | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [questions, setQuestions] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);
  const [scenarioType, setScenarioType] = useState<ScenarioType>("survey");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [surveysData, templatesData] = await Promise.all([surveysApi.list(), surveysApi.listTemplates()]);
      setSurveys(surveysData); setTemplates(templatesData);
    } catch (error) { console.error("Failed to load:", error); }
    finally { setLoading(false); }
  };

  const handleCreate = () => { setEditingSurvey(null); setName(""); setDescription(""); setQuestions([]); setScenarioType("survey"); setShowEditor(true); };
  const handleEdit = async (survey: Survey) => {
    try {
      const detail = await surveysApi.get(survey.id);
      setEditingSurvey(detail); setName(detail.name); setDescription(detail.description);
      setQuestions((detail.questions || []).map((q: any) => ({ ...q })));
      setScenarioType((detail as any).scenario_type || "survey");
      setShowEditor(true);
    } catch (error) { console.error("Failed to load detail:", error); }
  };
  const handleSave = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      if (editingSurvey) await surveysApi.update(editingSurvey.id, { name, description, questions, scenario_type: scenarioType } as any);
      else await surveysApi.create({ name, description, questions, scenario_type: scenarioType } as any);
      setShowEditor(false); loadData();
    } catch (error) { console.error("Failed to save:", error); }
    finally { setSaving(false); }
  };
  const handleDelete = async (surveyId: string) => { if (confirm("确定删除？")) { await surveysApi.delete(surveyId); loadData(); } };
  const handleFromTemplate = async (templateId: string) => { await surveysApi.fromTemplate(templateId); loadData(); };
  const handleExport = async (surveyId: string) => {
    try {
      const data = await surveysApi.export(surveyId);
      downloadBlob(JSON.stringify(data, null, 2), `survey-${surveyId}.json`);
    } catch (error) { console.error("Export failed:", error); }
  };
  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]; if (!file) return;
    try { await surveysApi.import(file); loadData(); }
    catch (error) { console.error("Import failed:", error); }
  };
  const handleDownloadTemplate = () => {
    downloadBlob(JSON.stringify(TEMPLATE_JSON, null, 2), "survey-template.json");
  };

  const downloadBlob = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
  };

  // Question editing helpers
  const addQuestion = () => {
    setQuestions([...questions, {
      id: `q${questions.length + 1}`, type: "open_ended", text: "", options: [],
      required: true, mode: "global", visibility: "isolated",
      enable_text: true, enable_rating: false,
      rating_config: { min_value: 1, max_value: 10, min_label: "", max_label: "" },
    }]);
  };
  const updateQuestion = (idx: number, field: string, value: any) => {
    const qs = [...questions]; qs[idx] = { ...qs[idx], [field]: value }; setQuestions(qs);
  };
  const updateQOption = (qi: number, oi: number, value: string) => {
    const qs = [...questions]; const opts = [...(qs[qi].options || [])]; opts[oi] = value; qs[qi].options = opts; setQuestions(qs);
  };
  const addQOption = (qi: number) => {
    const qs = [...questions]; if (!qs[qi].options) qs[qi].options = []; qs[qi].options.push(""); setQuestions(qs);
  };
  const removeQOption = (qi: number, oi: number) => {
    const qs = [...questions]; qs[qi].options = (qs[qi].options || []).filter((_: any, i: number) => i !== oi); setQuestions(qs);
  };
  const removeQuestion = (idx: number) => setQuestions(questions.filter((_, i) => i !== idx));

  return (
    <div className="container mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div><h2 className="text-2xl font-bold text-gray-900">问卷管理</h2><p className="text-gray-500 mt-1">创建和管理调研问卷</p></div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
            <FileDown className="w-4 h-4 mr-1" />下载模板
          </Button>
          <Button variant="outline" size="sm" onClick={() => fileRef.current?.click()}>
            <Upload className="w-4 h-4 mr-1" />导入问卷
          </Button>
          <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleImport} />
          <Button size="sm" onClick={handleCreate}><Plus className="w-4 h-4 mr-1" />创建问卷</Button>
        </div>
      </div>

      {/* Templates */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">问卷模板</h3>
        <div className="grid grid-cols-3 gap-4">
          {templates.map(t => (
            <Card key={t.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div><h4 className="font-medium">{t.name}</h4><p className="text-sm text-gray-500">{t.description}</p></div>
                  <Badge variant="secondary">{t.category}</Badge>
                </div>
                <p className="text-sm text-gray-500 mb-4">{t.questions?.length || 0} 个问题</p>
                <Button size="sm" variant="outline" onClick={() => handleFromTemplate(t.id)}>使用模板</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* My surveys */}
      <div>
        <h3 className="text-lg font-semibold mb-4">我的问卷</h3>
        {loading ? <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" /></div> :
        surveys.length === 0 ? (
          <Card><CardContent className="py-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">暂无问卷</p><Button onClick={handleCreate}>创建第一个问卷</Button>
          </CardContent></Card>
        ) : (
          <div className="grid gap-4">
            {surveys.map(s => (
              <Card key={s.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-lg">
                        {s.name}
                        <Badge variant="outline" className="text-xs ml-2">{scenarioLabels[(s as any).scenario_type || "survey"] || "问卷调查"}</Badge>
                      </h4>
                      <p className="text-gray-500 mt-1">{s.description}</p>
                      <p className="text-sm text-gray-400 mt-2">{s.question_count ?? 0} 个问题 · 版本 {s.version}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => handleEdit(s)}><Edit className="w-4 h-4" /></Button>
                      <Button size="sm" variant="outline" onClick={() => handleExport(s.id)}><Download className="w-4 h-4" /></Button>
                      <Button size="sm" variant="ghost" onClick={() => handleDelete(s.id)}><Trash2 className="w-4 h-4 text-red-500" /></Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Editor Dialog */}
      {showEditor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[92vh] overflow-y-auto">
            <CardHeader><CardTitle>{editingSurvey ? "编辑问卷" : "创建问卷"}</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div><Label>问卷名称 *</Label><Input value={name} onChange={e => setName(e.target.value)} placeholder="问卷名称" /></div>
                <div><Label>描述</Label><Input value={description} onChange={e => setDescription(e.target.value)} placeholder="简要描述" /></div>
              </div>

              {/* Scenario type selector */}
              <div>
                <Label>场景类型</Label>
                <RadioGroup
                  value={scenarioType}
                  onValueChange={(value: string) => setScenarioType(value as ScenarioType)}
                  className="grid grid-cols-2 gap-3 mt-2"
                >
                  {[
                    { value: "survey", label: "问卷调查", emoji: "📋", desc: "标准化问题收集" },
                    { value: "focus_group", label: "焦点小组", emoji: "👥", desc: "多人自由讨论" },
                    { value: "idi", label: "深度访谈", emoji: "🎙️", desc: "一对一深入挖掘" },
                    { value: "debate", label: "辩论讨论", emoji: "⚖️", desc: "正反方观点碰撞" },
                  ].map((item) => (
                    <div key={item.value}>
                      <RadioGroupItem value={item.value} id={`sc-${item.value}`} className="peer sr-only" />
                      <Label
                        htmlFor={`sc-${item.value}`}
                        className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                      >
                        <span className="text-2xl mb-1">{item.emoji}</span>
                        <span className="text-sm font-medium">{item.label}</span>
                        <span className="text-xs text-muted-foreground">{item.desc}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>

              {/* Question editor */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>题目列表（{questions.length} 题）</Label>
                  <Button size="sm" variant="outline" onClick={addQuestion}><Plus className="w-3 h-3 mr-1" />添加题目</Button>
                </div>
                <div className="space-y-3 max-h-[50vh] overflow-y-auto border rounded-lg p-3">
                  {questions.length === 0 && (
                    <p className="text-sm text-gray-400 text-center py-6">暂无题目，点击"添加题目"开始</p>
                  )}
                  {questions.map((q, qi) => (
                    <div key={qi} className="border rounded-lg p-3 bg-white space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs shrink-0">#{qi + 1}</Badge>
                        <Select value={q.type} onValueChange={v => { updateQuestion(qi, "type", v); if (v !== "single_choice" && v !== "multiple_choice") { updateQuestion(qi, "options", []); } }}>
                          <SelectTrigger className="w-24 h-7 text-xs"><SelectValue /></SelectTrigger>
                          <SelectContent>
                            {Object.entries(QUESTION_TYPES).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
                          </SelectContent>
                        </Select>
                        <Select value={q.mode || "global"} onValueChange={v => updateQuestion(qi, "mode", v)}>
                          <SelectTrigger className="w-20 h-7 text-xs"><SelectValue /></SelectTrigger>
                          <SelectContent>{Object.entries(MODES).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}</SelectContent>
                        </Select>
                        <div className="flex-1" />
                        <div className="flex items-center gap-1 text-xs">
                          <span>文字</span><Switch checked={q.enable_text !== false} onCheckedChange={v => updateQuestion(qi, "enable_text", v)} />
                          <span>评分</span><Switch checked={q.enable_rating || false} onCheckedChange={v => { updateQuestion(qi, "enable_rating", v); if (v && !q.rating_config) updateQuestion(qi, "rating_config", { min_value: 1, max_value: 10, min_label: "", max_label: "" }); }} />
                        </div>
                        <Button variant="ghost" size="sm" onClick={() => removeQuestion(qi)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                      </div>
                      <Textarea className="text-sm" rows={2} value={q.text || ""} onChange={e => updateQuestion(qi, "text", e.target.value)} placeholder="题目文本..." />
                      {/* Options for choice questions */}
                      {(q.type === "single_choice" || q.type === "multiple_choice") && (
                        <div className="space-y-1 pl-2 border-l-2 border-gray-200">
                          {((q.options as string[]) || []).map((opt: string, oi: number) => (
                            <div key={oi} className="flex items-center gap-1">
                              <Input className="h-7 text-xs flex-1" value={opt} onChange={e => updateQOption(qi, oi, e.target.value)} placeholder={`选项 ${oi + 1}`} />
                              <Button variant="ghost" size="sm" onClick={() => removeQOption(qi, oi)}><Trash2 className="w-3 h-3" /></Button>
                            </div>
                          ))}
                          <Button variant="ghost" size="sm" className="text-xs" onClick={() => addQOption(qi)}><Plus className="w-3 h-3 mr-1" />添加选项</Button>
                        </div>
                      )}
                      {/* Rating config */}
                      {q.enable_rating && (
                        <div className="grid grid-cols-4 gap-2 text-xs pl-2 border-l-2 border-blue-200">
                          <div><span className="text-gray-400">最小值</span><Input className="h-7" type="number" value={q.rating_config?.min_value || 1} onChange={e => updateQuestion(qi, "rating_config", { ...q.rating_config, min_value: +e.target.value })} /></div>
                          <div><span className="text-gray-400">最大值</span><Input className="h-7" type="number" value={q.rating_config?.max_value || 10} onChange={e => updateQuestion(qi, "rating_config", { ...q.rating_config, max_value: +e.target.value })} /></div>
                          <div><span className="text-gray-400">最小标签</span><Input className="h-7" value={q.rating_config?.min_label || ""} onChange={e => updateQuestion(qi, "rating_config", { ...q.rating_config, min_label: e.target.value })} /></div>
                          <div><span className="text-gray-400">最大标签</span><Input className="h-7" value={q.rating_config?.max_label || ""} onChange={e => updateQuestion(qi, "rating_config", { ...q.rating_config, max_label: e.target.value })} /></div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t">
                <Button variant="outline" onClick={() => setShowEditor(false)}>取消</Button>
                <Button onClick={handleSave} disabled={saving}>{saving ? "保存中..." : "保存"}</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
