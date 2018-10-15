pragma solidity ^0.4.24;

import 'openzeppelin-solidity/contracts/token/ERC20/ERC20Burnable.sol';
import 'openzeppelin-solidity/contracts/token/ERC20/ERC20Detailed.sol';
import 'openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol';

contract AnswersToken is ERC20Burnable, ERC20Detailed, ERC20Mintable {
  uint256 public constant INITIAL_SUPPLY = 5000 * (10 ** 18);

  constructor()
    ERC20Burnable()
    ERC20Detailed("AnswersToken", "AST", 18)
    ERC20Mintable()
    public
  {
    _mint(msg.sender, INITIAL_SUPPLY);
  }
}
