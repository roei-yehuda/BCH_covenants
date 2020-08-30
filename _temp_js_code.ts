/*
This file is a template...
*/

import {BITBOX} from "bitbox-sdk";
import { CashCompiler, Contract, SignatureTemplate } from 'cashscript';

// general consts
let NETWORK = 'testnet';
const MAINNET_API = 'https://free-main.fullstack.cash/v3/';
const TESTNET_API = 'https://free-test.fullstack.cash/v3/';

// wallet consts
const w_json_f = 'wallet.json';
let mnemonic = '';
const child_i = 0;

// contract consts
const cash_f = 'cov.cash';
const artifact_f = 'cov.json';
const con_info_json_f = '_cov_info.json';
const do_compile = true;


const fs = require('fs');
const outObj = new Object();


// @ts-ignore
async function create_wallet() {
	/*
	Creates an HDnode and saves its info into w_json_f.
	*/

	if (NETWORK === 'mainnet') {
		const bitbox = new BITBOX();
	}
	else {
		const bitbox = new BITBOX({restURL: TESTNET_API});
	}

	if (mnemonic === '') {
		mnemonic = bitbox.Mnemonic.generate();
	}

	const rootSeed = bitbox.Mnemonic.toSeed(mnemonic);
	const hdNode = bitbox.HDNode.fromSeed(rootSeed, NETWORK);	// wallet

	// Create key pair and public key
	const childNode = bitbox.HDNode.derive(hdNode, child_i);
	const childKeyPair = bitbox.HDNode.toKeyPair(childNode);	// alice
	const childPK = bitbox.ECPair.toPublicKey(childKeyPair);	// alicePk

	// Write out the basic information into a json file
	const outObj = {
		mnemonic: mnemonic,
		hdNode: hdNode,
		childNode_i: child_i,
		childNode: childNode,
		childKeyPair: childKeyPair,
		childPK: childPK,
		cashAddress: bitbox.HDNode.toCashAddress(childNode),
	};
	fs.writeFile(w_json_f, JSON.stringify(outObj, null, 2), function (err) {
      if (err) return console.error(err)
      console.log(w_json_f + ' written successfully.');
    });

}

// @ts-ignore
async function init_contract() {
	/*
	This function creates and returns a new contract
	*/

	if (NETWORK === 'mainnet') {
		const bitbox = new BITBOX();
	}
	else {
		const bitbox = new BITBOX({restURL: TESTNET_API});
	}

	// artifact
	if (do_compile) {
		const artifact = CashCompiler.compileFile(cash_f);
	}
	else {
		try{
			const artifact = require(artifact_f);
		} catch (err) {
			try{
				const artifact = require('.\\' + artifact_f);
			} catch (err) {
				console.log('Could not import ' +  artifact_f);
				process.exit(0);
			}
		}
	}

	// provider
	const provider = new BitboxNetworkProvider(NETWORK, bitbox);

	// new contract
	if ('' === ''){
		// no constructor arguments are given, so try and get them from con_info_json_f
		const conInfo = load_contract_info();
		const con = new Contract(artifact, conInfo.constructor_args, provider);
	} else {
		// create a new contract
		const con = new Contract(artifact, [], provider);
		// Write out the basic information into con_info_json_f
		const outObj = {
			address: con.address,
			constructor_args: [],
			network_provider_str: 'new BitboxNetworkProvider(NETWORK, bitbox)'
		};
		fs.writeFile(con_info_json_f, JSON.stringify(outObj, null, 2), function (err) {
		  if (err) return console.error(err)
		  console.log(con_info_json_f + ' written successfully.')
		});
	}

	return con;

}


// @ts-ignore
async function load_contract_info(){
	/*
	Load the info found at con_info_json_f, which is basically the contract's address and, a list of its constructor arguments.
	*/

	try {
	  var conInfo = require(con_info_json_f);
	} catch (err) {
		try {
			var conInfo = require('.\\' + con_info_json_f);
		} catch (err) {
			console.log('Could not open ' +  con_info_json_f);
			process.exit(0);
		}
	}
	console.log('loaded ' + con_info_json_f);
	return conInfo;
}


// @ts-ignore
async function print_contract_info() {

	const con = init_contract();
	console.log('contract info:');
	console.log('address: ' + con.address);
	console.log('opcount: ' + con.opcount);
	console.log('bytesize: ' + con.bytesize);
	const contractBalance = await con.getBalance();
	console.log('balance: ' + contractBalance);
	console.log('UTXOs:');
	const utxos = await con.getUtxos();
	console.log(utxos);
}

// @ts-ignore
async function use_contract() {
	/*
	Use a contract by calling one of its functions
	*/

	// creator of tx:
	const walletInfo = await load_wallet_info();
	const childKeyPair = walletInfo.childKeyPair;	// alice
	const childPK = walletInfo.childPK;	// alicePk

	// contract contract:
	const con = init_contract();

	// build and send tx:
	const txDetails = '';

	console.log('Tx details:');
	console.log(txDetails);

}



console.log('Wassup??');

