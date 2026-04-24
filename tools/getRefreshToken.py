import requests

# Vul hier je gegevens in:
CLIENT_ID = ''
CLIENT_SECRET = ''
CODE = '' 

try:
    print("Gegevens naar Strava sturen...")
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': CODE,
            'grant_type': 'authorization_code'
        }
    )

    data = response.json()

    # Check of er een foutmelding in het antwoord zit
    if 'errors' in data or 'message' in data:
        print("\n❌ STRAVA GEEFT EEN FOUTMELDING:")
        print(data)
        print("\nLet op: de 'code' uit de adresbalk is maar een paar minuten geldig.")
        print("Als hij is verlopen, moet je Stap 1 en 2 (de link in je browser) even opnieuw doen.")
    else:
        print("\n✅ SUCCES! --- JOUW NIEUWE TOKENS ---")
        print(f"Refresh Token: {data.get('refresh_token')}")
        print(f"Access Token:  {data.get('access_token')}")
        print("--------------------------------------\n")

except Exception as e:
    print("\n❌ Er ging iets mis met het script zelf:")
    print(e)

# Dit is de magische regel die het scherm openhoudt!
input("\nDruk op Enter om dit venster te sluiten...")
