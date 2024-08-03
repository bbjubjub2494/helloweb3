// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "@forge-std-1.9.1/src/Script.sol";

import {Challenge} from "src/Challenge.sol";

contract Solve is Script {
    function run(Challenge challenge) public {
        vm.broadcast();

        challenge._win();

        assert(challenge.isSolved());
    }
}
