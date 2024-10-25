# Frontend Documentation

This document explains how the current frontend of the bridge application works, based on the three main files: `app.py`, `index.html`, and `script.js`.

## Overview

The frontend is a web application that allows users to interact with a bridge contract on a Proof of Work (PoW) Ethereum network. It provides functionality to lock Ether in the bridge contract.

## Components

### 1. Backend (app.py)

The backend is a Flask application that serves as an intermediary between the frontend and the Ethereum network. Key features include:

- Connects to the PoW Ethereum network using Web3.py
- Loads the bridge contract ABI and address
- Provides API endpoints for:
  - Serving the main page
  - Locking Ether
  - Retrieving the contract ABI
  - Retrieving the contract address

### 2. Frontend HTML (index.html)

The HTML file provides the structure for the web interface. It includes:

- A form for users to input the amount of Ether to lock
- Status display area
- Result display area
- Error log area
- Links to necessary JavaScript files (Web3.js and custom script.js)

### 3. Frontend JavaScript (script.js)

The JavaScript file handles the client-side logic and interaction with MetaMask. Key functionalities include:

- Initializing Web3 and connecting to MetaMask
- Checking and updating the network connection
- Handling the "Lock Ether" form submission
- Sending transaction data to the backend
- Initiating the transaction through MetaMask
- Displaying results and errors

## Workflow

1. When the page loads, `script.js` attempts to connect to MetaMask and initialize Web3.
2. The script checks if the user is connected to the correct PoW network.
3. When the user submits the "Lock Ether" form:
   a. The frontend sends a request to the backend with the amount to lock.
   b. The backend prepares the transaction data and sends it back to the frontend.
   c. The frontend uses this data to send a transaction request to MetaMask.
   d. MetaMask prompts the user to confirm the transaction.
   e. The result (transaction hash or error) is displayed to the user.

## Error Handling

- The application includes error logging both on the frontend and backend.
- Errors are displayed in the user interface and logged to the console for debugging.

## Security Considerations

- The application uses environment variables for sensitive data (e.g., contract addresses, RPC endpoints).
- It relies on MetaMask for secure key management and transaction signing.

