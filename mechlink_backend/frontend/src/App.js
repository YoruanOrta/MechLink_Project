import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import RegisterVehicle from "./Vehicles/RegisterVehicle";
import ViewVehicles from "./Vehicles/ViewVehicles";
import BookAppointment from "./appointments/BookAppointment"; 
import MyAppointments from "./appointments/MyAppointments";
import MaintenanceLogs from "./pages/MaintenanceLogs";
import NotificationsPage from "./pages/NotificationsPage";
import "./styles/App.css";
import SearchMechanics from './pages/SearchMechanics';
import MyServices from "./pages/MyServices";
import Favorites from './pages/Favorites';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/vehicles/register" element={<RegisterVehicle />} />
        <Route path="/vehicles" element={<ViewVehicles />} />
        <Route path="/appointments/book" element={<BookAppointment />} />
        <Route path="/appointments" element={<MyAppointments />} />
        <Route path="/maintenance/logs" element={<MaintenanceLogs />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/search" element={<SearchMechanics />} />
        <Route path="/my-services" element={<MyServices />} />
        <Route path="/favorites" element={<Favorites />} />
      </Routes>
    </Router>
  );
}

export default App;
