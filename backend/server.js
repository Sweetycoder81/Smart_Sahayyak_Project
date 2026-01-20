const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db.js');
const authRoutes = require('./routes/authRoutes');

dotenv.config();
const app = express();

// Middleware
app.use(express.json());
app.use(cors());

connectDB();

// Test Route
app.get('/', (req, res) => {
    res.send("Smart Sahayyak Backend is Running... 🚀");
});

app.use('/api/auth', authRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));