const express = require('express');
const mysql = require('mysql2/promise');
const dotenv = require('dotenv');
const Groq = require('groq-sdk');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');

// Loads environment variables from a .env file into process.env
dotenv.config();

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());
app.use(bodyParser.json());

// FIX: Initialize the Groq client once, globally, using the key from .env
const groq = new Groq({apiKey: process.env.GROQ_API_KEY});

// Hard-coded credentials for the user account database
const userDbConfig = {
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'account_db'
};

// In-memory storage for the user's target database credentials
let userDbCredentials = null;

const getUserDbConnection = async () => {
  return await mysql.createConnection(userDbConfig);
};

const getUserSpecifiedDbConnection = async () => {
  if (!userDbCredentials) {
    return null;
  }
  return await mysql.createConnection(userDbCredentials);
};

// Signup endpoint
app.post('/signup', async (req, res) => {
  // FIX: Removed groqApiKey from the request body. It's no longer needed from
  // the user.
  const {email, username, password} = req.body;
  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const connection = await getUserDbConnection();
    // FIX: Updated INSERT query to no longer save an API key.
    const [result] = await connection.query(
        'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
        [email, username, hashedPassword]);
    await connection.end();
    res.json({success: true});
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({error: error.message});
  }
});

// Login endpoint
app.post('/login', async (req, res) => {
  const {username, password} = req.body;
  try {
    const connection = await getUserDbConnection();
    const [rows] = await connection.query(
        'SELECT * FROM users WHERE username = ?', [username]);
    await connection.end();

    if (rows.length === 0) {
      return res.status(401).json({error: 'Invalid username or password'});
    }

    const user = rows[0];
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({error: 'Invalid username or password'});
    }

    // FIX: Removed groqApiKey from the response. The client doesn't need it.
    res.json({success: true});
  } catch (error) {
    console.error('Error logging in user:', error);
    res.status(500).json({error: error.message});
  }
});

// Credentials endpoint to connect to the user's target database
app.post('/credentials', async (req, res) => {
  // FIX: Removed groqApiKey from the request body.
  const {host, dbName, username, password} = req.body;
  userDbCredentials = {host, user: username, password, database: dbName};

  let connection;
  try {
    connection = await getUserSpecifiedDbConnection();
    if (!connection) {
      return res.status(400).json(
          {error: 'No database connection established.'});
    }

    const [tables] = await connection.query('SHOW TABLES');
    const tableNames = tables.map(row => Object.values(row)[0]);

    const schemaPromises = tableNames.map(async (tableName) => {
      const [columns] =
          await connection.query(`SHOW COLUMNS FROM ${tableName}`);
      return {tableName, columns};
    });

    const schema = await Promise.all(schemaPromises);
    res.json({success: true, schema});
  } catch (error) {
    console.error('Error connecting to user-specified database:', error);
    res.status(500).json({error: error.message});
  } finally {
    if (connection) connection.end();
  }
});

const getDatabaseSchema = async (db) => {
  const [tables] = await db.query('SHOW TABLES');
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

const generateSQLQuery =
    async (databaseName, schema, chatHistory, userQuery) => {
  const formattedSchema = JSON.stringify(schema, null, 2);
  const formattedHistory =
      chatHistory.map(entry => `Question: ${entry.content}`).join('\n');
  const prompt = `
        You are an expert SQL data analyst. Your task is to write a single, executable SQL query to answer the user's question based on the provided database schema and conversation history.

        <SCHEMA>
        ${formattedSchema}
        </SCHEMA>

        Conversation History:
        ${formattedHistory}

        - Analyze the user's question carefully. If they ask for a total, sum, average, or count, use the appropriate SQL aggregate function (e.g., SUM(), AVG(), COUNT()).
        - Write ONLY the raw SQL query.
        - Do NOT include any explanations, introductory text, or markdown formatting like \`\`\`.

        Question: ${userQuery}
        SQL Query:
    `;
  const response = await groq.chat.completions.create({
    messages: [{role: 'user', content: prompt}],
    model: 'llama3-8b-8192',
  });

  // FIX: Greatly improved SQL parsing to handle conversational text and
  // multiple statements.
  let rawResponse = response.choices[0]?.message?.content.trim() || '';

  // Clean up potential markdown formatting first
  if (rawResponse.startsWith('```sql')) {
    rawResponse = rawResponse.substring(5);
  }
  if (rawResponse.startsWith('```')) {
    rawResponse = rawResponse.substring(3);
  }
  if (rawResponse.endsWith('```')) {
    rawResponse = rawResponse.slice(0, -3).trim();
  }

  // Find the start of the first valid SQL query statement
  const keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH'];
  let startIndex = -1;

  for (const keyword of keywords) {
    const index = rawResponse.toUpperCase().indexOf(keyword);
    if (index !== -1) {
      if (startIndex === -1 || index < startIndex) {
        startIndex = index;
      }
    }
  }

  let query = rawResponse;
  if (startIndex > -1) {
    query = rawResponse.substring(startIndex);
  }

  // Take only the first statement if multiple are present (e.g., separated by
  // ';')
  query = query.split(';')[0];

  return query.trim();
};

const formatSQLResponse = async (sqlQuery, result, error = null) => {
  const formattedResult = JSON.stringify(result, null, 2);
  const prompt = `
        You are a helpful assistant. Format SQL query results and explain SQL errors in simple terms.
        If you receive a result, format it nicely in HTML.
        If there is an error, explain it simply.
        Use HTML tags like <p>, <br>, <strong>, and <table> for readability.
        SQL Query: ${sqlQuery}
        Result: ${formattedResult}
        Error: ${error ? error.message : 'None'}
        Your formatted response:
    `;
  const response = await groq.chat.completions.create({
    messages: [{role: 'user', content: prompt}],
    model: 'llama3-70b-8192',
  });
  return response.choices[0]?.message?.content.trim();
};

// Handle user queries
app.post('/chat', async (req, res) => {
  const {userQuery, chatHistory} = req.body;
  let db;
  try {
    db = await getUserSpecifiedDbConnection();
    if (!db) {
      return res.status(400).json({
        formattedResponse:
            'No database connected. Please provide credentials first.'
      });
    }

    const schema = await getDatabaseSchema(db);
    const sqlQuery = await generateSQLQuery(
        userDbCredentials.database, schema, chatHistory, userQuery);
    console.log('Generated SQL Query:', sqlQuery);

    let result;
    try {
      const [queryResult] = await db.query(sqlQuery);
      result = queryResult;
    } catch (sqlError) {
      const formattedError = await formatSQLResponse(sqlQuery, null, sqlError);
      return res.json(
          {sqlQuery, formattedResponse: formattedError, error: true});
    }

    console.log('SQL Query Result:', result);
    const formattedResponse = await formatSQLResponse(sqlQuery, result);
    res.json({sqlQuery, formattedResponse, error: false});
  } catch (error) {
    console.error('Error processing request:', error);
    res.status(500).json({formattedResponse: 'Internal Server Error.'});
  } finally {
    if (db) db.end();
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
