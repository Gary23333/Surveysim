import { Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import DashboardPage from "./pages/DashboardPage";
import TaskListPage from "./pages/TaskListPage";
import TaskCreatePage from "./pages/TaskCreatePage";
import ResultPage from "./pages/ResultPage";
import SurveyPage from "./pages/SurveyPage";
import PersonaPage from "./pages/PersonaPage";
import ConfigPage from "./pages/ConfigPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<TaskListPage />} />
        <Route path="tasks" element={<TaskListPage />} />
        <Route path="tasks/create" element={<TaskCreatePage />} />
        <Route path="tasks/:taskId/dashboard" element={<DashboardPage />} />
        <Route path="tasks/:taskId/results" element={<ResultPage />} />
        <Route path="surveys" element={<SurveyPage />} />
        <Route path="personas" element={<PersonaPage />} />
        <Route path="config" element={<ConfigPage />} />
      </Route>
    </Routes>
  );
}

export default App;
