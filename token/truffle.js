module.exports = {
  networks: {
    development: {
      host: 'localhost',
      port: 8545,
      gas: 500000,
      network_id: '*'
    },
    kovan: {
      host: 'localhost',
      port: 8545,
      network_id: '42',
    }
  }
};
