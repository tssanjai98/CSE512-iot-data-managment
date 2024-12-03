import React, { useState, useEffect } from "react";
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Select,
    MenuItem,
    CircularProgress,
    TableContainer,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Paper,
    TextField,
    Button,
    Modal,
    Box,
} from "@mui/material";
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import fakeData from "../fakeData/fake_data.json"; // Replace with actual data
import "../styles/dashboard.css";
import axios from 'axios';

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const randomSummaries = [
    "Battery levels across most cars are stable, with a few showing critical levels.",
    "Engine temperature data indicates consistent performance, with a few outliers.",
    "Tire pressure sensors show healthy readings across all cars in the dataset.",
    "Fuel levels are moderate, with a few vehicles requiring immediate refueling.",
    "Overall, the system is functioning well with minimal alerts.",
];

const Dashboard = () => {
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [selectedCar, setSelectedCar] = useState("");
    const [selectedSensor, setSelectedSensor] = useState("");
    const [loading, setLoading] = useState(true);
    const [alertMode, setAlertMode] = useState(false);
    const [summary, setSummary] = useState("");
    const [modalOpen, setModalOpen] = useState(false);
    const [error, setError] = useState(null);

    const API_ENDPOINT = "http://127.0.0.1:8000/get_metrics";

    // Fetch data from the API
    const fetchData = async () => {
        setLoading(true);
        try {
            const response = await fetch(API_ENDPOINT);
            if (!response.ok) {
                throw new Error("Failed to fetch data");
            }
            const result = await response.json();
            const apiData = result.data; // Extract the `data` property
            setData(apiData);
            setFilteredData(apiData);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    // Simulate data loading
    useEffect(() => {
        fetchData()
    }, []);

    // Update filtered data when category or car changes
    useEffect(() => {
        let updatedData = data;

        if (selectedCategory !== "all") {
            updatedData = updatedData.filter((item) => item.category === selectedCategory);
        }

        if (selectedCar) {
            updatedData = updatedData.filter((item) => item.car_name === selectedCar);
        }

        setFilteredData(updatedData);
    }, [selectedCategory, selectedCar, data]);

    // Filter data for alerts
    const alertData = filteredData
        .flatMap((item) =>
            item.metrics
                .filter((metric) => metric.alert)
                .map((metric) => ({
                    car_name: item.car_name,
                    sensor_name: metric.sensor_name,
                    value: metric.value,
                    alert_cause: metric.alert_cause,
                    severity: metric.severity,
                }))
        );

    // Data for alert visualizations
    const alertCauses = alertData.reduce((acc, alert) => {
        acc[alert.alert_cause] = (acc[alert.alert_cause] || 0) + 1;
        return acc;
    }, {});

    const alertCauseData = Object.entries(alertCauses).map(([cause, count]) => ({
        name: cause,
        value: count,
    }));

    const alertsByCar = alertData.reduce((acc, alert) => {
        acc[alert.car_name] = (acc[alert.car_name] || 0) + 1;
        return acc;
    }, {});

    const alertsByCarData = Object.entries(alertsByCar).map(([car, count]) => ({
        car_name: car,
        count: count,
    }));


    // List of cars in the filtered data
    const carOptions = [...new Set(filteredData.map((item) => item.car_name))];

    // List of sensors for a selected car
    const sensorOptions = selectedCar
        ? ["All Sensors", ...new Set(filteredData.find((item) => item.car_name === selectedCar)?.metrics.map((metric) => metric.sensor_name) || [])]
        : [];

    // Prepare sensor data
    const getSensorData = (sensorName) => {
        return filteredData
            .flatMap((item) =>
                item.metrics
                    .filter((metric) => metric.sensor_name === sensorName)
                    .map((metric) => ({
                        car_name: item.car_name,
                        value: metric.value,
                        timestamp: item.timestamp,
                    }))
            );
    };

    // Generate Prompt for Text Summarization
    const generatePrompt = (data) => {
        // Extract sensor details
        const sensorSummaries = data.map((sensor) => {
            return `The sensor "${sensor.sensor_id}" has ${sensor.warning_count} warnings, ${sensor.critical_count} critical alerts, and ${sensor.normal_count} normal readings.`;
        });

        // Combine into a full prompt
        return `Summarize the following IoT car sensor alert statistics in a clear, professional, and concise text format:
    
${sensorSummaries.join("\n")}

Provide an overall summary highlighting key insights, potential risks, and the general state of the system.`;
    };

    // Typewriter effect for summary
    const typewriterEffect = (text) => {
        console.log(text)
        setSummary("");
        let i = 0;
        const interval = setInterval(() => {
            console.log(summary)
            if (i < text.length) {
                setSummary((prev) => prev + text.charAt(i));
                i++;
            } else {
                clearInterval(interval);
            }
        }, 1); // Typing speed
    };

    const generateSummary = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch alerts data from local API
            const alertsResponse = await axios.get("http://127.0.0.1:8000/get_severity_counts");
            console.log(alertsResponse)
            const summaryPrompt =  generatePrompt(alertsResponse.data.data);

            console.log(summaryPrompt)

            

            

            // Call the backend proxy server
            const proxyResponse = await axios.post("http://localhost:9999/proxy/gemini", {
                model: "gemini-1.5-flash", // Use the desired OpenAI model
                messages: summaryPrompt,
                max_tokens: 500,
            });

            // Extract the summary from ChatGPT's response
            const generatedSummary = proxyResponse.data;

            typewriterEffect(generatedSummary);
            setModalOpen(true);
        } catch (err) {
            console.error("Error generating summary:", err.response?.data || err.message);
            setError("Failed to generate summary. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Generate a random summary
    const resetFilters = () => {
        setSelectedCategory("all");
        setSelectedCar("")
        setSelectedSensor("");
    };

    if (loading) {
        return (
            <div className="spinner">
                <CircularProgress />
            </div>
        );
    }

    return (
        <div className="dashboard">
            <Typography variant="h4" gutterBottom>
                AZ Automobile Monitoring Dashboard
            </Typography>

            {/* Toggle between Dashboard and Alerts View */}
            <Button
                variant={alertMode ? "contained" : "outlined"}
                onClick={() => setAlertMode(!alertMode)}
                style={{ marginBottom: "20px" }}
            >
                {alertMode ? "Switch to Main Dashboard" : "Switch to Alerts View"}
            </Button>

            {!alertMode ? (
                <>
                    {/* Filters */}
                    <Grid container spacing={2} style={{ marginBottom: "20px" }}>
                        <Grid item xs={4}>
                            <TextField
                                select
                                label="Filter by Category"
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                fullWidth
                            >
                                <MenuItem value="all">All</MenuItem>
                                <MenuItem value="suv">SUV</MenuItem>
                                <MenuItem value="sedan">Sedan</MenuItem>
                                <MenuItem value="coupe">Coupe</MenuItem>
                            </TextField>
                        </Grid>
                        <Grid item xs={4}>
                            <TextField
                                select
                                label="Filter by Car Name"
                                value={selectedCar}
                                onChange={(e) => setSelectedCar(e.target.value)}
                                fullWidth
                                disabled={!carOptions.length}
                            >
                                {carOptions.map((car) => (
                                    <MenuItem key={car} value={car}>
                                        {car}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>
                        <Grid item xs={4}>
                            <TextField
                                select
                                label="Filter by Sensor"
                                value={selectedSensor}
                                onChange={(e) => setSelectedSensor(e.target.value)}
                                fullWidth
                                disabled={!sensorOptions.length}
                            >
                                {sensorOptions.map((sensor) => (
                                    <MenuItem key={sensor} value={sensor}>
                                        {sensor}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid item xs={4}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={resetFilters}
                                style={{ marginTop: "20px" }}
                            >
                                Reset Filters
                            </Button>
                        </Grid>
                    </Grid>


                    {/* Sensor Visualizations */}
                    {!selectedSensor || selectedSensor === "All Sensors" ? (
                        < Grid container spacing={3}>
                            {/* Engine Temperature */}
                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">Engine Temperature Trends</Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={getSensorData("Engine Temperature Sensor")}>
                                                <XAxis dataKey="timestamp" />
                                                <YAxis />
                                                <Tooltip />
                                                <Line type="monotone" dataKey="value" stroke="#8884d8" />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Battery Levels */}
                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">Battery Levels</Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={getSensorData("Battery Level Sensor")}>
                                                <XAxis dataKey="car_name" />
                                                <YAxis />
                                                <Tooltip />
                                                <Bar dataKey="value" fill="#82ca9d" />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Fuel Level */}
                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">Fuel Levels</Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={getSensorData("Fuel Level Sensor")}>
                                                <XAxis dataKey="car_name" />
                                                <YAxis />
                                                <Tooltip />
                                                <Bar dataKey="value" fill="#FFBB28" />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Tire Pressure */}
                            <Grid item xs={12} md={6}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">Tire Pressure Trends</Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <ScatterChart>
                                                <XAxis type="category" dataKey="car_name" name="Car" />
                                                <YAxis type="number" dataKey="value" name="Tire Pressure" />
                                                <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                                                <Scatter data={getSensorData("Tire Pressure Sensor")} fill="#FF8042" />
                                            </ScatterChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    ) : (
                        <Grid container spacing={3}>
                            {/* Specific Sensor Chart */}
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6">{selectedSensor} Trends</Typography>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={getSensorData(selectedSensor)}>
                                                <XAxis dataKey="timestamp" />
                                                <YAxis />
                                                <Tooltip />
                                                <Line type="monotone" dataKey="value" stroke="#8884d8" />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    )}

                    {/* Summarize Button */}
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={generateSummary}
                        style={{ marginTop: "20px" }}
                    >
                        Summarize Visualization
                    </Button>
                </>
            ) : (
                <>
                    {/* Alert Dashboard Visualizations */}
                    <Grid container spacing={3}>
                        {/* Alerts by Cause */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alerts by Cause</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={alertCauseData}
                                                cx="50%"
                                                cy="50%"
                                                outerRadius={100}
                                                label
                                                dataKey="value"
                                            >
                                                {alertCauseData.map((entry, index) => (
                                                    <Cell
                                                        key={`cell-${index}`}
                                                        fill={COLORS[index % COLORS.length]}
                                                    />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Alerts by Car */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alerts by Car</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart data={alertsByCarData}>
                                            <XAxis dataKey="car_name" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar dataKey="count" fill="#FF8042" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Alerts Severity by Sensor */}
                        <Grid item xs={12}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alert Severity by Sensor</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <ScatterChart>
                                            <XAxis dataKey="sensor_name" name="Sensor" />
                                            <YAxis dataKey="severity" name="Severity" />
                                            <Tooltip />
                                            <Scatter
                                                data={alertData.map((alert) => ({
                                                    sensor_name: alert.sensor_name,
                                                    severity:
                                                        alert.severity === "Critical"
                                                            ? 3
                                                            : alert.severity === "Warning"
                                                                ? 2
                                                                : 1,
                                                }))}
                                                fill="#8884d8"
                                            />
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </>
            )
            }

            {/* Summary Modal */}
            <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
                <Box
                    sx={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        width: 400,
                        bgcolor: "background.paper",
                        border: "2px solid #000",
                        boxShadow: 24,
                        p: 4,
                    }}
                >
                    <Typography variant="h6">Summary</Typography>
                    <Typography sx={{ mt: 2 }}>{summary}</Typography>
                </Box>
            </Modal>
        </div >
    );
};

export default Dashboard;
