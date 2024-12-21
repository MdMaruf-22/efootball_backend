import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Firebase Admin initialization
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "black-stars-f4fbb",
    "private_key_id": "fad59e00613992b4f1ce53e3ba1995b487a6eaea",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCjO3hl28v0Nklj
83bkEOYou5HE4MZUyiTt3YOlMwo0L4sPBIhBrwRvlwtuS0j817b6U1xMmR4V6B6b
vnB86Yn/Tt8hdd3+Rha6JHtaa6snv6n3hg1ne+/L/VTWCWBXfew2MAppL3dWTXvt
lAYmNo184X7CBCEsdOTC9zCqBo21rYGQ05Ih9ABbgxVzeHfAr9jM19R+O3uJkeKf
QWllw0pwJhtLwiN9+9cRqe4ekr+sk0OzFx29Px4GqOLXX15CeF1siWz/r+JpAE7C
o+md/pAlev3tEBrLK+oK8ikqa6omFQoU16R7HRKc772a2ix35WVSzGozvTVVpp5k
AYQtD0d5AgMBAAECggEAFp9dNNS3rrLADMuxxwhL4F+lOLbO60e8GCv9R5h2yhEV
bIaRccpVSuKRUX8P8Fw0flCuTT64AODo2RHq2iJYdJtUPk7CblqoDLKWAUvvGR+t
k+IEGpBT2sl93U9zBufV+b6XusiQI/8HdWpF8zwtSMj3EzbqTWnX8z4PWbPLJl9a
shnsvLzf2n2gaCtg7vdxNAGcRWepTAmuqduj6X2DVwuVGlDa5vJWdeHd/wgnayPk
lnFq1BGZVcxKy6yP4lsSQF3P5DmShG0uINTLYFJjbmqGqNHd0oYxLfOtb7RTlYbb
OZo3tosCJlAmz9VWbg/VbP/R8BIPoiQ2OZEOmhFePwKBgQDmP0eWAXe3WGdtJ+9e
TU4z9OzvzUnDWzx3OKH8JfISKXkZCUEufqYee6cfSne/8dyuR0g7x5uEh91b5svo
dMxrvzRBDgd3dyI4MjLnqDthGRrdQwtGzIWcI9b7ctJcUZhKDJbY9k0eoIhXw9cN
3apNVy34JmObijJvTD3GUsTmXwKBgQC1fVaY+gweykEytBRz5p6Uc1lk85NXQtkn
ydz026BS1YnfO7xeoF0BOgnlKwO1yXkws6puhzF+w8KeNRt0vnxiK4ZUF69qN3qg
VRX/PKPtyDFA9Yo5UEmEo4SNLuh47KTAbsS1+5eH1LX7y0raOURR5zS+dwGf88Df
4ClkEggxJwKBgBJmGh1VjrB7AwDJASrC+K3UM57SA8P1pXZNczxH9/kVkVS71ZaW
jkW/UdKBS+JtvFm83nvQbo//n2O5pK+1raQqik1shpI4VeaxtDmoyt3ueKQXuG32
5/JbNtGvEjpIVugL63346J6660pAHw4/mV1GyyiaQLlsKK2WJRWVBaD3AoGAZ+W/
A4hyE9ZZiLtK0ib+NaHrVT2T5eqhAoQveAWbPJB+g0thRRKs65zcOVNspk8Wj+jq
8qd2kEllSsjAVQ8Pieu81LtSco4cJ1lOZHXEqsVmXPe0D6eEzugFZAWslD10+6zt
8/h6AQqmu+TfjxoloHWp3jemuHkEu6VKTL197xUCgYAtW1NWSa9q1nKdSPc6SjRP
wLoUjBCfMi00MULIHCIVQhiBCq16VMvR5F9TxHSrJAbsoJSJnBOvy5TDTrHLWacY
/19mIaMT8an2qnxbhh7vFABLdY97xwupjbI7WRbL1BVrIPfYXM0Ni5HSbDxDBhoL
eIH0JderSiNSojrReXwUDw==
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-2856f@black-stars-f4fbb.iam.gserviceaccount.com",
    "client_id": "111997749818648193588",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-2856f%40black-stars-f4fbb.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

def create_monthly_collection():
    # Get current month and year
    current_month = datetime.now().strftime("%Y-%m")
    print(f"Creating collection for {current_month}...")

    # Reference to 'players' collection
    players_ref = db.collection('players').stream()

    # Iterate through players and copy their data to the monthly collection
    for player_doc in players_ref:
        player_data = player_doc.to_dict()
        club_id = player_doc.id  # Document ID (club_id)

        # Add data to the new monthly collection
        db.collection(f'players_monthly_{current_month}').document(club_id).set(player_data)
        print(f"Added data for player {club_id} to monthly collection.")

    print(f"Monthly collection for {current_month} created successfully.")

# Run the function
if __name__ == "__main__":
    create_monthly_collection()
