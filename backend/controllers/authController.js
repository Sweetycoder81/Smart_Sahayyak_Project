const User = require('../models/User');
const bcrypt = require('bcryptjs');

exports.registerUser = async (req, res) => {
    try {
        const { name, email, password, emergencyEmail } = req.body;

        // Check if user already exists
        let user = await User.findOne({ email });
        if (user) return res.status(400).json({ msg: "User already exists" });

        // Hash password (Security)
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        user = new User({ name, email, password: hashedPassword, emergencyEmail });
        await user.save();

        res.status(201).json({ msg: "User registered successfully!" });
    } catch (err) {
        res.status(500).send("Server Error");
    }
};