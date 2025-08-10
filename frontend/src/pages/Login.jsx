// src/pages/Login.jsx
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import API from "../api";
import styles from "./Login.module.css"
const Login = () => {
  const [isSignup, setIsSignup] = useState(false);
  const navigate = useNavigate();

  // Form states
  const [gmail_id, setGmailId] = useState("");
  const [password, setPassword] = useState("");
  const [user_name, setUserName] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await API.post("/api/signup/", { gmail_id, user_name, password });
      alert("Signup successful!");
      setIsSignup(false);
      setUserName("");
    } catch (err) {
      alert(err.response?.data?.detail || "Signup failed");
    }
  };

  const handleSignin = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        "http://localhost:8000/api/signin",
        { gmail_id, password },
        { withCredentials: true }
      );
      navigate("/profile");
    } catch (err) {
      alert("Invalid credentials");
    }
  };

  return (
  <div className={styles.container}>
    
    <div className={styles.rightPane}>
      <h1>AI PROMPT GENERATOR</h1>
      <h2>{isSignup ? "Sign Up" : "Sign In"}</h2>

      <form
        onSubmit={isSignup ? handleSignup : handleSignin}
        className={styles.form}
      >
        <input
          type="text"
          placeholder="Gmail ID"
          value={gmail_id}
          onChange={(e) => setGmailId(e.target.value)}
          className={styles.input}
          required
        />
        {isSignup && (
          <input
            type="text"
            placeholder="Username"
            value={user_name}
            onChange={(e) => setUserName(e.target.value)}
            className={styles.input}
            required
          />
        )}
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
          required
        />
        <button type="submit" className={styles.button}>
          {isSignup ? "Sign Up" : "Sign In"}
        </button>
      </form>

      <button
        onClick={() => setIsSignup(!isSignup)}
        className={styles.toggle}
      >
        {isSignup
          ? "Already have an account? Sign In"
          : "Don't have an account? Sign Up"}
      </button>
    </div>
  </div>
);

};
export default Login;