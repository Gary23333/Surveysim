import { useLocation } from "react-router-dom";
import { Bell, Search } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/": "任务列表",
  "/tasks": "任务列表",
  "/tasks/create": "创建任务",
  "/surveys": "问卷管理",
  "/personas": "人格管理",
  "/config": "系统配置",
};

export default function Header() {
  const location = useLocation();

  // 获取页面标题
  const getPageTitle = () => {
    // 检查是否是Dashboard页面
    if (location.pathname.includes("/dashboard")) {
      return "调研看板";
    }
    return pageTitles[location.pathname] || "Virtual Survey";
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-lg font-semibold text-gray-900">{getPageTitle()}</h1>
      </div>

      {/* 右侧操作 */}
      <div className="flex items-center gap-4">
        {/* 搜索 */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索..."
            className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* 通知 */}
        <button className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <Bell className="w-5 h-5 text-gray-500" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* 用户头像 */}
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-medium">U</span>
        </div>
      </div>
    </header>
  );
}
