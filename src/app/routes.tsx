import { createBrowserRouter } from "react-router";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LandingPage } from "./pages/LandingPage";
import { Login } from "./pages/auth/Login";
import { Register } from "./pages/auth/Register";
import { ForgotPassword } from "./pages/auth/ForgotPassword";
import { DashboardLayout } from "./components/layouts/DashboardLayout";
import { Dashboard } from "./pages/dashboard/Dashboard";
import { SalesManagement } from "./pages/sales/SalesManagement";
import { AddSales } from "./pages/sales/AddSales";
import { SalesHistory } from "./pages/sales/SalesHistory";
import { WasteManagement } from "./pages/waste/WasteManagement";
import { WasteLogging } from "./pages/waste/WasteLogging";
import { WasteSimulation } from "./pages/waste/WasteSimulation";
import { Inventory } from "./pages/inventory/Inventory";
import { AIForecasting } from "./pages/ai/AIForecasting";
import { Recommendations } from "./pages/ai/Recommendations";
import { AnomalyDetection } from "./pages/ai/AnomalyDetection";
import { Reports } from "./pages/reports/Reports";
import { MLWorkflow } from "./pages/ml/MLWorkflow";
import { SystemArchitecture } from "./pages/system/SystemArchitecture";
import { NotFound } from "./pages/NotFound";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: LandingPage,
  },
  {
    path: "/login",
    Component: Login,
  },
  {
    path: "/register",
    Component: Register,
  },
  {
    path: "/forgot-password",
    Component: ForgotPassword,
  },
  {
    Component: ProtectedRoute,
    children: [
      {
        path: "/app",
        Component: DashboardLayout,
        children: [
          { index: true, Component: Dashboard },
          { path: "sales", Component: SalesManagement },
          { path: "sales/add", Component: AddSales },
          { path: "sales/history", Component: SalesHistory },
          { path: "waste", Component: WasteManagement },
          { path: "waste/log", Component: WasteLogging },
          { path: "waste/simulation", Component: WasteSimulation },
          { path: "inventory", Component: Inventory },
          { path: "ai/forecasting", Component: AIForecasting },
          { path: "ai/recommendations", Component: Recommendations },
          { path: "ai/anomaly-detection", Component: AnomalyDetection },
          { path: "reports", Component: Reports },
          { path: "ml-workflow", Component: MLWorkflow },
          { path: "architecture", Component: SystemArchitecture },
        ],
      },
    ],
  },
  {
    path: "*",
    Component: NotFound,
  },
]);
