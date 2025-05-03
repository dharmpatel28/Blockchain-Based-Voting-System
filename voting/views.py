import json
from django.shortcuts import render, redirect
from web3 import Web3
import os
from django.contrib import messages
from .forms import AdminLoginForm, AddCandidateForm, RegisterVoterForm
from django.http import JsonResponse

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))


contract_address = "0x4aC8126C870a08bd6961a713c6a88C7d6EdceA85"

with open('E:/voting_system/voting/Election.abi.json') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)
# const adminAddress = await web3.eth.getCoinbase()

def homepage(request):
    return render(request, 'homepage.html')


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            private_key = form.cleaned_data['private_key']
            try:
                account = w3.eth.account.from_key(private_key)
            except Exception as e:
                messages.error(request, "Invalid private key format.")
                return redirect('admin')

            try:
                official = contract.functions.electionOfficial().call()
                if account.address.lower() == official.lower():
                    request.session['private_key'] = private_key
                    return redirect('admin_dashboard')
                else:
                    messages.error(
                        request, "Unauthorized: This private key does not belong to the election official.")
            except Exception as e:
                messages.error(request, f"Error accessing contract: {str(e)}")
    else:
        form = AdminLoginForm()
    return render(request, 'admin.html', {'form': form})

    # return render(request, 'admin.html')


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def start_election(request):
    private_key = request.session.get('private_key')

    if not private_key:
        messages.error(request, "You must log in first.")
        return redirect('admin')

    try:
        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)

        transaction = contract.functions.startElection().build_transaction({
            'chainId': 1337,
            'gas': 3000000,
            'gasPrice': w3.to_wei(20, 'gwei'),
            'nonce': nonce
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        status = receipt.get('status')

        # Ensure status is an integer
        if isinstance(status, str):
            status = int(status, 16)

        if status == 1:
            messages.success(request, "Election started successfully!")
        else:
            messages.error(request, "Election start failed.")

    except Exception as e:
        messages.error(request, f"Error starting election: {str(e)}")

    return redirect('admin_dashboard')



def end_election(request):
    private_key = request.session.get('private_key')

    if not private_key:
        messages.error(request, "You must log in first.")
        return redirect('admin')

    try:
        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)

        # Optional: Check if current state is Voting (1)
        current_state = contract.functions.state().call()
        if current_state != 1:
            messages.error(request, f"Election must be in 'Voting' state to end. Current state: {current_state}")
            return redirect('admin_dashboard')

        # Build the transaction
        transaction = contract.functions.endElection().build_transaction({
            'chainId': 1337,  # For Ganache. Use the correct chain ID for your network
            'gas': 3000000,
            'gasPrice': w3.to_wei(20, 'gwei'),
            'nonce': nonce
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        status = receipt.get('status')

        # Convert status to int if necessary
        if isinstance(status, str):
            status = int(status, 16)

        if status == 1:
            messages.success(request, "Election ended successfully!")
        else:
            messages.error(request, "Election ending failed.")

    except Exception as e:
        messages.error(request, f"Error ending election: {str(e)}")

    return redirect('admin_dashboard')


from django.shortcuts import render, redirect
from django.contrib import messages

def add_candidate(request):
    if request.method == "POST":
        party_name = request.POST.get("party_name")
        private_key = request.session.get("private_key")

        if not private_key:
            messages.error(request, "You must log in first.")
            return redirect('admin')

        if not party_name:
            messages.error(request, "Party name is required.")
            return redirect('admin_dashboard')

        try:
            account = w3.eth.account.from_key(private_key)
            nonce = w3.eth.get_transaction_count(account.address)

            transaction = contract.functions.addCandidates(party_name).build_transaction({
                'chainId': 1337,  # Use correct chain ID for your network
                'gas': 300000,
                'gasPrice': w3.to_wei(20, 'gwei'),
                'nonce': nonce
            })

            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

            if receipt.status == 1:
                messages.success(request, f"Candidate '{party_name}' added successfully!")
            else:
                messages.error(request, "Failed to add candidate.")

        except Exception as e:
            messages.error(request, f"Error adding candidate: {str(e)}")

        return redirect('admin_dashboard')

    # If GET request, show a form (optional)
    return render(request, 'add_candidate.html')  # Or just redirect


def register_voter(request):
    if request.method == "POST":
        voter_address = request.POST.get("voter_address")
        voter_name = request.POST.get("voter_name")
        private_key = request.session.get("private_key")

        if not private_key:
            messages.error(request, "You must log in first.")
            return redirect('admin')

        if not voter_address or not voter_name:
            messages.error(request, "Voter address and name are required.")
            return redirect('admin_dashboard')

        try:
            account = w3.eth.account.from_key(private_key)
            nonce = w3.eth.get_transaction_count(account.address)

            transaction = contract.functions.registerVoter(voter_address, voter_name).build_transaction({
                'chainId': 1337,  # Use correct chain ID for your network
                'gas': 300000,  # You may adjust the gas limit
                'gasPrice': w3.to_wei(20, 'gwei'),
                'nonce': nonce
            })

            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

            if receipt.status == 1:
                messages.success(request, f"Voter '{voter_name}' registered successfully!")
            else:
                messages.error(request, "Failed to register voter.")

        except Exception as e:
            messages.error(request, f"Error registering voter: {str(e)}")

        return redirect('admin_dashboard')

    # If GET request, show a form (optional)
    return render(request, 'register_voter.html')  # Or just redirect



def user(request):
    return render(request, 'user.html')


def show_results(request):

    state = contract.functions.state().call()
    if state != 2:  # Assuming '2' corresponds to 'Ended' state
        messages.error(
            request, "Election results are not available until the election has ended.")
    # Call the smart contract to get the winner
    try:
        winner = contract.functions.getWinner().call()
    except Exception as e:
        winner = str(e)

    # Call the smart contract to get votes for each party
    total_parties = contract.functions.totalParties().call()
    party_votes = []

    for party_id in range(total_parties):
        party_name = contract.functions.parties(
            party_id).call()[1]  # Party name is at index 1
        vote_count = contract.functions.getPartyVotes(party_id).call()
        party_votes.append({"name": party_name, "votes": vote_count})

    context = {
        'winner': winner,
        'party_votes': party_votes,
    }

    return render(request, 'result.html', context)
