import pandas as pd
import requests
import base64
from time import sleep

# Tokens de acesso da API do Spotify
CLIENT_ID = 'insira seu token aqui'
CLIENT_SECRET = 'insira seu token aqui'

# Autenticação
def get_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {'Authorization': f'Basic {auth_header}'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(auth_url, headers=headers, data=data)
    return response.json()['access_token']

access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
auth_header = {'Authorization': f'Bearer {access_token}'}

# Carrega a planilha
df = pd.read_excel("../Original_Data/Spotify Global Chart 2024.xlsx")

# Adiciona colunas para resultados
df['album_name'] = None
df['album_cover_url'] = None

# Busca o nome e a capa dos álbuns
def search_track_album(track_name, artist_name):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={requests.utils.quote(query)}&type=track&limit=1"

    while True:
        response = requests.get(url, headers=auth_header)

        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 5))
            sleep(wait_time)
            continue

        if response.status_code != 200:
            return None, None

        items = response.json().get('tracks', {}).get('items', [])
        if not items:
            return None, None

        track = items[0]
        album_name = track['album']['name']
        album_cover = track['album']['images'][0]['url'] if track['album']['images'] else None
        return album_name, album_cover

# Itera sobra cada linha do dataframe e adiciona o nome da álbum e a url da capa
for i, row in df.iterrows():
    track = row['track_name']
    artist = row['artist']

    try:
        album, cover = search_track_album(track, artist)
        df.at[i, 'album_name'] = album
        df.at[i, 'album_cover_url'] = cover
        print(f"{i+1}: {track} - {artist} → Álbum: {album}")
    except Exception as e:
        print(f"Erro ao processar linha {i+1}: {track} - {artist} | {e}")

    sleep(0.5)  # Evita time limit

# Salva em um csv
df.to_excel("../Original_Data/top_200_spotify.csv", index=False)
