import copy
import json
from typing import Union, List
from urllib.parse import urlencode
import time
import datetime
import pytz
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue, getVideoId


class ChannelCore(RequestCore):
    def __init__(self, channel_id: str, request_params: str):
        super().__init__()
        self.browseId = channel_id
        self.params = request_params
        self.result = {}
        self.continuation = None

    def prepare_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        if not self.continuation:
            self.data["params"] = self.params
            self.data["browseId"] = self.browseId
        else:
            self.data["continuation"] = self.continuation

    def playlist_parse(self, i) -> dict:
        return {
            "id": getValue(i, ["playlistId"]),
            "thumbnails": getValue(i, ["thumbnail", "thumbnails"]),
            "title": getValue(i, ["title", "runs", 0, "text"]),
            "videoCount": getValue(i, ["videoCountShortText", "simpleText"]),
            "lastEdited": getValue(i, ["publishedTimeText", "simpleText"]),
        }

    def parse_response(self):
        response = self.data.json()

        thumbnails = []
        try:
            thumbnails.extend(getValue(response, ["header", "c4TabbedHeaderRenderer", "avatar", "thumbnails"]))
            self.continuation = getValue(response,
                                       ["header", "c4TabbedHeaderRenderer", "tagline", "channelTaglineRenderer",
                                        "moreEndpoint", "showEngagementPanelEndpoint", "engagementPanel",
                                        "engagementPanelSectionListRenderer", "content", "sectionListRenderer",
                                        "contents", 0, "itemSectionRenderer", "contents", 0, "continuationItemRenderer",
                                        "continuationEndpoint", "continuationCommand", "token"])
        except:
            pass
        try:
            thumbnails.extend(getValue(response, ["metadata", "channelMetadataRenderer", "avatar", "thumbnails"]))
        except:
            pass
        try:
            thumbnails.extend(getValue(response, ["microformat", "microformatDataRenderer", "thumbnail", "thumbnails"]))
        except:
            pass

        playlists: list = []

        for tab in getValue(response, ["contents", "twoColumnBrowseResultsRenderer", "tabs"]):
            tab: dict
            title = getValue(tab, ["tabRenderer", "title"])
            if title == "Playlists":
                playlist = getValue(tab,
                                    ["tabRenderer", "content", "sectionListRenderer", "contents", 0,
                                     "itemSectionRenderer",
                                     "contents", 0, "gridRenderer", "items"])
                if playlist is not None and getValue(playlist, [0, "gridPlaylistRenderer"]):
                    for i in playlist:
                        if getValue(i, ["continuationItemRenderer"]):
                            self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint",
                                                             "continuationCommand", "token"])
                            break
                        i: dict = i["gridPlaylistRenderer"]
                        playlists.append(self.playlist_parse(i))

        subscribe = getValue(response,["header", "c4TabbedHeaderRenderer", "subscriberCountText", "simpleText"]).split(" sub")[0]
        if "K" in subscribe:
            subscribe = subscribe.split("K")[0].replace(",", "").replace(".", "") + "000"
        if "M" in subscribe:
            subscribe = subscribe.split("M")[0].replace(",", "").replace(".", "") + "0000"

        self.result = {
            "id": getValue(response, ["metadata", "channelMetadataRenderer", "externalId"]),
            "url": getValue(response, ["metadata", "channelMetadataRenderer", "channelUrl"]),
            "description": getValue(response, ["metadata", "channelMetadataRenderer", "description"]),
            "title": getValue(response, ["metadata", "channelMetadataRenderer", "title"]),
            "banners": getValue(response, ["header", "c4TabbedHeaderRenderer", "banner", "thumbnails"]),
            "subscribers": subscribe,
            "thumbnails": thumbnails,
            "availableCountryCodes": getValue(response,
                                              ["metadata", "channelMetadataRenderer", "availableCountryCodes"]),
            "isFamilySafe": getValue(response, ["metadata", "channelMetadataRenderer", "isFamilySafe"]),
            "keywords": getValue(response, ["metadata", "channelMetadataRenderer", "keywords"]),
            "tags": getValue(response, ["microformat", "microformatDataRenderer", "tags"]),
            "playlists": playlists,
        }

    def parse_next_response(self):
        response = self.data.json()

        self.continuation = None

        response = getValue(response,
                            ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"])
        for i in response:
            if getValue(i, ["continuationItemRenderer"]):
                self.continuation = getValue(i,
                                             ["continuationItemRenderer", "continuationEndpoint", "continuationCommand",
                                              "token"])
                break
            elif getValue(i, ['gridPlaylistRenderer']):
                self.result["playlists"].append(self.playlist_parse(getValue(i, ['gridPlaylistRenderer'])))
            # TODO: Handle other types like gridShowRenderer

    def about_data(self):
        response = self.data.json()

        joined_date = getValue(response,
                               ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction",
                                "continuationItems",
                                0, "aboutChannelRenderer", "metadata", "aboutChannelViewModel", "joinedDateText",
                                "content"]).split("Joined ")[1].replace(",", "").split(" ")

        jd_month = time.strptime(joined_date[0], '%b').tm_mon
        jd_day = joined_date[1]
        jd_year = joined_date[2]
        joined_date = datetime.datetime.strptime(f'{jd_day}-{jd_month}-{jd_year} 00:00:00', '%d-%m-%Y %H:%M:%S')
        self.result = {

            "views": getValue(response,
                              ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems",
                               0, "aboutChannelRenderer", "metadata", "aboutChannelViewModel", "viewCountText"]).split(" view")[0].replace(",", ""),
            "joinedDate": joined_date,
            "country": getValue(response,
                                ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems",
                                 0, "aboutChannelRenderer", "metadata", "aboutChannelViewModel", "country"]),
            "videos": getValue(response,
                               ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems",
                                0, "aboutChannelRenderer", "metadata", "aboutChannelViewModel", "videoCountText"]).split(" video")[0].replace(",", ""),
        }

    async def async_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = await self.asyncPostRequest()
        self.parse_next_response()

    def sync_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = self.syncPostRequest()
        self.parse_next_response()

    def has_more_playlists(self):
        return self.continuation is not None

    async def async_create(self):
        self.prepare_request()
        self.data = await self.asyncPostRequest()
        self.parse_response()

    def sync_create(self):
        self.prepare_request()
        self.data = self.syncPostRequest()
        self.parse_response()

    async def async_about(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = await self.asyncPostRequest()
        self.about_data()

    def sync_about(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = self.syncPostRequest()
        self.about_data()
