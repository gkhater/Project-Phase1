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
    // client.connect(5001, '192.168.204.63', () => {
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
        setTimeout(connectToServer, 1000); // Attempt to reconnect after 3 seconds
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
        // Send messages
        const messages = ['l', username, password, "5003"];
        messages.forEach((message, index) => {
            setTimeout(() => {
                client.write(Buffer.from(message, 'utf-8')); // Send each message encoded as UTF-8
                console.log(`Sent: ${message}`);
            }, 1000 * index); // Delay increases for each subsequent message
        });
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
        // Send messages
        const messages = ['s', name, email, username, password];
        messages.forEach((message, index) => {
            setTimeout(() => {
                client.write(Buffer.from(message, 'utf-8')); // Send each message encoded as UTF-8
                console.log(`Sent: ${message}`);
            }, 1000 * index); // Delay increases for each subsequent message
        });
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
        // Send logout message
        client.write(Buffer.from('logout', 'utf-8'));
        res.redirect('/');  
        // console.log('Sent: logout');
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
    // console.log(image);
    if (isClientConnected) {
        const message = `add ${qty} ${name} ${price} ${image} ${description}`;
        client.write(Buffer.from(message, 'utf-8'));

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

// app.post('/add-item', (req, res) => {
//     const { name, qty, price, description, image } = req.body;
    
//     if (isClientConnected) {
//         // Use a delimiter to split the message, ensuring every component is present
//         const message = `add ${qty} ${name} ${price} ${description} IMAGE_START${image || ''}IMAGE_END`;
        
//         client.write(Buffer.from(message, 'utf-8'));

//         client.once('data', (data) => {
//             try {
//                 const responseData = JSON.parse(data.toString());
//                 if (responseData.code === 200) {
//                     res.json({ success: true, message: 'Item added successfully' });
//                 } else {
//                     res.json({ success: false, message: responseData.error || 'Failed to add item' });
//                 }
//             } catch (error) {
//                 res.status(500).json({ success: false, message: 'Error processing server response' });
//             }
//         });
//     } else {
//         res.status(500).json({ success: false, message: 'Not connected to server' });
//     }
// });

// Route to handle "products" request
app.get('/products', async (req, res) => {
    const backendData = JSON.stringify({ command: 'products' });
    if (isClientConnected) {
        const message = "products"
        // const message = JSON.stringify({ command: 'products' });
        
        client.write(Buffer.from(message, 'utf-8'));
    }  else {
        res.status(500).render('response', { message: 'Error', data: 'Not connected to server' });
    }


    client.once('data', (data) => {
        // console.log(data.toString())
        const response = JSON.parse(data.toString());
        res.json(response);
        console.log(response)
    });

    client.on('error', (err) => {
        console.error('Error connecting to backend:', err);
        res.status(500).json({ error: 'Failed to fetch products' });
    });
});
