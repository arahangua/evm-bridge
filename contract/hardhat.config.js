require('dotenv').config(); 
require("@nomicfoundation/hardhat-toolbox");

const { PRIVATE_KEY } = process.env;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    pow_chain: {
      url: "http://<reset of the node url>",
      accounts: [`0x${process.env.PRIVATE_KEY}`]
    },
    pos_chain:{
      url: "http://<reset of the node url>",
      accounts: [`0x${process.env.PRIVATE_KEY}`]
    }

  }
};
