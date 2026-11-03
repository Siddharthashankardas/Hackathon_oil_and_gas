import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend unavailable");
        }
        return response.json();
      })
      .then((data) => {
        setBackendStatus(data.status);
      })
      .catch(() => {
        setBackendStatus("Disconnected");
      });
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Pipeline Operations</h1>
          <p>Linepack Optimizer | Decision Support Platform</p>
        </div>

        <span className="status">
          Backend: {backendStatus}
        </span>
      </header>

      <main className="dashboard">
        <section className="welcome">
          <h2>Pipeline Operations Cockpit</h2>
          <p>
            Monitor pipeline conditions, evaluate operating
            scenarios and support linepack decisions.
          </p>
        </section>

        <section className="cards">
          <div className="card">
            <h3>Pipeline Network</h3>
            <p>Network overview will appear here.</p>
          </div>

          <div className="card">
            <h3>Current Linepack</h3>
            <p>Engineering calculations pending.</p>
          </div>

          <div className="card">
            <h3>Active Scenarios</h3>
            <p>Scenario management pending.</p>
          </div>

          <div className="card">
            <h3>AI Decision Support</h3>
            <p>Agent orchestration pending.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;