// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CombinedBridge {
    address public admin;
    mapping(address => uint256) public balances;
    mapping(bytes32 => bool) public processedNonces;
    mapping(bytes32 => bool) public queuedNonces;

    event EtherLocked(address indexed from, uint256 amount, address toChainAddress); // oracle knows the mapping between the address(hex) and the matching chain. (works as a "password")
    event EtherUnlocked(address indexed to, uint256 amount, bytes32 nonce); // nonce here checks if the transfer was properly done.
    event Withdrawalqueued(address indexed from, bytes32 nonce);

    constructor() {
        admin = msg.sender; //sets admin address (a rich account to manage the bridging)
    }

    // Locks Ether in the contract
    function lockEther(address toChainAddress) external payable {
        require(msg.value > 0, "Send ETH to lock");
        balances[msg.sender] += msg.value;
        emit EtherLocked(msg.sender, msg.value, toChainAddress); // event that oracle listens to

    }


    function queue_unlockEther(address from, bytes32 nonce) external{
        queuedNonces[nonce] = true;
        emit Withdrawalqueued(from, nonce);
    }

    // Unlocks the Ether and sends directly to the recipient address
    function unlockEther(address payable to, uint256 amount, bytes32 nonce) external {
        require(!processedNonces[nonce], "Transfer already processed");
        require(queuedNonces[nonce], "withdrawal was not approved by the Oracle");
        require(balances[to] >= amount, "Insufficient balance locked");
        balances[to] -= amount;
        to.transfer(amount);
        processedNonces[nonce] = true;
        emit EtherUnlocked(to, amount, nonce); // also an event oracle CAN listen to
    }

    // Additional administrative functions to handle errors or misrouted funds
    function reclaimEther(address from, uint256 amount) external {
        require(msg.sender == admin, "Only admin can reclaim funds");
        require(balances[from] >= amount, "Insufficient balance");
        balances[from] -= amount;
        payable(admin).transfer(amount);
    }

    // pure view functions
    function check_if_processed(bytes32 nonce) public view returns (bool) {
        return processedNonces[nonce];
    }


}