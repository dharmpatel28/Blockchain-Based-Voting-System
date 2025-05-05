// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.19;

contract Election {
    // Structures
    struct Voter {
        string name;
        bool voted;
        uint votedPartyId;
    }

    struct Party {
        uint id;
        string name;
        uint voteCount;
    }

    // State Variables
    address public electionOfficial;
    string public electionName;
    uint public totalVotes;
    uint public totalParties;

    mapping(address => Voter) public voters;
    mapping(uint => Party) public parties;

    enum State { Created, Voting, Ended }
    State public state;

    // Events
    event VoterRegistered(address voter);
    event PartyAdded(uint partyId, string partyName);
    event VoteCasted(address voter, uint partyId);
    event VotingStarted();
    event VotingEnded();

    // Modifiers
    modifier onlyOfficial() {
        require(msg.sender == electionOfficial, "Only official can perform this action.");
        _;
    }

    modifier inState(State _state) {
        require(state == _state, "Invalid state for this action.");
        _;
    }

    // Constructor
    constructor(string memory _electionName) {
        electionOfficial = msg.sender;
        electionName = _electionName;
        state = State.Created;
    }

    // Register Voter
    function registerVoter(address _voter, string memory _name)
        public onlyOfficial inState(State.Created)
    {
        require(bytes(voters[_voter].name).length == 0, "Voter already registered.");
        voters[_voter] = Voter(_name, false, 0);
        emit VoterRegistered(_voter);
    }

    // Add Party
    function addCandidates(string memory _name)
        public onlyOfficial inState(State.Created)
    {
        parties[totalParties] = Party(totalParties, _name, 0);
        emit PartyAdded(totalParties, _name);
        totalParties++;
    }

    // Start Election
    function startElection() public onlyOfficial inState(State.Created) {
        state = State.Voting;
        emit VotingStarted();
    }

    // Cast Vote
    function vote(uint _partyId)
        public inState(State.Voting)
    {
        Voter storage sender = voters[msg.sender];
        require(bytes(sender.name).length > 0, "Not a registered voter.");
        require(!sender.voted, "Already voted.");
        require(_partyId < totalParties, "Invalid party ID.");

        sender.voted = true;
        sender.votedPartyId = _partyId;
        parties[_partyId].voteCount++;
        totalVotes++;

        emit VoteCasted(msg.sender, _partyId);
    }

    // End Election
    function endElection() public onlyOfficial inState(State.Voting) {
        state = State.Ended;
        emit VotingEnded();
    }

    function getElectionState() public view returns (uint) {
    return uint(state);  // Return state as an integer
}

    // Get Results
    function getPartyVotes(uint _partyId) public view inState(State.Ended) returns (uint) {
    require(_partyId < totalParties, "Invalid party ID.");
    return parties[_partyId].voteCount;
    }

    function getWinner() public view inState(State.Ended) returns (string memory winnerName) {
    require(totalParties > 0, "No parties registered.");
    require(totalVotes > 0, "No votes cast.");

    uint winningVoteCount = 0;
    uint winningPartyId;

    for (uint i = 0; i < totalParties; i++) {
        if (parties[i].voteCount > winningVoteCount) {
            winningVoteCount = parties[i].voteCount;
            winningPartyId = i;
        }
    }

    winnerName = parties[winningPartyId].name;
}
}
