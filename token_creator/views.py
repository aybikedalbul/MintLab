from django.shortcuts import render
from django.conf import settings
from web3 import Web3
import json
import os

def token_maker(request):
    if request.method == "POST":
        # Formdan gelen verileri al
        name = request.POST.get("token_name")
        symbol = request.POST.get("token_symbol")
        initial_supply = request.POST.get("token_supply")

        # Form alanlarının dolu olup olmadığını kontrol et
        if not name or not symbol or not initial_supply:
            return render(request, "token_maker.html", {"error": "All fields are required."})

        try:
            initial_supply = int(initial_supply)
        except ValueError:
            return render(request, "token_maker.html", {"error": "Initial supply must be a number."})

        # Blockchain bağlantısını kur
        w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))

        # Blockchain bağlantısının başarılı olup olmadığını kontrol et
        if not w3.is_connected():
            return render(request, "token_maker.html", {"error": "Blockchain network connection failed. Please check your Infura URL or internet connection."})

        # Contract bilgilerini yükle
        contract_path = os.path.join(settings.BASE_DIR, "token_creator", "contract.json")
        with open(contract_path, "r") as file:
            contract_data = json.load(file)

        abi = contract_data["abi"]
        bytecode = contract_data.get("bytecode")
        contract_address = contract_data.get("address")

        try:
            # Eğer kontrat deploy edilmediyse deploy et (isteğe bağlı)
            if not contract_address:
                contract = w3.eth.contract(abi=abi, bytecode=bytecode)
                transaction = contract.constructor(name, symbol, initial_supply * (10 ** 18)).build_transaction({
                    "from": settings.INFURA_ACCOUNT_ADDRESS,
                    "nonce": w3.eth.get_transaction_count(settings.INFURA_ACCOUNT_ADDRESS),
                    "gas": 3000000,
                    "gasPrice": w3.to_wei("20", "gwei"),
                })

                # İşlemi imzala ve gönder
                signed_txn = w3.eth.account.sign_transaction(transaction, private_key=settings.INFURA_PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                print(f"Transaction Hash: {tx_hash.hex()}")  # İşlemin hash'ini terminale yazdır
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                contract_address = tx_receipt.contractAddress

                # Yeni contract adresini contract.json'a kaydet
                contract_data["address"] = contract_address
                with open(contract_path, "w") as file:
                    json.dump(contract_data, file)

        except Exception as e:
            # Hata olursa terminale yazdır ve hata mesajı döndür
            print(f"Error during contract deployment: {str(e)}")
            return render(request, "token_maker.html", {"error": f"Contract deployment failed: {str(e)}"})

        # Mevcut bir contract ile işlem yap
        try:
            contract = w3.eth.contract(address=contract_address, abi=abi)
            return render(request, "success.html", {"contract_address": contract_address})
        except Exception as e:
            print(f"Error interacting with contract: {str(e)}")
            return render(request, "token_maker.html", {"error": f"Failed to interact with contract: {str(e)}"})

    return render(request, "token_maker.html")

def welcome(request):
    return render(request, "welcome.html")

def about(request):
    return render(request, "about.html")
