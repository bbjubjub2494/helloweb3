// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

import {Challenge} from "src/Challenge.sol";

contract Deploy is Script {
    function setUp() public {}

    function run() public {
        vm.broadcast();

        Challenge challenge = new Challenge();

        vm.writeFile(vm.envOr("OUTPUT_FILE", string("/tmp/deploy.txt")), vm.toString(address(challenge)));
    }
}
