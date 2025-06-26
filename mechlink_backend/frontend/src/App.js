import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Login";
import RegisterVehicle from "./Vehicles/RegisterVehicle";
import ViewVehicles from "./Vehicles/ViewVehicles";
import BookAppointment from "./appointments/BookAppointment";
import MyAppointments from "./appointments/MyAppointments";
import Dashboard from "./pages/Dashboard";
import "./styles/App.css";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/Vehicles/register" element={<RegisterVehicle />} />
        <Route path="/Vehicles" element={<ViewVehicles />} />
        <Route path="/appointments/book" element={<BookAppointment />} />
        <Route path="/appointments" element={<MyAppointments />} />
      </Routes>
    </Router>
  );
}

export default App;
