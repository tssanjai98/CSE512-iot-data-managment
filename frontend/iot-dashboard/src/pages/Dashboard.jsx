import React, { useState, useEffect } from "react";
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Select,
    MenuItem,
    Button,
    CircularProgress,
} from "@mui/material";
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    LineChart,
    Line,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    RadarChart,
    Radar,
    PolarGrid,
    PolarAngleAxis,
} from "recharts";


import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TextField
} from "@mui/material";


import fakeData from "../../../../datagen/fake_data.json"; // Import fake data
import "../styles/dashboard.css";

const Dashboard = () => {
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [alertsMode, setAlertsMode] = useState(false); // Mode state
    const [loading, setLoading] = useState(true);

    const [deviceFilter, setDeviceFilter] = useState(""); // Device ID filter
    const [categoryFilter, setCategoryFilter] = useState("all"); // Category filter

    // Filtered data for the table
    const filteredAlerts = filteredData
        .filter((d) => d.alerts)
        .filter((d) =>
            deviceFilter ? d.device_id.toLowerCase().includes(deviceFilter.toLowerCase()) : true
        )
        .filter((d) => (categoryFilter === "all" ? true : d.category === categoryFilter));

    // Simulate loading of data
    useEffect(() => {
        setLoading(true);
        setTimeout(() => {
            setData(fakeData);
            setFilteredData(fakeData);
            setLoading(false);
        }, 1000); // Simulated loading delay
    }, []);

    // Update filtered data when category changes
    useEffect(() => {
        if (selectedCategory === "all") {
            setFilteredData(data);
        } else {
            setFilteredData(data.filter((device) => device.category === selectedCategory));
        }
    }, [selectedCategory, data]);

    // Chart Data Preparation
    const statusDistribution = [
        { name: "Active", value: filteredData.filter((d) => d.status === "active").length },
        { name: "Inactive", value: filteredData.filter((d) => d.status === "inactive").length },
        { name: "Maintenance", value: filteredData.filter((d) => d.status === "maintenance").length },
        { name: "Error", value: filteredData.filter((d) => d.status === "error").length },
    ];

    const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

    // Prepare chart data
    const alertDistribution = [
        { name: "With Alerts", value: filteredData.filter((d) => d.alerts).length },
        { name: "Without Alerts", value: filteredData.filter((d) => !d.alerts).length },
    ];

    const alertsByCategory = [
        { category: "Sensor", count: filteredData.filter((d) => d.alerts && d.category === "sensor").length },
        { category: "Actuator", count: filteredData.filter((d) => d.alerts && d.category === "actuator").length },
        { category: "Communication", count: filteredData.filter((d) => d.alerts && d.category === "communication").length },
        { category: "Power", count: filteredData.filter((d) => d.alerts && d.category === "power").length },
        { category: "Tracking", count: filteredData.filter((d) => d.alerts && d.category === "tracking").length },
    ];

    const alertCauses = filteredData
        .filter((d) => d.alerts && d.alert_cause)
        .reduce((acc, device) => {
            acc[device.alert_cause] = (acc[device.alert_cause] || 0) + 1;
            return acc;
        }, {});

    const alertCauseData = Object.entries(alertCauses).map(([cause, count]) => ({
        name: cause,
        value: count,
    }));

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
                IoT Dashboard
            </Typography>

            {/* Mode Toggle Button */}
            <div className="mode-toggle">
                <Button
                    variant={alertsMode ? "contained" : "outlined"}
                    onClick={() => setAlertsMode(!alertsMode)}
                >
                    {alertsMode ? "Switch to Main Dashboard" : "Switch to Alerts Mode"}
                </Button>
            </div>

            {!alertsMode && (
                <>
                    {/* Filter Dropdown */}
                    <div className="filter">
                        <Typography variant="subtitle1">Filter by Category:</Typography>
                        <Select
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                            style={{ marginLeft: "10px" }}
                        >
                            <MenuItem value="all">All</MenuItem>
                            <MenuItem value="sensor">Sensor</MenuItem>
                            <MenuItem value="actuator">Actuator</MenuItem>
                            <MenuItem value="communication">Communication</MenuItem>
                            <MenuItem value="power">Power</MenuItem>
                            <MenuItem value="tracking">Tracking</MenuItem>
                        </Select>
                    </div>

                    <Grid container spacing={3}>
                        {/* Pie Chart: Device Status Distribution */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Device Status Distribution</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={statusDistribution}
                                                cx="50%"
                                                cy="50%"
                                                label
                                                outerRadius={100}
                                                fill="#8884d8"
                                                dataKey="value"
                                            >
                                                {statusDistribution.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Bar Chart: Battery Levels */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Battery Levels Across Devices</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart data={filteredData}>
                                            <XAxis dataKey="device_id" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar dataKey="metrics.battery_level" fill="#82ca9d" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Line Chart: Uptime Trends */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Device Uptime Trends</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <LineChart data={filteredData}>
                                            <XAxis dataKey="device_id" />
                                            <YAxis />
                                            <Tooltip />
                                            <Line type="monotone" dataKey="metrics.uptime" stroke="#8884d8" />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Scatter Plot: Latency vs. Signal Strength */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Latency vs. Signal Strength</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <ScatterChart>
                                            <XAxis type="number" dataKey="metrics.latency" name="Latency" />
                                            <YAxis type="number" dataKey="metrics.signal_strength" name="Signal Strength" />
                                            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                                            <Scatter data={filteredData} fill="#8884d8" />
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Radar Chart: Device Health Metrics */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Device Health Metrics</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <RadarChart data={filteredData.slice(0, 10)}> {/* First 10 devices */}
                                            <PolarGrid />
                                            <PolarAngleAxis dataKey="device_id" />
                                            <Radar name="Battery" dataKey="metrics.battery_level" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </>
            )}

            {alertsMode && (
                <>
                    {/* Alerts Mode */}
                    <Grid container spacing={3}>
                        {/* Pie Chart: Alerts Distribution */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alerts Distribution</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={alertDistribution}
                                                cx="50%"
                                                cy="50%"
                                                label
                                                outerRadius={100}
                                                fill="#8884d8"
                                                dataKey="value"
                                            >
                                                {alertDistribution.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={index === 0 ? "#FF8042" : "#82ca9d"} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Bar Chart: Alerts by Category */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alerts by Category</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart data={alertsByCategory}>
                                            <XAxis dataKey="category" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar dataKey="count" fill="#FF8042" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Alert Causes</Typography>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={alertCauseData}
                                                cx="50%"
                                                cy="50%"
                                                label
                                                outerRadius={100}
                                                fill="#82ca9d"
                                                dataKey="value"
                                            >
                                                {alertCauseData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </Grid>


                        {/* Alerts Table */}
                        <Grid item xs={12}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">Devices with Alerts</Typography>
                                    {/* Filters */}
                                    <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
                                        <TextField
                                            label="Filter by Device ID"
                                            variant="outlined"
                                            size="small"
                                            value={deviceFilter}
                                            onChange={(e) => setDeviceFilter(e.target.value)}
                                        />
                                        <Select
                                            value={categoryFilter}
                                            onChange={(e) => setCategoryFilter(e.target.value)}
                                            variant="outlined"
                                            size="small"
                                        >
                                            <MenuItem value="all">All Categories</MenuItem>
                                            <MenuItem value="sensor">Sensor</MenuItem>
                                            <MenuItem value="actuator">Actuator</MenuItem>
                                            <MenuItem value="communication">Communication</MenuItem>
                                            <MenuItem value="power">Power</MenuItem>
                                            <MenuItem value="tracking">Tracking</MenuItem>
                                        </Select>
                                    </div>
                                    {/* Table */}
                                    <TableContainer component={Paper}>
                                        <Table>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Device ID</TableCell>
                                                    <TableCell>Category</TableCell>
                                                    <TableCell>Status</TableCell>
                                                    <TableCell>Battery Level</TableCell>
                                                    <TableCell>Last Maintenance</TableCell>
                                                    <TableCell>Alert Cause</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {filteredAlerts.map((device) => (
                                                    <TableRow key={device.device_id}>
                                                        <TableCell>{device.device_id}</TableCell>
                                                        <TableCell>{device.category}</TableCell>
                                                        <TableCell>{device.status}</TableCell>
                                                        <TableCell>{device.metrics.battery_level}%</TableCell>
                                                        <TableCell>{new Date(device.last_maintenance).toLocaleDateString()}</TableCell>
                                                        <TableCell>{device.alert_cause || "N/A"}</TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>;
                    </Grid>
                </>
            )}
        </div>
    );
};

export default Dashboard;
