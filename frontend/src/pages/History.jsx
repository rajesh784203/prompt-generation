import React, { useState, useEffect } from "react";
import Navigate from "../components/Navbar";
import axios from "axios";
import API from "../api";
import  './History.css'
const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true); // 👈 new loading state

  useEffect(() => {
    const fetchUserAndHistory = async () => {
      try {
        const userRes = await axios.get("http://localhost:8000/api/me", {
          withCredentials: true,
        });
        const gmailId = userRes.data.gmail_id;
        const historyRes = await API.get(`/api/history/${gmailId}`);
        setHistory(historyRes.data);
      } catch (err) {
        alert("Failed to fetch history");
      } finally {
        setLoading(false); // 👈 stop loading after both API calls
      }
    };

    fetchUserAndHistory();
  }, []);

  if (loading) return <p>Loading...</p>; // 👈 only show loading if truly loading

  return (
    <>
    <Navigate/>
    <div className="prompt-history">
  <h2>Your Prompt History</h2>
  {history.length === 0 ? (
    <p>No prompts found yet.</p>
  ) : (
    history.map((entry) => (
      <div className="prompt-entry" key={entry.id}>
        <p><strong>Idea:</strong> {entry.idea}</p>
        <p>
          <strong>Questions:</strong>
          <pre>{entry.questions}</pre>
        </p>
        <p>
          <strong>Answers:</strong>
          <pre>{entry.answers}</pre>
        </p>
        <p>
          <strong>Final Prompt:</strong>
          <pre>{entry.final_prompt}</pre>
        </p>
        <p><em>{new Date(entry.timestamp).toLocaleString()}</em></p>
      </div>
    ))
  )}
</div>
</>
  );
};

export default History;