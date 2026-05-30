import { useState, useEffect } from "react";
import { providersApi, behaviorPromptsApi } from "@/api/providers";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import {
  Dialog, DialogContent, DialogDescription,
  DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Plus, Edit, Trash2, Settings, FileText, Search, Zap } from "lucide-react";
import type { Provider, BehaviorPrompt, ModelInfo, ThinkingConfig } from "@/types";

const PRESETS: { name: string; label: string; icon: string }[] = [
  { name: "OpenAI", label: "OpenAI", icon: "🤖" },
  { name: "MiMo", label: "小米 MiMo", icon: "📱" },
  { name: "DeepSeek", label: "DeepSeek", icon: "🐋" },
  { name: "Volcengine", label: "豆包(火山引擎)", icon: "🌋" },
];

const DEFAULT_TC: ThinkingConfig = { mode: "none", effort_values: [] };

export default function ConfigPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [behaviorPrompts, setBehaviorPrompts] = useState<BehaviorPrompt[]>([]);
  const [loading, setLoading] = useState(true);

  // Provider dialog
  const [providerDialog, setProviderDialog] = useState(false);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [providerForm, setProviderForm] = useState({ name: "", base_url: "", api_key: "", default_model: "", models: [] as ModelInfo[] });
  const [providerSaving, setProviderSaving] = useState(false);
  const [providerError, setProviderError] = useState("");

  // Test connect state
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  // Detect models state
  const [detectedModels, setDetectedModels] = useState<any[] | null>(null);
  const [detecting, setDetecting] = useState(false);

  // Prompt dialog
  const [promptDialog, setPromptDialog] = useState(false);
  const [editingPromptId, setEditingPromptId] = useState<string | null>(null);
  const [promptForm, setPromptForm] = useState({ id: "", name: "", description: "", prompt: "" });
  const [promptSaving, setPromptSaving] = useState(false);
  const [promptError, setPromptError] = useState("");

  // Delete confirm
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: "provider" | "prompt"; id: string; name: string } | null>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [providersData, promptsData] = await Promise.all([
        providersApi.list(), behaviorPromptsApi.list(),
      ]);
      setProviders(providersData);
      setBehaviorPrompts(promptsData);
    } catch (error) { console.error("Failed to load data:", error); }
    finally { setLoading(false); }
  };

  // ========= Provider =========
  const openAddProvider = (preset?: string) => {
    setEditingProvider(null);
    setTestResult(null);
    setDetectedModels(null);
    if (preset) {
      setProviderForm({ name: preset, base_url: "", api_key: "", default_model: "", models: [] });
    } else {
      setProviderForm({ name: "", base_url: "", api_key: "", default_model: "", models: [] });
    }
    setProviderError("");
    setProviderDialog(true);
  };

  const openEditProvider = (p: Provider) => {
    setEditingProvider(p.name);
    setTestResult(null);
    setDetectedModels(null);
    setProviderForm({
      name: p.name, base_url: p.base_url || "",
      api_key: "", default_model: p.default_model || "",
      models: (p.models || []).map(m => ({ ...m, supports_thinking: m.supports_thinking || false })),
    });
    setProviderError("");
    setProviderDialog(true);
  };

  const addModelRow = () => {
    setProviderForm({
      ...providerForm,
      models: [...providerForm.models, { id: "", name: "", max_tokens: 4096, supports_thinking: false }],
    });
  };

  const updateModelRow = (idx: number, field: string, value: any) => {
    const updated = [...providerForm.models];
    (updated[idx] as any)[field] = value;
    setProviderForm({ ...providerForm, models: updated });
  };

  const removeModelRow = (idx: number) => {
    setProviderForm({ ...providerForm, models: providerForm.models.filter((_, i) => i !== idx) });
  };

  const handleSaveProvider = async () => {
    setProviderError("");
    if (!providerForm.name.trim()) { setProviderError("名称不能为空"); return; }
    if (!providerForm.base_url.trim()) { setProviderError("Base URL不能为空"); return; }
    if (!providerForm.api_key.trim()) { setProviderError("API Key不能为空"); return; }
    if (providerForm.models.length === 0) { setProviderError("至少添加一个模型"); return; }
    if (providerForm.models.some(m => !m.id.trim())) { setProviderError("所有模型的ID不能为空"); return; }

    setProviderSaving(true);
    try {
      const data: any = {
        name: providerForm.name.trim(),
        base_url: providerForm.base_url.trim(),
        api_key: providerForm.api_key.trim(),
        default_model: providerForm.default_model.trim() || providerForm.models[0].id,
        models: providerForm.models.map(m => ({
          id: m.id, name: m.name || m.id, max_tokens: m.max_tokens || 4096,
          supports_thinking: m.supports_thinking || false,
        })),
      };
      if (editingProvider) {
        await providersApi.update(editingProvider, data);
      } else {
        await providersApi.create(data);
      }
      setProviderDialog(false);
      await loadData();
    } catch (error: any) {
      setProviderError(error?.response?.data?.detail || error?.message || "保存失败");
    } finally { setProviderSaving(false); }
  };

  const handleDeleteProvider = (name: string) => {
    setDeleteTarget({ type: "provider", id: name, name });
    setDeleteDialog(true);
  };

  const handleTestConnect = async () => {
    if (!providerForm.name.trim()) { setProviderError("请先填写名称并保存Provider"); return; }
    setTesting(true);
    setTestResult(null);
    try {
      const result = await providersApi.testConnect(providerForm.name.trim());
      setTestResult(result);
    } catch (error: any) {
      setTestResult({ success: false, error: error?.response?.data?.detail || error?.message || "测试失败" });
    } finally { setTesting(false); }
  };

  const handleDetectModels = async () => {
    if (!providerForm.name.trim()) { setProviderError("请先填写名称并保存Provider"); return; }
    setDetecting(true);
    setDetectedModels(null);
    try {
      const result = await providersApi.detectModels(providerForm.name.trim());
      setDetectedModels(result.models || []);
      if (result.success && result.models?.length > 0) {
        // Optionally merge detected models into the form
      }
    } catch (error: any) {
      setDetectedModels([]);
    } finally { setDetecting(false); }
  };

  const importDetectedModel = (model: any) => {
    const exists = providerForm.models.some(m => m.id === model.id);
    if (!exists) {
      setProviderForm({
        ...providerForm,
        models: [...providerForm.models, { id: model.id, name: model.name || model.id, max_tokens: 4096, supports_thinking: false }],
      });
    }
  };

  // ========= Prompt =========
  const openAddPrompt = () => { setEditingPromptId(null); setPromptForm({ id: "", name: "", description: "", prompt: "" }); setPromptError(""); setPromptDialog(true); };
  const openEditPrompt = (p: BehaviorPrompt) => { setEditingPromptId(p.id); setPromptForm({ id: p.id, name: p.name || "", description: p.description || "", prompt: p.prompt || "" }); setPromptError(""); setPromptDialog(true); };

  const handleSavePrompt = async () => {
    setPromptError("");
    if (!promptForm.id.trim()) { setPromptError("ID不能为空"); return; }
    if (!promptForm.name.trim()) { setPromptError("名称不能为空"); return; }
    setPromptSaving(true);
    try {
      const data = { id: promptForm.id.trim(), name: promptForm.name.trim(), description: promptForm.description.trim(), prompt: promptForm.prompt.trim() };
      if (editingPromptId) { await behaviorPromptsApi.update(editingPromptId, data as any); }
      else { await behaviorPromptsApi.create(data as any); }
      setPromptDialog(false);
      await loadData();
    } catch (error: any) {
      setPromptError(error?.response?.data?.detail || error?.message || "保存失败");
    } finally { setPromptSaving(false); }
  };

  const handleDeletePrompt = (id: string, name: string) => { setDeleteTarget({ type: "prompt", id, name }); setDeleteDialog(true); };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      if (deleteTarget.type === "provider") { await providersApi.delete(deleteTarget.id); }
      else { await behaviorPromptsApi.delete(deleteTarget.id); }
      setDeleteDialog(false); setDeleteTarget(null); await loadData();
    } catch (error: any) { alert(`删除失败: ${error?.message || "未知错误"}`); }
  };

  const getThinkingInfo = (p: Provider) => {
    const tc = p.thinking_config || DEFAULT_TC;
    if (tc.mode === "toggle") return "开关模式";
    if (tc.mode === "effort") return `强度: ${tc.effort_values?.join("/")}`;
    if (tc.mode === "effort_only") return `强度: ${tc.effort_values?.join("/")}`;
    return "不支持";
  };

  return (
    <div className="container mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">系统配置</h2>
        <p className="text-gray-500 mt-1">管理LLM配置和行为提示词</p>
      </div>

      <Tabs defaultValue="providers">
        <TabsList>
          <TabsTrigger value="providers">LLM配置</TabsTrigger>
          <TabsTrigger value="prompts">行为提示词</TabsTrigger>
        </TabsList>

        <TabsContent value="providers" className="mt-6">
          {/* Preset selector + Add button */}
          <div className="flex items-center gap-3 mb-4 flex-wrap">
            <h3 className="text-lg font-semibold">LLM Provider配置</h3>
            <div className="flex-1" />
            <div className="flex gap-2 flex-wrap">
              {PRESETS.map(p => (
                <Button key={p.name} size="sm" variant="outline" onClick={() => openAddProvider(p.name)}>
                  {p.icon} {p.label}
                </Button>
              ))}
              <Button size="sm" onClick={() => openAddProvider()}>
                <Plus className="w-4 h-4 mr-1" />自定义
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" /></div>
          ) : providers.length === 0 ? (
            <Card><CardContent className="py-8 text-center">
              <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">暂无Provider配置，点击上方预设或自定义添加</p>
            </CardContent></Card>
          ) : (
            <div className="grid gap-4">
              {providers.map((provider) => (
                <Card key={provider.name}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-lg">{provider.name}</h4>
                          <Badge variant="outline" className="text-xs">{getThinkingInfo(provider)}</Badge>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{provider.base_url}</p>
                        <p className="text-xs text-gray-400">默认模型: {provider.default_model}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {provider.models?.map((model) => (
                            <Badge key={model.id} variant="secondary" className="flex gap-1">
                              {model.name}
                              {model.supports_thinking && <span title="支持思考模式">🧠</span>}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2 shrink-0">
                        <Button size="sm" variant="outline" onClick={() => openEditProvider(provider)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => handleDeleteProvider(provider.name)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="prompts" className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">行为提示词管理</h3>
            <Button onClick={openAddPrompt}><Plus className="w-4 h-4 mr-2" />添加提示词</Button>
          </div>
          {loading ? (
            <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" /></div>
          ) : behaviorPrompts.length === 0 ? (
            <Card><CardContent className="py-8 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">暂无行为提示词</p>
              <Button onClick={openAddPrompt}>添加第一个提示词</Button>
            </CardContent></Card>
          ) : (
            <div className="grid gap-4">
              {behaviorPrompts.map((prompt) => (
                <Card key={prompt.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold">{prompt.name}</h4>
                        <p className="text-xs text-gray-400">ID: {prompt.id}</p>
                        <p className="text-sm text-gray-500 mt-1">{prompt.description}</p>
                        <p className="text-sm text-gray-400 mt-2 line-clamp-3 whitespace-pre-wrap">{prompt.prompt}</p>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => openEditPrompt(prompt)}><Edit className="w-4 h-4" /></Button>
                        <Button size="sm" variant="ghost" onClick={() => handleDeletePrompt(prompt.id, prompt.name)}><Trash2 className="w-4 h-4 text-red-500" /></Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Provider Dialog */}
      <Dialog open={providerDialog} onOpenChange={setProviderDialog}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingProvider ? "编辑Provider" : "添加Provider"}</DialogTitle>
            <DialogDescription>配置LLM API连接信息。选择预设可快速填充，也可直接编辑。</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Provider名称 *</Label>
                <Input value={providerForm.name} onChange={e => setProviderForm({ ...providerForm, name: e.target.value })} disabled={!!editingProvider} placeholder="OpenAI" />
              </div>
              <div>
                <Label>默认模型</Label>
                <Input value={providerForm.default_model} onChange={e => setProviderForm({ ...providerForm, default_model: e.target.value })} placeholder="gpt-4o-mini" />
              </div>
            </div>
            <div>
              <Label>API Base URL *</Label>
              <Input value={providerForm.base_url} onChange={e => setProviderForm({ ...providerForm, base_url: e.target.value })} placeholder="https://api.openai.com/v1" />
            </div>
            <div>
              <Label>API Key *</Label>
              <Input type="password" value={providerForm.api_key} onChange={e => setProviderForm({ ...providerForm, api_key: e.target.value })} placeholder={editingProvider ? "留空则不修改" : "sk-..."} />
            </div>

            {/* Model Editor */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>模型列表</Label>
                <div className="flex gap-2">
                  <Button type="button" size="sm" variant="outline" onClick={handleDetectModels} disabled={detecting}>
                    <Search className="w-3 h-3 mr-1" />{detecting ? "检测中..." : "检测模型"}
                  </Button>
                  <Button type="button" size="sm" variant="outline" onClick={addModelRow}>
                    <Plus className="w-3 h-3 mr-1" />添加
                  </Button>
                </div>
              </div>
              <div className="space-y-2 border rounded-lg p-3 max-h-64 overflow-y-auto">
                {providerForm.models.length === 0 && (
                  <p className="text-sm text-gray-400 text-center py-4">暂无模型，点击"添加"或"检测模型"</p>
                )}
                {providerForm.models.map((m, i) => (
                  <div key={i} className="flex items-center gap-2 bg-gray-50 rounded p-2">
                    <Input className="flex-1" size={8} value={m.id} onChange={e => updateModelRow(i, "id", e.target.value)} placeholder="model-id" />
                    <Input className="w-20" value={m.max_tokens} type="number" onChange={e => updateModelRow(i, "max_tokens", +e.target.value)} />
                    <div className="flex items-center gap-1 shrink-0">
                      <Label className="text-xs whitespace-nowrap">思考</Label>
                      <Switch checked={m.supports_thinking || false} onCheckedChange={v => updateModelRow(i, "supports_thinking", v)} />
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => removeModelRow(i)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Detected Models */}
            {detectedModels !== null && (
              <div className="border rounded-lg p-3 max-h-40 overflow-y-auto">
                <p className="text-sm font-medium mb-2">检测到 {detectedModels.length} 个模型</p>
                {detectedModels.slice(0, 20).map((m: any) => (
                  <div key={m.id} className="flex items-center justify-between text-sm py-1 border-b last:border-0">
                    <span>{m.id}</span>
                    <Button size="sm" variant="ghost" onClick={() => importDetectedModel(m)}>
                      <Plus className="w-3 h-3" /> 导入
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Test Connect */}
            <div>
              <Button type="button" variant="outline" onClick={handleTestConnect} disabled={testing} className="w-full">
                <Zap className="w-4 h-4 mr-2" />{testing ? "测试中..." : "测试连通性"}
              </Button>
              {testResult && (
                <div className={`mt-2 p-3 rounded-lg text-sm ${testResult.success ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"}`}>
                  {testResult.success ? (
                    <p>✅ 连通成功！延迟 {testResult.latency_ms}ms，模型: {testResult.model}</p>
                  ) : (
                    <p>❌ {testResult.error || `HTTP ${testResult.status_code}`}</p>
                  )}
                </div>
              )}
            </div>

            {providerError && <p className="text-sm text-red-500">{providerError}</p>}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setProviderDialog(false)}>取消</Button>
            <Button onClick={handleSaveProvider} disabled={providerSaving}>{providerSaving ? "保存中..." : "保存"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Prompt Dialog */}
      <Dialog open={promptDialog} onOpenChange={setPromptDialog}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingPromptId ? "编辑行为提示词" : "添加行为提示词"}</DialogTitle>
            <DialogDescription>配置Agent的行为风格提示词模板。</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div><Label>ID *</Label><Input value={promptForm.id} onChange={e => setPromptForm({ ...promptForm, id: e.target.value })} disabled={!!editingPromptId} placeholder="neutral" /></div>
            <div><Label>名称 *</Label><Input value={promptForm.name} onChange={e => setPromptForm({ ...promptForm, name: e.target.value })} placeholder="中立风格" /></div>
            <div><Label>描述</Label><Input value={promptForm.description} onChange={e => setPromptForm({ ...promptForm, description: e.target.value })} placeholder="简短描述" /></div>
            <div><Label>提示词内容</Label><Textarea value={promptForm.prompt} onChange={e => setPromptForm({ ...promptForm, prompt: e.target.value })} rows={6} placeholder="你是一个..." /></div>
            {promptError && <p className="text-sm text-red-500">{promptError}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPromptDialog(false)}>取消</Button>
            <Button onClick={handleSavePrompt} disabled={promptSaving}>{promptSaving ? "保存中..." : "保存"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除{deleteTarget?.type === "provider" ? "Provider" : "行为提示词"}「{deleteTarget?.name}」吗？
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog(false)}>取消</Button>
            <Button variant="destructive" onClick={confirmDelete}>确认删除</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
