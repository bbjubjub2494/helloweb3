// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

contract Deploy is Script {
    function setUp() public {}

    function run() public {
        vm.broadcast();

        //address challenge = deploy(system);
                                                                                                                       
	// TODO
	address challenge = 0x0000000000000000000000000000000000000001;

        vm.writeFile(vm.envOr("OUTPUT_FILE", string("/tmp/deploy.txt")), vm.toString(challenge));
    }
}
