import React, { useState, useEffect } from "react";
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Button,
    TextField,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
} from "@mui/material";
import mermaid from "mermaid";
import "../styles/queryTool.css";
import { staticApiResponse } from "../fakeData/staticData";

const QueryTool = () => {
    const [query, setQuery] = useState("");
    const [apiResponse, setApiResponse] = useState(null);
    const [selectedPlanGraph, setSelectedPlanGraph] = useState(null);
    const [loading, setLoading] = useState(false);
    const [graphId, setGraphId] = useState(0); // Add a counter for unique IDs

    // Initialize mermaid once
    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,  // Changed to false
            theme: 'default',
            securityLevel: 'loose',
        });
    }, []);

    // Handle graph rendering
    useEffect(() => {
        const renderMermaidDiagram = async () => {
            if (selectedPlanGraph) {
                try {
                    // Clear previous content
                    const element = document.getElementById('mermaid-diagram');
                    if (element) {
                        element.innerHTML = '';
                        
                        // Generate unique ID for this render
                        const uniqueId = `graphDiv-${graphId}`;
                        setGraphId(prev => prev + 1);

                        // Create temporary element with unique ID
                        const tempDiv = document.createElement('div');
                        tempDiv.id = uniqueId;
                        element.appendChild(tempDiv);

                        // Render new diagram
                        const { svg } = await mermaid.render(uniqueId, selectedPlanGraph);
                        element.innerHTML = svg;
                    }
                } catch (error) {
                    console.error("Failed to render mermaid diagram:", error);
                }
            }
        };

        renderMermaidDiagram();
    }, [selectedPlanGraph, graphId]);

    const executeQuery = async () => {
        if (!(query.startsWith("select") ||query.startsWith("SELECT")) ) {
            window.alert("Operation Restricted!!");
            return;
        }
        setLoading(true);
    
        try {
            const response = await fetch("http://127.0.0.1:8000/get_query_plan", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ query }), // Send the query as the request body
            });
    
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
    
            const result = await response.json();
            setApiResponse(result); // Set the API response
            setSelectedPlanGraph(null); // Reset the selected plan graph
            console.log(result)
        } catch (error) {
            console.error("Error executing query:", error);
            window.alert("Failed to execute the query. Please try again.");
        } finally {
            setLoading(false); // Stop the loading spinner
        }
    };

    const renderGraph = (graph) => {
        setSelectedPlanGraph(graph);
    };

    return (
        <div className="query-tool">
            <Typography variant="h4" gutterBottom>
                Query Tool
            </Typography>

            {/* Query Input Section */}
            <Card>
                <CardContent>
                    <Typography variant="h6">Write Your Query</Typography>
                    <TextField
                        multiline
                        rows={4}
                        variant="outlined"
                        fullWidth
                        placeholder="Enter SQL Query here..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        style={{ marginTop: "15px" }}
                    />
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={executeQuery}
                        style={{ marginTop: "15px" }}
                        disabled={loading || !query}
                    >
                        {loading ? "Executing..." : "Execute Query"}
                    </Button>
                </CardContent>
            </Card>

            {/* Execution Plans */}
            {apiResponse && (
                <Grid container spacing={3} style={{ marginTop: "20px" }}>
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6">Execution Plans</Typography>
                                <div className="plans-container">
                                    {apiResponse.executionPlans.map((plan) => (
                                        <div
                                            key={plan.id}
                                            className={`plan-card ${plan.id === apiResponse.selectedPlan ? "chosen-plan" : ""}`}
                                            onClick={() => renderGraph(plan.graph)}
                                        >
                                            <Typography variant="body1">
                                                <strong>{plan.description}</strong>
                                            </Typography>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Mermaid Graph */}
            {selectedPlanGraph && (
                <Grid container spacing={3} style={{ marginTop: "20px" }}>
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6">Execution Plan Diagram</Typography>
                                <div id="mermaid-diagram"></div>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Query Results */}
            {apiResponse && apiResponse.searchResult.length > 0 && (
                <Grid container spacing={3} style={{ marginTop: "20px" }}>
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6">Query Results</Typography>
                                <TableContainer component={Paper}>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                {Object.keys(apiResponse.searchResult[0]).map((key) => (
                                                    <TableCell key={key}>{key.replace("_", " ").toUpperCase()}</TableCell>
                                                ))}
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {apiResponse.searchResult.map((row, index) => (
                                                <TableRow key={index}>
                                                    {Object.values(row).map((value, cellIndex) => (
                                                        <TableCell key={cellIndex}>{value}</TableCell>
                                                    ))}
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}
        </div>
    );
};

export default QueryTool;