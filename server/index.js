const express = require('express');
const mysql = require('mysql2/promise');
const dotenv = require('dotenv');
const Groq = require("groq-sdk");
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');

dotenv.config();

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());
app.use(bodyParser.json());

// Hard-coded credentials for the user database
const userDbConfig = {
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'account_db'
};

// In-memory storage for user-specified database credentials
let userDbCredentials = null;

// Function to create a connection to the user database
const getUserDbConnection = async () => {
    return await mysql.createConnection(userDbConfig);
};

// Function to create a connection to the user-specified database
const getUserSpecifiedDbConnection = async () => {
    if (!userDbCredentials) {
        // Commented out to allow running without DB connection
        // throw new Error('User database credentials not set.');
        return null; // Return null instead of throwing an error
    }
    return await mysql.createConnection(userDbCredentials);
};

// Signup endpoint
app.post('/signup', async (req, res) => {
    const { email, username, password, groqApiKey } = req.body;
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const connection = await getUserDbConnection();
        const [result] = await connection.query(
            'INSERT INTO users (email, username, password, groq_api_key) VALUES (?, ?, ?, ?)',
            [email, username, hashedPassword, groqApiKey]
        );
        await connection.end();
        res.json({ success: true });
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ error: error.message });
    }
});

// Login endpoint
app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        const connection = await getUserDbConnection();
        const [rows] = await connection.query('SELECT * FROM users WHERE username = ?', [username]);
        await connection.end();

        if (rows.length === 0) {
            return res.status(401).json({ error: 'Invalid username or password' });
        }

        const user = rows[0];
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ error: 'Invalid username or password' });
        }

        res.json({ success: true, groqApiKey: user.groq_api_key });
    } catch (error) {
        console.error('Error logging in user:', error);
        res.status(500).json({ error: error.message });
    }
});

let groq;

app.post('/credentials', async (req, res) => {
    const { host, dbName, username, password, groqApiKey } = req.body;
    groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

    // Store user-specified database credentials
    userDbCredentials = { host, user: username, password, database: dbName };

    let connection;
    try {
        connection = await getUserSpecifiedDbConnection();

        if (!connection) {
            return res.status(400).json({ error: "No database connection established." });
        }

        // Retrieve list of tables
        const [tables] = await connection.query("SHOW TABLES");
        const tableNames = tables.map(row => Object.values(row)[0]);

        // Retrieve schema details for each table
        const schemaPromises = tableNames.map(async (tableName) => {
            const [columns] = await connection.query(`SHOW COLUMNS FROM ${tableName}`);
            return { tableName, columns };
        });

        const schema = await Promise.all(schemaPromises);

        res.json({ success: true, schema });
    } catch (error) {
        console.error("Error connecting to user-specified database:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.end();
    }
});

// Connect to MySQL database
const initDatabase = async () => {
    return await mysql.createConnection(userDbCredentials);
};

// Get detailed schema from the database
const getDatabaseSchema = async (db) => {
    const [tables] = await db.query("SHOW TABLES");
    const schema = {};

    for (let row of tables) {
        const tableName = Object.values(row)[0];
        const [columns] = await db.query(`SHOW COLUMNS FROM ${tableName}`);
        schema[tableName] = columns.map(column => ({
            field: column.Field,
            type: column.Type,
            null: column.Null,
            key: column.Key,
            default: column.Default,
            extra: column.Extra
        }));
    }

    return schema;
};

// Generate SQL query using Groq
const generateSQLQuery = async (databaseName, schema, chatHistory, userQuery) => {
    const formattedSchema = JSON.stringify(schema, null, 2);
    const formattedHistory = chatHistory.map(entry => `Question: ${entry.content}`).join('\n');

    const prompt = `
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        The database name is "${databaseName}". Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
        
        <SCHEMA>
        ${formattedSchema}
        </SCHEMA>
        
        Conversation History:
        ${formattedHistory}
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        
        For example:
        Question: which 3 artists have the most tracks?
        SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
        Question: Name 10 artists
        SQL Query: SELECT Name FROM Artist LIMIT 10;
        
        Your turn:
        
        Question: ${userQuery}
        SQL Query:
    `;

    const response = await groq.chat.completions.create({
        messages: [
            {
                role: "user",
                content: prompt,
            },
        ],
        model: "llama3-8b-8192",
    });

    return response.choices[0]?.message?.content.trim();
};

// Format SQL response using Groq
const formatSQLResponse = async (sqlQuery, result, error = null) => {
    const formattedResult = JSON.stringify(result, null, 2);
    const prompt = `
        You are a helpful assistant that formats SQL query results and explains SQL errors in simple terms.

        If you receive a successful SQL query result, format it for easy understanding. 
        If you receive an error, explain the cause of the error and how to fix it in simple language.
        If you do not receive an error, do not mention it.
        
        Replace code blocks and syntaxes with <code> html tag. 
        Replace asterisks with <bold> html tag.
        Use proper spacing and add new lines using <p> and <br> tags.
        Try to make it as much readable on html page as possible.
        Use html tables wherever required.
        Make it look pretty.
        for titles use <strong> or <bold>
        dont add extra    

        SQL Query: ${sqlQuery}
        
        Result:
        ${formattedResult}
        
        Error: ${error ? error.message : "None"}
        
        Your formatted response:
    `;

    const response = await groq.chat.completions.create({
        messages: [
            {
                role: "user",
                content: prompt,
            },
        ],
        model: "llama3-70b-8192",
    });

    return response.choices[0]?.message?.content.trim();
};

// Handle user queries
app.post('/chat', async (req, res) => {
    const { userQuery, chatHistory } = req.body;
    let db;
    try {
        // Use user-specified database connection
        db = await getUserSpecifiedDbConnection();

        // If no DB is connected, return an error
        if (!db) {
            return res.status(400).json({ sqlQuery: null, formattedResponse: "No database connected. Please provide credentials first.", error: true });
        }

        // Get schema details for the specific database
        const schema = await getDatabaseSchema(db);

        const sqlQuery = await generateSQLQuery(userDbCredentials.database, schema, chatHistory, userQuery);
        console.log('Generated SQL Query:', sqlQuery); // Log the generated SQL query

        let result;
        try {
            const [queryResult] = await db.query(sqlQuery);
            result = queryResult;
        } catch (sqlError) {
            // Handle SQL error
            const formattedError = await formatSQLResponse(sqlQuery, null, sqlError);
            return res.json({ sqlQuery, formattedResponse: formattedError, error: true });
        }

        console.log('SQL Query Result:', result); // Log the SQL query result

        // Format the SQL query result using Groq
        const formattedResponse = await formatSQLResponse(sqlQuery, result, 'html'); // Request HTML format
        res.json({ sqlQuery, formattedResponse, error: false });
    } catch (error) {
        console.error("Error processing request:", error);
        res.status(500).json({ sqlQuery: null, formattedResponse: "Internal Server Error. Please try again later.", error: true });
    } finally {
        if (db) db.end();
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
