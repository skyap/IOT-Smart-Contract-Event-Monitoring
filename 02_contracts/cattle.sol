pragma solidity ^0.6.7;
pragma experimental ABIEncoderV2;

import "openzeppelin/contracts/token/ERC721/ERC721Burnable.sol";
import "openzeppelin/contracts/utils/Counters.sol";


contract Cattle is ERC721Burnable {

    using Counters for Counters.Counter;

    using Strings for string;
    
    Counters.Counter public _tokenId;

    constructor() public ERC721("Cattle","C") {}
     

    event add_token_activity_event(uint256 indexed tokenId, string[] token_activity);
    
    function create_token() public{
        _tokenId.increment();
        uint256 token_id=_tokenId.current();
        super._mint(msg.sender,token_id);
    }
    function deactive_token(uint256 token_id) public{
        super._burn(token_id);        
    }

    function add_token_activity(uint256 tokenId,string[] memory token_activity) public {
        require(super._isApprovedOrOwner(msg.sender,tokenId));
        emit add_token_activity_event(tokenId,token_activity);
        
    }
}

