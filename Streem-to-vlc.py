import json
import jmespath
from jinja2 import Environment

with open('output.json', 'r') as f:
    playlist_json = json.load(f)

playlist_json = sorted(playlist_json, key=lambda x: int(x.get("curtent_index", 0)))

playlist_title = jmespath.search("[*].title|[0]",playlist_json)
playlist_videos_titles = jmespath.search("[*].video_title",playlist_json)
playlist_videos_links = jmespath.search("[*].video_link",playlist_json)
playlist_chanels_titles = jmespath.search("[*].chanel_title",playlist_json)

all_playlist_data = zip(playlist_chanels_titles,playlist_videos_titles,playlist_videos_links)

template_str = """
#EXTM3U
#EXTVLCOPT:playlist-title={{ playlist_title }}
	{% for chanel_title,video_title,video_link in all_playlist_data %}
#EXTINF:-1,{{ chanel_title }} - {{ video_title  }}
{{ video_link  }}{% endfor %}
"""
                                
env = Environment()
output_str = env.from_string(template_str).render(all_playlist_data=all_playlist_data,playlist_title=playlist_title)
with open("playlist.m3u", "w") as playlist_file:
    playlist_file.write(output_str)

