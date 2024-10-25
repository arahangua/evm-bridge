let web3;
let contract;
let userAccount;
const POW_CHAIN_ID = '702'; // Replace with your actual PoW chain ID

async function updateStatus(message) {
    document.getElementById('status').textContent = message;
}

async function checkAndUpdateNetwork() {
    if (typeof window.ethereum !== 'undefined') {
        const chainId = await web3.eth.getChainId();
        if (chainId.toString() === POW_CHAIN_ID) {
            await updateStatus('Connected to MetaMask on PoW network');
            return true;
        } else {
            await updateStatus(`Please switch to the PoW network (Chain ID: ${POW_CHAIN_ID}) in MetaMask. Current network: ${chainId}`);
            return false;
        }
    }
    return false;
}

async function initializeWeb3() {
    if (typeof window.ethereum !== 'undefined') {
        web3 = new Web3(window.ethereum);
        try {
            // Request account access
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            userAccount = (await web3.eth.getAccounts())[0];
            
            if (!(await checkAndUpdateNetwork())) {
                return false;
            }
            
            // Get the contract ABI
            const response = await fetch('/get_abi');
            const contractABI = await response.json();
            
            // Get the contract address from the server
            const addressResponse = await fetch('/get_contract_address');
            const contractAddress = await addressResponse.text();
            
            if (!contractAddress) {
                throw new Error('Contract address not found');
            }
            
            contract = new web3.eth.Contract(contractABI, contractAddress);

            // Listen for network changes
            window.ethereum.on('chainChanged', (chainId) => {
                checkAndUpdateNetwork();
            });

            return true;
        } catch (error) {
            console.error("Error initializing Web3:", error);
            await updateStatus('Failed to connect to MetaMask or wrong network');
            return false;
        }
    } else {
        console.log('MetaMask not detected');
        await updateStatus('Please install MetaMask');
        return false;
    }
}

window.addEventListener('load', initializeWeb3);

async function lockEther() {
    const amount = document.getElementById('amount').value;
    
    if (!(await initializeWeb3())) {
        return;
    }

    try {
        console.log('Sending lock_ether request with amount:', amount);
        const response = await fetch('/lock_ether', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                amount: amount,
                from: userAccount
            }),
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const responseText = await response.text();
        console.log('Response text:', responseText);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}, message: ${responseText}`);
        }
        
        const transactionData = JSON.parse(responseText);
        console.log('Transaction data:', transactionData);
        
        // Send transaction using MetaMask
        const txHash = await window.ethereum.request({
            method: 'eth_sendTransaction',
            params: [{
                from: userAccount,
                to: transactionData.to,
                value: web3.utils.toHex(transactionData.value),
                data: transactionData.data,
                gas: web3.utils.toHex(transactionData.gas),
                gasPrice: web3.utils.toHex(transactionData.gasPrice),
            }],
        });
        
        document.getElementById('result').textContent = `Transaction sent: ${txHash}`;
    } catch (error) {
        console.error('Error:', error);
        console.error('Error stack:', error.stack);
        document.getElementById('result').textContent = 'Error: ' + error.message;
        document.getElementById('error-log').innerHTML += '<p>Error stack: ' + error.stack + '</p>';
    }
}

document.getElementById('lockEtherForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await lockEther();
});
