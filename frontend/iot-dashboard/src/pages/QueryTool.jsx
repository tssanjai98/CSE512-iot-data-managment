import React, { useState } from "react";

const QueryTool = () => {
    const [query, setQuery] = useState("");
    const [plans, setPlans] = useState([]);
    const [results, setResults] = useState(null);

    const handleQuerySubmit = async () => {
        try {
            const response = await fetch("http://your-backend-api.com/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            });
            const data = await response.json();
            setPlans(data.plans); // Assuming API returns multiple plans
            setResults(data.results); // Assuming API returns query results
        } catch (error) {
            console.error("Error fetching query results:", error);
        }
    };

    return (
        <div>
            <h1>Query Optimization Tool</h1>
            <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your SQL query here"
                rows={5}
                cols={50}
            />
            <button onClick={handleQuerySubmit}>Run Query</button>
            <div>
                <h2>Query Plans</h2>
                {plans.map((plan, index) => (
                    <div key={index}>
                        <p>{plan.description}</p>
                    </div>
                ))}
            </div>
            <div>
                <h2>Query Results</h2>
                {results && <pre>{JSON.stringify(results, null, 2)}</pre>}
            </div>
        </div>
    );
};

export default QueryTool;
