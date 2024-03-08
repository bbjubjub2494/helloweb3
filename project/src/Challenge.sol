// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract Challenge {
    bool public solved;

    function _win() external {
        solved = true;
    }

    function isSolved() public returns (bool) {
        return solved;
    }
}
