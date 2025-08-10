import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Profile from "./pages/Profile"
import Dashboard from './pages/Dashboard'
import History from './pages/History'

const App = () => {

  return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/history" element={<History/>} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
  )
}

export default App
