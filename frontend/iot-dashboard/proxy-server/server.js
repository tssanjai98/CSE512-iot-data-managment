const express = require("express");
const axios = require("axios");
const cors = require("cors");
const { GoogleGenerativeAI } = require("@google/generative-ai");


const app = express();
const PORT = 9999;

// Middleware
app.use(cors()); // Allow requests from the frontend
app.use(express.json()); // Parse JSON request bodies

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_API_KEY = "";

const OPENAI_API_KEY = ""; // Replace with your OpenAI API key
const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";


const genAI = new GoogleGenerativeAI("AIzaSyB2gI8Edzi8y-sOLI0rigkRCbwmYzV9WLg");

// Proxy route to forward requests to Anthropic API
app.post("/proxy/gemini", async (req, res) => {
    try {
        const { model, messages, max_tokens } = req.body;
        const model1 = genAI.getGenerativeModel({ model: model });
        // Forward request to Anthropic API
        const result = await model1.generateContent(messages);

        // Send the API response back to the client
        console.log(result.response.text());
        res.json(result.response.text());
    } catch (error) {
        console.error("Error connecting to GEMINI API:", error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data || "Internal Server Error",
        });
    }
});

// Proxy route to forward requests to Anthropic API
app.post("/proxy/anthropic", async (req, res) => {
    try {
        const { model, messages, max_tokens } = req.body;

        // Forward request to Anthropic API
        const response = await axios.post(
            ANTHROPIC_API_URL,
            { model, messages, max_tokens },
            {
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": ANTHROPIC_API_KEY,
                },
            }
        );

        // Send the API response back to the client
        res.json(response.data);
    } catch (error) {
        console.error("Error connecting to Anthropic API:", error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data || "Internal Server Error",
        });
    }
});


app.post("/proxy/chatgpt", async (req, res) => {
    try {
        const { model, messages, max_tokens } = req.body;

        // Forward the request to OpenAI's ChatGPT API
        const response = await axios.post(
            OPENAI_API_URL,
            { model, messages, max_tokens },
            {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${OPENAI_API_KEY}`, // Pass OpenAI API key
                },
            }
        );

        // Send the response back to the frontend
        res.json(response.data);
    } catch (error) {
        console.error("Error connecting to ChatGPT API:", error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data || "Internal Server Error",
        });
    }
});




// Start the server
app.listen(PORT, () => {
    console.log(`Proxy server is running at http://localhost:${PORT}`);
});
