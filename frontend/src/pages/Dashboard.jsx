import React, { useState, useEffect } from 'react'
import Navigate from '../components/Navbar'
import axios from 'axios'
import API from '../api'
import  './Dashboard.css'
const Dashboard = () => {
  const [gmailId, setGmailId] = useState("")
  const [idea, setIdea] = useState("")
  const [questions, setQuestions] = useState("")
  const [answers, setAnswers] = useState("")
  const [finalPrompt, setFinalPrompt] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    axios.get("http://localhost:8000/api/me", {
      withCredentials: true,
    })
    .then((res) => {
      setGmailId(res.data.gmail_id)
    })
    .catch(() => {
      alert("User info could not be retrieved.")
    })
  }, [])

  const handleIdeaSubmit = async () => {
    try {
      setLoading(true)
      const res = await API.post("/api/idea", { gmail_id: gmailId, idea })
      setQuestions(res.data.questions)
    } catch (err) {
      alert("Failed to generate questions")
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerSubmit = async () => {
    try {
      setLoading(true)
      const answersArray = answers.split("\n")
      const res = await API.post("/api/answer", { gmail_id: gmailId, answers: answersArray })
      setFinalPrompt(res.data.final_prompt)
    } catch (err) {
      alert("Failed to refine prompt")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
    <Navigate/>
    <div className="generator-container">
  <h2>AI Prompt Generator</h2>

  <textarea
    rows="4"
    cols="50"
    placeholder="Enter your idea here..."
    value={idea}
    onChange={(e) => setIdea(e.target.value)}
  />
  <br />
  <button onClick={handleIdeaSubmit} disabled={loading || !idea}>
    Generate Questions
  </button>

  {questions && (
    <>
      <h3>Generated Questions:</h3>
      
      <pre>{questions}</pre>

      <textarea
        rows="6"
        cols="50"
        placeholder="Answer each question (separate answers by new lines)"
        value={answers}
        onChange={(e) => setAnswers(e.target.value)}
      />
      <br />
      <button onClick={handleAnswerSubmit} disabled={loading || !answers}>
        Refine Prompt
      </button>
    </>
  )}

  {finalPrompt && (
    <>
      <h3>Final AI Prompt:</h3>
      <pre>{finalPrompt}</pre>
    </>
  )}
</div>
</>
  )
}

export default Dashboard
