const http = require('http');
const { Client } = require('pg');
require('dotenv').config();

const client = new Client({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: process.env.POSTGRES_PORT
});

client.connect();

const server = http.createServer((req, res) => {
  console.log(`Received request: ${req.method} ${req.url}`);

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, POST, PUT');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.method === 'POST' && req.url === '/user_inputs') {
    console.log('POST request received for user_inputs');

    let body = '';

    req.on('data', (chunk) => {
      body += chunk;
    });

    req.on('end', async () => {
      try {
        const values = JSON.parse(body);
        console.log('Received data for user_inputs:', values);

        // Validate required fields
        const requiredFields = ['user_id', 'kwh_rate', 'target_usage'];
        const missingFields = requiredFields.filter(
          (field) => !Object.hasOwn(values, field) || values[field] === null
        );

        if (missingFields.length > 0) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(
            JSON.stringify({
              message: `Missing required fields: ${missingFields.join(', ')}`,
            })
          );
          return;
        }

        const columns = Object.keys(values).join(', ');
        const params = Object.values(values);
        const placeholders = Object.keys(values)
          .map((_, i) => `$${i + 1}`)
          .join(', ');

        const query = `INSERT INTO user_inputs(${columns}) VALUES(${placeholders})`;

        await client.query(query, params);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(
          JSON.stringify({ message: 'Data inserted successfully into user_inputs' })
        );
      } catch (err) {
        console.error('Error processing user_inputs:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Error inserting data into user_inputs' }));
      }
    });

    return;
  }

  if (req.method === 'POST' && req.url === '/thresholds') {
    console.log('POST request received for thresholds');

    let body = '';

    req.on('data', (chunk) => {
      body += chunk;
    });

    req.on('end', async () => {
      try {
        const values = JSON.parse(body);
        console.log('Received data for thresholds:', values);

        // Validate required fields
        const requiredFields = [
          'meter_id',
          'max_v',
          'voltage_imbalance',
          'warning_current',
          'trip_off_current',
          'kVAR_max',
          'kVAR_imbalance',
          'kW_max',
          'kW_imbalance',
          'pf_max',
          'vTHD_limit',
          'iTHD_limit',
        ];
        const missingFields = requiredFields.filter(
          (field) => !Object.hasOwn(values, field) || values[field] === null
        );

        if (missingFields.length > 0) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(
            JSON.stringify({
              message: `Missing required fields: ${missingFields.join(', ')}`,
            })
          );
          return;
        }

        const columns = Object.keys(values).join(', ');
        const params = Object.values(values);
        const placeholders = Object.keys(values)
          .map((_, i) => `$${i + 1}`)
          .join(', ');

        const query = `INSERT INTO thresholds(${columns}) VALUES(${placeholders})`;

        await client.query(query, params);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(
          JSON.stringify({ message: 'Data inserted successfully into thresholds' })
        );
      } catch (err) {
        console.error('Error processing thresholds:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Error inserting data into thresholds' }));
      }
    });

    return;
  }

  console.log('No matching route found');
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Not Found' }));
});

server.listen(3001, () => {
  console.log('Server for Postgres is running on port 3001...');
});
