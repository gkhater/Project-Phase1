// Import required modules
const express = require('express');
const bodyParser = require('body-parser');
const net = require('net');

// Create an instance of express
const app = express();
const port = 5000;

// Use body-parser middleware to parse JSON requests
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set EJS as the template engine
app.set('view engine', 'ejs');

// Serve static files
app.use(express.static('public'));

// Create a persistent socket connection
let client = new net.Socket();
let isClientConnected = false;

// Connect to the server and keep the connection open
function connectToServer() {
    client.connect(5001, '127.0.0.1', () => {
        console.log('Connected to server');
        isClientConnected = true;
    });

    client.on('error', (err) => {
        console.error('Error:', err.message);
        isClientConnected = false;
    });

    client.on('close', () => {
        console.log('Connection closed, reconnecting...');
        isClientConnected = false;
        setTimeout(connectToServer, 1000); // Attempt to reconnect after 1 second
    });
}

// Establish the initial connection
connectToServer();

// Render the login page
app.get('/', (req, res) => {
    res.render('login');
});

// Render the sign-in page
app.get('/signup', (req, res) => {
    res.render('signup');
});

// Create a route for login
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    if (isClientConnected) {
        // Send JSON data for login
        const loginData = {
            choice: `l`,
            username: username,
            password: password,
            p2p_port: "5003"
        };
        const jsonMessage = JSON.stringify(loginData);
        client.write(jsonMessage);
        console.log(`Sent: ${jsonMessage}`);
    } else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }

    // Handle data received from the server
    client.once('data', (data) => {
        const responseData = JSON.parse(data.toString());
        console.log('Received from server:', responseData);

        if (responseData.code === 200) {
            res.render('welcome', { username: responseData.name, products: responseData.products });
        } else {
            res.render('response', { message: 'Interaction failed', data: responseData.message });
        }
    });
});

// Create a route for sign in
app.post('/signin', (req, res) => {
    const { name, email, username, password } = req.body;

    if (isClientConnected) {
        // Send JSON data for sign in
        const signupData = {
            choice: `s`,
            name: name,
            email: email,
            username: username,
            password: password
        };
        const jsonMessage = JSON.stringify(signupData);
        client.write(jsonMessage);
        console.log(`Sent: ${jsonMessage}`);
    } else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }

    // Handle data received from the server
    client.once('data', (data) => {
        console.log('Received from server:', data.toString());
        res.render('response', { message: 'Sign-in interaction successful', data: data.toString() });
    });
});

// Handle logout request
app.post('/logout', (req, res) => {
    if (isClientConnected) {
        // Send logout command as JSON
        const logoutData = {
            command: 'logout'
        };
        const jsonMessage = JSON.stringify(logoutData);
        client.write(jsonMessage);
        res.redirect('/');  
    } else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }

    // Handle data received from the server
    client.once('data', (data) => {
        console.log('Received from server:', data.toString());
        res.redirect('/');  // Redirect to home page after logout
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

// Endpoint to handle adding a new item
app.post('/add-item', (req, res) => {
    const { name, qty, price, description, image } = req.body;

    if (isClientConnected) {
        // Send add-item command as JSON
        const addItemData = {
            command: `add ${qty} ${name} ${price} ${image} ${description}`,
        };
        const jsonMessage = JSON.stringify(addItemData);
        client.write(jsonMessage);
        console.log(`Sent: ${jsonMessage}`);

        client.once('data', (data) => {
            const responseData = JSON.parse(data.toString());
            if (responseData.code === 200) {
                res.json({ success: true, message: 'Item added successfully' });
            } else {
                res.json({ success: false, message: 'Failed to add item' });
            }
        });
    } else {
        res.status(500).json({ success: false, message: 'Not connected to server' });
    }
});

// Endpoint to handle deposit
app.post('/deposit', (req, res) => {
    const { amount } = req.body;

    if (isClientConnected) {
        // Send deposit command to server
        const depositData = {
            command: `deposit ${amount}`,
        };
        const jsonMessage = JSON.stringify(depositData);
        client.write(jsonMessage);
        console.log(`Sent: ${jsonMessage}`);

        client.once('data', (data) => {
            const responseData = JSON.parse(data.toString());
            if (responseData.code === 200) {
                res.json({ success: true, message: 'Deposit successful' });
            } else {
                res.json({ success: false, message: 'Failed to deposit' });
            }
        });
    } else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }
});

// Route to handle "products" request
app.get('/products', async (req, res) => {
    if (isClientConnected) {
        // Send products request as JSON
        const productsData = {
            command: 'products'
        };
        const jsonMessage = JSON.stringify(productsData);
        client.write(jsonMessage);
        console.log(`Sent: ${jsonMessage}`);
    }  else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }

    client.once('data', (data) => {
        const response = JSON.parse(data.toString());
        res.json(response);
        console.log(response);
    });

    client.on('error', (err) => {
        console.error('Error connecting to backend:', err);
        res.status(500).json({ error: 'Failed to fetch products' });
    });
});

// Endpoint to handle purchasing selected items
app.post('/purchase', async (req, res) => {
    let { selectedProducts } = req.body;

    if (!Array.isArray(selectedProducts)) {
        selectedProducts = [selectedProducts];
    }

    if (isClientConnected) {
        try {
            for (const productID of selectedProducts) {
                // Send buy command for each selected product
                const buyData = {
                    command: `buy ${productID}`
                };
                const jsonMessage = JSON.stringify(buyData);
                client.write(jsonMessage);
                console.log(`Sent: ${jsonMessage}`);

                // Await server response for each buy command
                const response = await new Promise((resolve, reject) => {
                    client.once('data', (data) => {
                        const responseData = JSON.parse(data.toString());
                        resolve(responseData);
                    });
                    client.on('error', (err) => {
                        reject(err);
                    });
                });

                if (response.code === 200) {
                    console.log(`Purchase of product ${productID} successful`);
                } else {
                    console.log(`Failed to purchase product ${productID}`);
                }
            }
            res.json({ success: true, message: 'Purchase initiated for selected items' });
        } catch (error) {
            console.error('Error processing purchase:', error);
            res.status(500).json({ success: false, message: 'Failed to complete purchase' });
        }
    } else {
        res.status(500).json({ success: false, message: 'Not connected to server' });
    }
});