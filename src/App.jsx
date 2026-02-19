import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [score, setScore] = useState(null);

  const generateQuestion = async () => {
    const res = await axios.post("http://127.0.0.1:8000/generate-question", {
      topic: "Artificial Intelligence",
      objectives: ["Define Artificial Intelligence"]
    });
    setQuestion(res.data.question);
  };

  const submitAnswer = async () => {
    const res = await axios.post("http://127.0.0.1:8000/evaluate-answer", {
      topic: "Artificial Intelligence",
      question: question,
      answer: "My answer"
    });
    setScore(res.data.score);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Learning App</h2>

      <button onClick={generateQuestion}>
        Generate Question
      </button>

      {question && (
        <>
          <p><b>Question:</b> {question}</p>
          <button onClick={submitAnswer}>
            Submit Answer
          </button>
        </>
      )}

      {score !== null && (
        <p><b>Score:</b> {score * 100}%</p>
      )}
    </div>
  );
}

export default App;
