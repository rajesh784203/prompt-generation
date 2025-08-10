import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';
import './Profile.css';
import Navigate  from "../components/Navbar";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("http://localhost:8000/api/me", {
      withCredentials: true,
    })
      .then((res) => {
        setUser(res.data);
      })
      .catch(() => {
        navigate("/signin");
      });
  }, [navigate]);

  useEffect(() => {
    if (user?.gmail_id) {
      axios.get(`http://localhost:8000/api/analytics/prompt-usage/${user.gmail_id}`)
        .then((res) => {
          setStats(res.data);
        })
        .catch((err) => {
          console.error("Failed to fetch analytics", err);
        });
    }
  }, [user]);

  if (!user) return <p>Loading...</p>;


  return (
    <>
    <Navigate/>
    <div className="dashboard-container">

      <div className="user-info">
        <h1 className="user-heading">👋 Welcome, {user.user_name}</h1>
        <p><strong>Email:</strong> {user.gmail_id}</p>
        <p><strong>Credits:</strong> {user.credits}</p>
      </div>

      {stats ? (
        <div style={{ marginTop: '30px' }}>
          <h2 style={{ marginBottom: '10px' }}>📊 Prompt Usage Analytics</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.daily_usage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
          <p style={{ marginTop: '10px' }}><strong>Total Prompts:</strong> {stats.total_prompts}</p>
        </div>
      ) : (
        <p style={{ marginTop: '30px' }}>Loading usage analytics...</p>
      )}
    </div>
    </>
  );
};

export default Profile;
