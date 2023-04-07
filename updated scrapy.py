import scrapy
import jmespath
import json
from pytube import YouTube


class YouTubeSpider(scrapy.Spider):
    name = 'youtube'
    def __init__(self, start_urls=None, *args, **kwargs):
        super(YouTubeSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_urls] if start_urls else ['https://www.youtube.com/watch?v=07qgoQngK2Q&list=PLs2Vk8lWLK7apJNVDWynflqjO1u8VyQiM&index=1&ab_channel=ElzeroWebSchool']
    def parse(self, response):
        try:
            main_json_str = response.xpath('//script[starts-with(text(), "var ytInitialData =")][1]').css("script::text").get().replace("var ytInitialData =", "").split(";")[0]
            main_json = json.loads(main_json_str)
            playlist_data = playlist_data= main_json["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]
            webCommandsurls = jmespath.search('[*].playlistVideoRenderer.navigationEndpoint.commandMetadata.webCommandMetadata.url',playlist_data)
            playlist_title = main_json["metadata"]["playlistMetadataRenderer"]["title"]
            base_url ="https://www.youtube.com"
            video_links =[f"{base_url}{webCommandurl}" for webCommandurl in webCommandsurls]
            indexs = jmespath.search('[*].playlistVideoRenderer.index.simpleText',playlist_data)
            videos_titles = jmespath.search('[*].playlistVideoRenderer.title.runs[0].text',playlist_data)
            yield {"title" : playlist_title}
            for video_link,index,video_title in zip(video_links,indexs,videos_titles):
                yield scrapy.Request(video_link, callback=self.post_result,meta={'index': index,'title':video_title})
        except json.decoder.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {e}")

    def post_result(self, response):
        try:
            index = response.meta.get('index')
            video_url = response.url
            video = YouTube(video_url) 
            main_json_str = response.xpath('//script[starts-with(text(), "var ytInitialData =")][1]').css("script::text").get().replace("var ytInitialData =", "").split(";")[0]
            main_json = json.loads(main_json_str)
            chanel_title = main_json["contents"]["twoColumnWatchNextResults"]["secondaryResults"]["secondaryResults"]["results"][0]["compactVideoRenderer"]["longBylineText"]["runs"][0]["text"]
            result = {
                "curtent_index": index,
               # "video_title": video.title, some times it return error like this "pytube.exceptions.PytubeError: Exception while accessing title of ..."
                "video_title" : response.meta.get('title'),
                "video_link": jmespath.search('formats[-1].url', video.streaming_data),
                "video_length": video.length * 1000, # convert to seconds
                "chanel_title": chanel_title
            }
            yield result
        except json.decoder.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {e}")
