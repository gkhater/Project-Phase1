MESSAGES = {
    # General messages
    "WELCOME_PROMPT": '''Welcome to AUBoutique! Do you want to: 
    [S] Sign up
    [L] Log in
    ''',
    "WELCOME_CLIENT": "Welcome back {user}!\n ",
    "INVALID_CHOICE": "Invalid choice, please try again. \n",
    "LOGOUT": "Logging out...\n",
    "PROMPT_USER": '''What would you like to do?
    Available items: 
    {items}
    Online Users: 
    {users}
    Type HELP for help. \n
    ''',
    "HELP_PROMPT": '''Possible commands: 
LOGOUT: Logs out of your account and ends your session.
TEXT [username] [message]: Texts [username] the [message] (username cannot contain empty spaces).
PRODUCTS: List all available products.
CHECK [username]: Check if a user is online.
HELPME : lists all available commands.
BUY [Product_ID]: Buys the product with matching id. 
ADD [name] [price] [description] : lists the following item up for sale. 
SOLD : Lists all of the items you've sold. 
ONLINE: Lists all online users. \n
''',

    "INVALID_ADD" : "Invalid request. Please use ADD [item_name] [price] [description]\n", 
    "INVALID_CHECK" : "Inavlid request.  Please use CHECK [username]\n", 
    "INVALID_BUY" : "Invalid request. Please use BUY [Product_ID]\n", 
    # Text messaging
    "TEXT_OFFLINE": "Could not send message {destination}, {destination} is offline.\n",
    "TEXT_SUCCESS": "Message successfully sent to {destination}!\n",

    # Sign-in/Sign-up
    "ENTER_NAME": "Enter your name: ", 
    "ENTER_EMAIL": "Enter your email: ",
    "ENTER_USERNAME": "Enter your username: ",
    "ENTER_PASSWORD": "Enter your password: ",

    # Sign-up success or failure
    "USER_ADDED_SUCCESS": "User: '{username}' added successfully.\n",
    "USERNAME_EXISTS": "Username: '{username}' already exists.\n",

    # Log-in success or failure
    "AUTH_SUCCESS": "Welcome, {name}!\n",
    "AUTH_FAILED": "Username and password don't match.\n",

    # Unknown command
    "UNKNOWN_COMMAND": "Unknown command. Type HELPME to get a list of all available commands.\n",

    # Server status
    "SERVER_START": "Server listening on port {port}...",
    "CONNECTION_ESTABLISHED": "Connection established with {addr}",
    "USER_DISCONNECTED": "User {username} has disconnected.",

    #Products
    "PRODUCT_NOT_FOUND" : "Error: product not found. Please provide a valid product ID.\n", 
    "ITEM_NOT_AVAILABLE" : "Error: '{name}' is no longer available for purchase.\n", 
    "SALE_SUCCESS" : "You bought '{name}' for ${price}. \nPlease pick up your purchase from the AUB Post Office in 3 days.\n", 
    "NO_SALES" : "You haven't sold any products yet.\n", 
    "PRODUCT_ADDED": "Product {product_name} added successfully!\n", 
    #Images
    "IMG_SUCCESS": "Image saved successfully\n", 
    "IMG_ERROR" : "Error sending image {e}\n", 

    #User status
    "USER_ONLINE" : "{username} is online \n", 
    "USER_OFFLINE": "{username} is offline \n"
}
