const AnswersToken = artifacts.require('./AnswersToken.sol');

module.exports = (deployer) => {
  deployer.deploy(AnswersToken);
};
