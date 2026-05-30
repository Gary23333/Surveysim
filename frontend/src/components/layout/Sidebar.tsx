import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ListTodo,
  PlusCircle,
  FileText,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const menuItems = [
  {
    title: "任务管理",
    items: [
      {
        label: "任务列表",
        icon: ListTodo,
        href: "/tasks",
      },
      {
        label: "创建任务",
        icon: PlusCircle,
        href: "/tasks/create",
      },
    ],
  },
  {
    title: "配置管理",
    items: [
      {
        label: "问卷管理",
        icon: FileText,
        href: "/surveys",
      },
      {
        label: "人格管理",
        icon: Users,
        href: "/personas",
      },
      {
        label: "系统配置",
        icon: Settings,
        href: "/config",
      },
    ],
  },
];

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation();

  return (
    <div
      className={cn(
        "bg-white border-r border-gray-200 transition-all duration-300 flex flex-col",
        isOpen ? "w-64" : "w-16"
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        {isOpen && (
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-gray-900">Virtual Survey</span>
          </Link>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* 菜单 */}
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((section, sectionIndex) => (
          <div key={sectionIndex} className="mb-6">
            {isOpen && (
              <div className="px-4 mb-2">
                <span className="text-xs font-semibold text-gray-400 uppercase">
                  {section.title}
                </span>
              </div>
            )}
            <div className="space-y-1 px-2">
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;

                return (
                  <Link
                    key={itemIndex}
                    to={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                      isActive
                        ? "bg-blue-50 text-blue-700"
                        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                    )}
                  >
                    <Icon
                      className={cn(
                        "w-5 h-5 flex-shrink-0",
                        isActive ? "text-blue-700" : "text-gray-400"
                      )}
                    />
                    {isOpen && <span className="text-sm font-medium">{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* 底部 */}
      <div className="p-4 border-t border-gray-200">
        {isOpen && (
          <div className="text-xs text-gray-400">
            Virtual Survey v0.3.0
          </div>
        )}
      </div>
    </div>
  );
}
