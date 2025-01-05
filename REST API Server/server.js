const http = require('http');
const { Client } = require('pg');
require('dotenv').config();

const client = new Client({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: 5433,
});

client.connect();

const server = http.createServer((req, res) => {
  console.log(`Received request: ${req.method} ${req.url}`);

  // CORS headers for cross-origin requests
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PUT');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle OPTIONS method (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Handle POST requests to update user data
  if (req.method === 'POST' && req.url === '/') {
    console.log('POST request received on root route');
    
    let body = '';

    // Collect the data from the request
    req.on('data', (chunk) => {
      body += chunk;
    });

    req.on('end', async () => {
      try {
        // Parse the incoming data
        const values = JSON.parse(body);
        console.log('Received data:', values);

        // Insert the data into the PostgreSQL database
        await client.query(
          'INSERT INTO user_inputs(user_id, kwh_rate, target_usage) VALUES($1, $2, $3)',
          [values['user_id'], values['kwh_rate'], values['target_usage']]
        );

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'User inputs updated successfully' }));
      } catch (err) {
        console.error('Error processing data:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Error updating user inputs' }));
      }
    });

    return; // End the POST request handler
  }

  // If no matching route is found
  console.log('No matching route found');
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Not Found' }));
});

// Start the server on port 3001
server.listen(3001, () => {
  console.log('Server for Postgres is running on port 3001...');
});
