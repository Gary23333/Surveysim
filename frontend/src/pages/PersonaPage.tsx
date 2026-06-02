import { useState, useEffect } from "react";
import { personasApi } from "@/api/personas";
import { providersApi } from "@/api/providers";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogDescription,
  DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Edit, Trash2, Wand2, Layers } from "lucide-react";
import type { Persona, PersonaSummary, PersonaTemplate, PersonaGroup, Provider } from "@/types";

export default function PersonaPage() {
  const [personas, setPersonas] = useState<PersonaSummary[]>([]);
  const [templates, setTemplates] = useState<PersonaTemplate[]>([]);
  const [groups, setGroups] = useState<PersonaGroup[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeGroupId, setActiveGroupId] = useState<string | null>(null);

  // Optimizer
  const [showOptimizer, setShowOptimizer] = useState(false);
  const [targetDescription, setTargetDescription] = useState("");
  const [optimizeProvider, setOptimizeProvider] = useState("DeepSeek");
  const [optimizeModel, setOptimizeModel] = useState("deepseek-v4-pro");
  const [optimizing, setOptimizing] = useState(false);
  const [optimizedResult, setOptimizedResult] = useState<any>(null);

  // Detail dialog
  const [showDetail, setShowDetail] = useState(false);
  const [detailPersona, setDetailPersona] = useState<Persona | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Edit dialog
  const [showEditor, setShowEditor] = useState(false);
  const [editPersonaId, setEditPersonaId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Persona>>({});
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState("");

  // Optimizer target
  const [optimizeTargetId, setOptimizeTargetId] = useState<string | null>(null);
  const [optimizeTargetName, setOptimizeTargetName] = useState<string>("");

  // Group dialog
  const [groupDialog, setGroupDialog] = useState(false);
  const [editingGroupId, setEditingGroupId] = useState<string | null>(null);
  const [groupForm, setGroupForm] = useState({ name: "", description: "", persona_ids: [] as string[] });
  const [groupSaving, setGroupSaving] = useState(false);
  const [groupError, setGroupError] = useState("");

  // Delete
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: "persona" | "group"; id: string; name: string } | null>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // 核心数据并行加载（providers 独立加载，不阻塞 personas）
      const [personasData, templatesData, groupsData] = await Promise.all([
        personasApi.list(), personasApi.listTemplates(), personasApi.listGroups(),
      ]);
      setPersonas(personasData);
      setTemplates(templatesData);
      setGroups(groupsData);
    } catch (error) { console.error("Failed to load data:", error); }

    // providers 独立加载，失败不影响主数据
    try {
      const providersData = await providersApi.list();
      setProviders(providersData);
    } catch (error) { console.error("Failed to load providers:", error); }
    finally { setLoading(false); }
  };

  const activeGroup = groups.find(g => g.id === activeGroupId);
  const filteredPersonas = activeGroupId
    ? personas.filter(p => activeGroup?.persona_ids.includes(p.id))
    : personas;

  // ===== Detail =====
  const openDetail = async (personaId: string) => {
    setDetailLoading(true);
    setShowDetail(true);
    try {
      const data = await personasApi.get(personaId);
      setDetailPersona(data);
    } catch (error) { console.error("Failed to load detail:", error); }
    finally { setDetailLoading(false); }
  };

  // ===== Edit =====
  const openEdit = async (personaId: string) => {
    setEditError("");
    try {
      const data = await personasApi.get(personaId);
      setEditPersonaId(personaId);
      setEditForm(data);
      setShowEditor(true);
    } catch (error) { console.error("Failed to load for edit:", error); }
  };

  const saveEdit = async () => {
    if (!editPersonaId || !editForm.name?.trim()) return;
    setEditSaving(true);
    setEditError("");
    try {
      await personasApi.update(editPersonaId, editForm as any);
      setShowEditor(false);
      setDetailPersona(null);
      await loadData();
    } catch (error: any) {
      setEditError(error?.response?.data?.detail || error?.message || "保存失败");
    } finally { setEditSaving(false); }
  };

  // ===== Optimize =====
  const handleOptimize = async () => {
    if (!targetDescription.trim()) return;
    setOptimizing(true);
    try {
      const result = await personasApi.optimize({
        target_description: targetDescription,
        provider_pack: optimizeProvider,
        model: optimizeModel,
        ...(optimizeTargetId ? { persona_id: optimizeTargetId } : {}),
      });
      setOptimizedResult(result);
    } catch (error) { console.error("Failed:", error); }
    finally { setOptimizing(false); }
  };

  const saveOptimized = async () => {
    if (!optimizedResult) return;
    if (optimizeTargetId) {
      await personasApi.update(optimizeTargetId, optimizedResult);
    } else {
      await personasApi.create(optimizedResult);
    }
    setShowOptimizer(false); setOptimizedResult(null); setTargetDescription("");
    setOptimizeTargetId(null); setOptimizeTargetName("");
    loadData();
  };

  // ===== Delete =====
  const handleDeletePersona = (personaId: string, name: string) => {
    setDeleteTarget({ type: "persona", id: personaId, name });
    setDeleteDialog(true);
  };
  const confirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      if (deleteTarget.type === "persona") await personasApi.delete(deleteTarget.id);
      else await personasApi.deleteGroup(deleteTarget.id);
      setDeleteDialog(false); setDeleteTarget(null); await loadData();
    } catch (error: any) { alert(`删除失败: ${error?.message || "未知错误"}`); }
  };

  // ===== Group =====
  const openAddGroup = () => { setEditingGroupId(null); setGroupForm({ name: "", description: "", persona_ids: [] }); setGroupError(""); setGroupDialog(true); };
  const openEditGroup = (g: PersonaGroup) => { setEditingGroupId(g.id); setGroupForm({ name: g.name, description: g.description || "", persona_ids: g.persona_ids || [] }); setGroupError(""); setGroupDialog(true); };
  const togglePersonaInGroup = (pid: string) => setGroupForm(prev => ({
    ...prev, persona_ids: prev.persona_ids.includes(pid) ? prev.persona_ids.filter(id => id !== pid) : [...prev.persona_ids, pid],
  }));
  const saveGroup = async () => {
    if (!groupForm.name.trim()) { setGroupError("名称不能为空"); return; }
    setGroupSaving(true);
    try {
      if (editingGroupId) await personasApi.updateGroup(editingGroupId, groupForm);
      else await personasApi.createGroup(groupForm);
      setGroupDialog(false); await loadData();
    } catch (error: any) { setGroupError(error?.response?.data?.detail || error?.message || "保存失败"); }
    finally { setGroupSaving(false); }
  };
  const handleDeleteGroup = (groupId: string, name: string) => { setDeleteTarget({ type: "group", id: groupId, name }); setDeleteDialog(true); };

  const selProv = providers.find(p => p.name === optimizeProvider);

  return (
    <div className="container mx-auto">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">人格管理</h2>
          <p className="text-gray-500 text-sm mt-1">{personas.length} 个人格 · {groups.length} 个分组</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => { setOptimizeTargetId(null); setOptimizeTargetName(""); setOptimizedResult(null); setTargetDescription(""); setShowOptimizer(true); }}>
            <Wand2 className="w-4 h-4 mr-2" />AI生成人格
          </Button>
          <Button variant="outline" onClick={openAddGroup}>
            <Layers className="w-4 h-4 mr-2" />创建分组
          </Button>
        </div>
      </div>

      {/* Group tabs — quick switching */}
      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
        <Badge
          variant={!activeGroupId ? "default" : "outline"}
          className="cursor-pointer px-3 py-1.5 text-sm shrink-0"
          onClick={() => setActiveGroupId(null)}
        >
          全部 ({personas.length})
        </Badge>
        {groups.map(g => (
          <Badge
            key={g.id}
            variant={activeGroupId === g.id ? "default" : "outline"}
            className="cursor-pointer px-3 py-1.5 text-sm shrink-0 flex items-center gap-1"
            onClick={() => setActiveGroupId(g.id)}
          >
            {g.name} ({g.persona_ids?.length || 0})
            <span className="opacity-50 hover:opacity-100" onClick={(e) => { e.stopPropagation(); openEditGroup(g); }}>
              <Edit className="w-3 h-3" />
            </span>
          </Badge>
        ))}
      </div>

      {/* Persona grid */}
      {loading ? (
        <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" /></div>
      ) : filteredPersonas.length === 0 ? (
        <Card><CardContent className="py-8 text-center text-gray-500">
          {activeGroupId ? "此分组暂无成员" : "暂无自定义人格，请从模板创建或通过LLM优化生成"}
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {filteredPersonas.map((persona) => (
            <Card key={persona.id} className="hover:shadow-md transition-shadow cursor-pointer group" onClick={() => openDetail(persona.id)}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-lg font-bold text-blue-600 shrink-0">
                    {persona.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold">{persona.name}</h4>
                    <p className="text-sm text-gray-500">{persona.occupation} · {persona.age}岁 · {persona.city}</p>
                    <p className="text-xs text-gray-400">{persona.gender}</p>
                  </div>
                </div>
                {persona.groups && persona.groups.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {persona.groups.map((g: string) => (
                      <Badge key={g} variant="outline" className="text-xs bg-blue-50 text-blue-700 py-0">{g}</Badge>
                    ))}
                  </div>
                )}
                <div className="flex justify-end gap-1 mt-3 pt-2 border-t opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); setOptimizeTargetId(persona.id); setOptimizeTargetName(persona.name); setOptimizedResult(null); setTargetDescription(""); setShowOptimizer(true); }}>
                    <Wand2 className="w-3 h-3 text-purple-500" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); openEdit(persona.id); }}>
                    <Edit className="w-3 h-3" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); handleDeletePersona(persona.id, persona.name); }}>
                    <Trash2 className="w-3 h-3 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Templates */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">人格模板</h3>
        <div className="grid grid-cols-6 gap-3">
          {templates.map((template) => (
            <Card key={template.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={async () => { await personasApi.fromTemplate(template.id); loadData(); }}>
              <CardContent className="p-3 text-center">
                <span className="text-2xl">{template.emoji}</span>
                <h4 className="font-medium text-sm mt-1">{template.name}</h4>
                <p className="text-xs text-gray-500">{template.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* ====== Detail Dialog ====== */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          {detailLoading ? (
            <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" /></div>
          ) : detailPersona ? (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-lg font-bold text-blue-600">
                    {detailPersona.name.charAt(0)}
                  </div>
                  {detailPersona.name}
                </DialogTitle>
                <DialogDescription>
                  {detailPersona.demographics?.occupation} · {detailPersona.demographics?.age}岁 · {detailPersona.demographics?.city}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3 py-2 text-sm">
                <div>
                  <Label className="text-xs text-gray-400">人口统计</Label>
                  <div className="grid grid-cols-3 gap-1 mt-1">
                    {Object.entries(detailPersona.demographics || {}).filter(([,v]) => v).map(([k, v]) => (
                      <span key={k} className="bg-gray-50 rounded px-2 py-1 text-xs">{k}: {String(v)}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-xs text-gray-400">性格特征</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {detailPersona.psychographics?.personality_traits?.map((t: string) => (
                      <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>
                    ))}
                    {detailPersona.psychographics?.values?.map((t: string) => (
                      <Badge key={t} variant="outline" className="text-xs">{t}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-xs text-gray-400">技术/风险偏好</Label>
                  <p className="text-xs mt-1">技术: {detailPersona.psychographics?.tech_savviness} · 风险: {detailPersona.psychographics?.risk_appetite}</p>
                </div>
                <div>
                  <Label className="text-xs text-gray-400">背景故事</Label>
                  <p className="text-xs text-gray-600 mt-1 whitespace-pre-wrap">{detailPersona.background?.life_story}</p>
                </div>
                <div>
                  <Label className="text-xs text-gray-400">关键经历</Label>
                  <ul className="list-disc list-inside text-xs text-gray-600">
                    {detailPersona.background?.key_experiences?.map((e: string, i: number) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <Label className="text-xs text-gray-400">当前关注</Label>
                  <ul className="list-disc list-inside text-xs text-gray-600">
                    {detailPersona.background?.current_concerns?.map((c: string, i: number) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
                {detailPersona.initial_attitudes && Object.keys(detailPersona.initial_attitudes).length > 0 && (
                  <div>
                    <Label className="text-xs text-gray-400">初始态度</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {Object.entries(detailPersona.initial_attitudes).map(([k, v]) => (
                        <Badge key={k} variant="outline" className="text-xs">{k}: {String(v)}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {detailPersona.groups && detailPersona.groups.length > 0 && (
                  <div>
                    <Label className="text-xs text-gray-400">所属分组</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {detailPersona.groups.map((g: string) => (
                        <Badge key={g} className="text-xs bg-blue-50 text-blue-700">{g}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowDetail(false)}>关闭</Button>
                <Button onClick={() => { setShowDetail(false); openEdit(detailPersona.id); }}>编辑</Button>
              </DialogFooter>
            </>
          ) : (
            <p className="text-center text-gray-500 py-8">加载失败</p>
          )}
        </DialogContent>
      </Dialog>

      {/* ====== Edit Dialog ====== */}
      <Dialog open={showEditor} onOpenChange={setShowEditor}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>编辑人格 — {editForm.name}</DialogTitle>
            <DialogDescription>修改人格的各项属性。</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div><Label>名称</Label><Input value={editForm.name || ""} onChange={e => setEditForm({ ...editForm, name: e.target.value })} /></div>
            <div className="grid grid-cols-3 gap-2">
              <div><Label>年龄</Label><Input type="number" value={editForm.demographics?.age || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, age: +e.target.value } })} /></div>
              <div><Label>性别</Label><Input value={editForm.demographics?.gender || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, gender: e.target.value } })} /></div>
              <div><Label>城市</Label><Input value={editForm.demographics?.city || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, city: e.target.value } })} /></div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div><Label>教育</Label><Input value={editForm.demographics?.education || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, education: e.target.value } })} /></div>
              <div><Label>职业</Label><Input value={editForm.demographics?.occupation || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, occupation: e.target.value } })} /></div>
              <div><Label>收入</Label><Input value={editForm.demographics?.income || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, income: e.target.value } })} /></div>
              <div><Label>婚姻</Label><Input value={editForm.demographics?.marital_status || ""} onChange={e => setEditForm({ ...editForm, demographics: { ...editForm.demographics as any, marital_status: e.target.value } })} /></div>
            </div>
            <div>
              <Label>背景故事</Label>
              <Textarea rows={3} value={editForm.background?.life_story || ""} onChange={e => setEditForm({ ...editForm, background: { ...editForm.background as any, life_story: e.target.value } })} />
            </div>
            <div>
              <Label>关键经历（每行一条）</Label>
              <Textarea rows={3} value={(editForm.background?.key_experiences || []).join("\n")} onChange={e => setEditForm({ ...editForm, background: { ...editForm.background as any, key_experiences: e.target.value.split("\n").filter(Boolean) } })} />
            </div>
            <div>
              <Label>当前关注（每行一条）</Label>
              <Textarea rows={3} value={(editForm.background?.current_concerns || []).join("\n")} onChange={e => setEditForm({ ...editForm, background: { ...editForm.background as any, current_concerns: e.target.value.split("\n").filter(Boolean) } })} />
            </div>
            <div>
              <Label>性格特征（逗号分隔）</Label>
              <Input value={(editForm.psychographics?.personality_traits || []).join(", ")} onChange={e => setEditForm({ ...editForm, psychographics: { ...editForm.psychographics as any, personality_traits: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) } })} />
            </div>
            <div>
              <Label>核心价值观（逗号分隔）</Label>
              <Input value={(editForm.psychographics?.values || []).join(", ")} onChange={e => setEditForm({ ...editForm, psychographics: { ...editForm.psychographics as any, values: e.target.value.split(",").map((s: string) => s.trim()).filter(Boolean) } })} />
            </div>
            {editError && <p className="text-sm text-red-500">{editError}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditor(false)}>取消</Button>
            <Button onClick={saveEdit} disabled={editSaving}>{editSaving ? "保存中..." : "保存"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ====== Optimize Dialog ====== */}
      <Dialog open={showOptimizer} onOpenChange={setShowOptimizer}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader><DialogTitle>LLM 优化生成人格</DialogTitle></DialogHeader>
          <div className="space-y-3 py-2">
            {optimizeTargetId ? (
              <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg text-sm text-purple-700">
                <Wand2 className="w-4 h-4" />
                正在基于 <span className="font-semibold">「{optimizeTargetName}」</span> 进行优化调整
              </div>
            ) : (
              <p className="text-sm text-gray-500">根据目标人群描述，从模板生成新的人格</p>
            )}
            <div>
              <Label>优化使用的 LLM</Label>
              <div className="grid grid-cols-2 gap-2">
                <Select value={optimizeProvider} onValueChange={v => { setOptimizeProvider(v); const p = providers.find(pp => pp.name === v); if (p) setOptimizeModel(p.default_model || p.models?.[0]?.id || ""); }}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{providers.map(p => <SelectItem key={p.name} value={p.name}>{p.name}</SelectItem>)}</SelectContent>
                </Select>
                <Select value={optimizeModel} onValueChange={setOptimizeModel}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {(selProv?.models || []).map(m => <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>目标人群描述</Label>
              <Textarea value={targetDescription} onChange={(e) => setTargetDescription(e.target.value)} placeholder="描述你想要的人群特征，例如：随迁老人、小镇青年、海归精英..." rows={4} />
            </div>
            <Button onClick={handleOptimize} disabled={!targetDescription.trim() || optimizing} className="w-full">
              {optimizing ? "优化中..." : "开始优化"}
            </Button>
            {optimizedResult && (
              <div className="space-y-3 border rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-xl font-bold text-blue-600">{optimizedResult.name?.charAt(0)}</div>
                  <div><h4 className="font-medium">{optimizedResult.name}</h4>
                    <p className="text-sm text-gray-500">{optimizedResult.demographics?.occupation} · {optimizedResult.demographics?.age}岁</p>
                  </div>
                </div>
                <p className="text-xs text-gray-600">{optimizedResult.background?.life_story}</p>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" size="sm" onClick={handleOptimize}>重新优化</Button>
                  <Button size="sm" onClick={saveOptimized}>保存人格</Button>
                </div>
              </div>
            )}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => { setShowOptimizer(false); setOptimizedResult(null); }}>关闭</Button></DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ====== Group Dialog ====== */}
      <Dialog open={groupDialog} onOpenChange={setGroupDialog}>
        <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader><DialogTitle>{editingGroupId ? "编辑分组" : "创建分组"}</DialogTitle></DialogHeader>
          <div className="space-y-3 py-2">
            <div><Label>分组名称 *</Label><Input value={groupForm.name} onChange={e => setGroupForm({ ...groupForm, name: e.target.value })} /></div>
            <div><Label>描述</Label><Input value={groupForm.description} onChange={e => setGroupForm({ ...groupForm, description: e.target.value })} /></div>
            <div>
              <Label>选择人格成员</Label>
              <div className="border rounded-lg max-h-56 overflow-y-auto divide-y">
                {personas.length === 0 ? <p className="text-sm text-gray-400 text-center py-4">暂无可用人格</p> :
                  personas.map(p => (
                    <div key={p.id} className="flex items-center gap-3 px-3 py-2 hover:bg-gray-50">
                      <Switch checked={groupForm.persona_ids.includes(p.id)} onCheckedChange={() => togglePersonaInGroup(p.id)} />
                      <span className="text-sm font-medium">{p.name}</span>
                      <span className="text-xs text-gray-500">{p.occupation}</span>
                    </div>
                  ))}
              </div>
            </div>
            {groupError && <p className="text-sm text-red-500">{groupError}</p>}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGroupDialog(false)}>取消</Button>
            {editingGroupId && <Button variant="destructive" onClick={() => { handleDeleteGroup(editingGroupId, groupForm.name || editingGroupId); setGroupDialog(false); }}>删除</Button>}
            <Button onClick={saveGroup} disabled={groupSaving}>{groupSaving ? "保存中..." : "保存"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirm */}
      <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>确认删除</DialogTitle><DialogDescription>确定删除「{deleteTarget?.name}」？</DialogDescription></DialogHeader>
          <DialogFooter><Button variant="outline" onClick={() => setDeleteDialog(false)}>取消</Button><Button variant="destructive" onClick={confirmDelete}>删除</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
