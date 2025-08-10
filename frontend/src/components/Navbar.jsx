import { Link, useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';

const Navigate = () => {


const navigate = useNavigate();

const handleLogout = () => {
    Cookies.remove("access_token");
    navigate("/login");
  };



return <nav className="navbar">
        <Link to="/profile" className="nav-link">Analytics</Link>
        <Link to="/dashboard" className="nav-link">Generate</Link>
        <Link to="/history" className="nav-link">History</Link>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </nav>

}


export default Navigate