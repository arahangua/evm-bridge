const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");


module.exports = buildModule("BridgeModule", (m) => {
  
  const bridge = m.contract("CombinedBridge", []); 
  
// if additional calling of functions is needed, we declare it here.

  return { bridge };
});
