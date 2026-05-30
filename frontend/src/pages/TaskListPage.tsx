import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTaskStore } from "@/stores/taskStore";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Eye, Play, Pause, Square, Trash2, Plus } from "lucide-react";
import { formatDate } from "@/lib/utils";
import type { TaskStatus, ScenarioType } from "@/types";

const statusColors: Record<TaskStatus, string> = {
  pending: "bg-gray-100 text-gray-800",
  running: "bg-blue-100 text-blue-800",
  paused: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
  stopped: "bg-orange-100 text-orange-800",
};

const statusLabels: Record<TaskStatus, string> = {
  pending: "待启动",
  running: "运行中",
  paused: "已暂停",
  completed: "已完成",
  error: "错误",
  stopped: "已停止",
};

const scenarioLabels: Record<ScenarioType, string> = {
  survey: "问卷调查",
  focus_group: "焦点小组",
  idi: "深度访谈",
  debate: "辩论讨论",
};

const scenarioEmojis: Record<ScenarioType, string> = {
  survey: "📋",
  focus_group: "👥",
  idi: "🎙️",
  debate: "⚖️",
};

export default function TaskListPage() {
  const navigate = useNavigate();
  const { tasks, loading, fetchTasks, startTask, pauseTask, resumeTask, stopTask, deleteTask } = useTaskStore();
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filteredTasks = filter === "all"
    ? tasks
    : tasks.filter((t) => t.status === filter);

  const handleStart = async (taskId: string) => {
    await startTask(taskId);
    navigate(`/tasks/${taskId}/dashboard`);
  };

  const handlePause = async (taskId: string) => {
    await pauseTask(taskId);
  };

  const handleResume = async (taskId: string) => {
    await resumeTask(taskId);
  };

  const handleStop = async (taskId: string) => {
    await stopTask(taskId);
  };

  const handleDelete = async (taskId: string) => {
    if (confirm("确定要删除这个任务吗？")) {
      await deleteTask(taskId);
    }
  };

  return (
    <div className="container mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">任务列表</h2>
          <p className="text-gray-500 mt-1">管理您的调研任务</p>
        </div>
        <Link to="/tasks/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            创建任务
          </Button>
        </Link>
      </div>

      {/* 过滤器 */}
      <div className="flex gap-2 mb-6">
        {["all", "pending", "running", "paused", "completed"].map((status) => (
          <Button
            key={status}
            variant={filter === status ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(status)}
          >
            {status === "all" ? "全部" : statusLabels[status as TaskStatus]}
          </Button>
        ))}
      </div>

      {/* 任务列表 */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">加载中...</p>
        </div>
      ) : filteredTasks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 mb-4">暂无任务</p>
            <Link to="/tasks/create">
              <Button>创建第一个任务</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredTasks.map((task) => (
            <Card key={task.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{scenarioEmojis[task.scenario_type]}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{task.name}</h3>
                        <p className="text-sm text-gray-500">
                          {scenarioLabels[task.scenario_type]} · {task.agent_count} 个参与者
                        </p>
                      </div>
                    </div>
                    {task.progress && task.status === "running" && (
                      <div className="mb-2">
                        <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                          <span>进度：第 {task.progress.current + 1}/{task.progress.total} 题</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-blue-600 h-1.5 rounded-full transition-all"
                            style={{ width: `${((task.progress.current || 0) / (task.progress.total || 1)) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                    {task.progress && task.status === "completed" && (
                      <p className="text-xs text-green-600 mb-2">已完成 {task.progress.total} 题</p>
                    )}
                    {task.agent_count && !task.progress && (
                      <p className="text-xs text-gray-400 mb-2">{task.agent_count} 位参与者待启动</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>创建于 {formatDate(task.created_at)}</span>
                      {task.started_at && (
                        <span>启动于 {formatDate(task.started_at)}</span>
                      )}
                      {task.completed_at && (
                        <span>完成于 {formatDate(task.completed_at)}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge className={statusColors[task.status]}>
                      {statusLabels[task.status]}
                    </Badge>

                    <div className="flex gap-1">
                      {task.status === "pending" && (
                        <Button
                          size="sm"
                          onClick={() => handleStart(task.id)}
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                      )}
                      {task.status === "running" && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handlePause(task.id)}
                          >
                            <Pause className="w-4 h-4" />
                          </Button>
                          <Link to={`/tasks/${task.id}/dashboard`}>
                            <Button size="sm" variant="outline">
                              <Eye className="w-4 h-4" />
                            </Button>
                          </Link>
                        </>
                      )}
                      {task.status === "paused" && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleResume(task.id)}
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleStop(task.id)}
                          >
                            <Square className="w-4 h-4" />
                          </Button>
                        </>
                      )}
                      {task.status === "completed" && (
                        <Link to={`/tasks/${task.id}/results`}>
                          <Button size="sm" variant="default" className="bg-green-600 hover:bg-green-700">
                            <ArrowRight className="w-4 h-4 mr-1" />查看结果
                          </Button>
                        </Link>
                      )}
                      {["pending", "completed", "stopped", "error"].includes(task.status) && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(task.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
