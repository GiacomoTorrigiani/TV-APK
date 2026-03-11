import flet as ft
import flet_video as fv  # <-- IL PLAYER VIDEO INTERNO
import requests

def main(page: ft.Page):
    page.title = "IPTV Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 450  
    page.window.height = 800

    all_channels = []

    # --- 1. IL PLAYER VIDEO INTERNO ---
    # Lo mettiamo in cima all'app. Inizialmente è invisibile.
    video_player = fv.Video(
        expand=False,
        height=250,          # Altezza del video
        visible=False,       # Nascosto finché non clicchi un canale
        autoplay=True,       # Parte da solo
        show_controls=True   # Mostra i tasti play/pausa e volume
    )

    # --- 2. ELEMENTI DELL'INTERFACCIA ---
    url_input = ft.TextField(
        label="URL API", 
        value="http://oplayer.one:80/player_api.php?username=4681957290&password=7907106035&action=get_live_streams",
        text_size=10,
        height=50
    )
    
    search_input = ft.TextField(
        label="🔍 Cerca canale (es. Sky, IT:)",
        on_change=lambda e: filter_channels(e.control.value),
        disabled=True 
    )

    channels_list = ft.ListView(expand=True, spacing=10)

    # --- 3. FUNZIONI ---
    def display_channels(channels_to_show):
        channels_list.controls.clear()
        
        # Mostriamo i primi 150 canali
        for channel in channels_to_show[:150]: 
            name = channel.get('name', 'Sconosciuto')
            stream_id = channel.get('stream_id', '')
            
            tile = ft.Container(
                content=ft.Row([
                    ft.Text("📺", size=24),
                    ft.Column([
                        ft.Text(name, size=16, weight="bold"),
                        ft.Text(f"ID: {stream_id}", size=12, color="grey"),
                    ], expand=True), 
                    ft.Text("▶", size=24, color="green")
                ]),
                padding=10,
                border_radius=10,
                bgcolor="#2b2b2b",
                # Quando tocchi la riga, chiama la funzione play_stream
                on_click=lambda e, sid=stream_id: play_stream(sid)
            )
            channels_list.controls.append(tile)
        
        if len(channels_to_show) > 150:
            channels_list.controls.append(
                ft.Text(f"...e altri {len(channels_to_show) - 150} canali. Usa la ricerca!", color="grey", italic=True, text_align=ft.TextAlign.CENTER)
            )
            
        page.update()

    def filter_channels(query):
        if not query:
            display_channels(all_channels)
            return
            
        query = query.lower()
        filtered = [c for c in all_channels if query in c.get('name', '').lower()]
        display_channels(filtered)

    def fetch_channels(e):
        channels_list.controls.clear()
        channels_list.controls.append(ft.Text("Scaricamento in corso...", italic=True, color="yellow"))
        page.update()
        
        headers = {'User-Agent': 'IPTVSmartersPro'}
        try:
            response = requests.get(url_input.value, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                all_channels.clear()
                all_channels.extend(data)
                
                search_input.disabled = False
                display_channels(all_channels)
            else:
                channels_list.controls.clear()
                channels_list.controls.append(ft.Text(f"Errore: {response.status_code}", color="red"))
                page.update()
        except Exception as ex:
            channels_list.controls.clear()
            channels_list.controls.append(ft.Text(f"Errore: {ex}", color="red"))
            page.update()

    def play_stream(stream_id):
            # Torniamo al .ts per Windows
            video_url = f"http://oplayer.one:80/live/4681957290/7907106035/{stream_id}.ts"
            
            video_player.playlist = [fv.VideoMedia(video_url)]
            video_player.visible = True
            video_player.play()
            page.update()
    fetch_btn = ft.ElevatedButton("📥 1. Scarica Canali", on_click=fetch_channels)
    
    # Aggiungiamo tutto alla pagina. NOTA: video_player è il primo elemento!
    page.add(
        video_player, 
        url_input,
        fetch_btn,
        search_input,
        ft.Divider(),
        channels_list
    )

# Avvio del server web locale
ft.run(main)