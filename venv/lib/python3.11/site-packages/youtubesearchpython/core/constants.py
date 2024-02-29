requestPayload = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20210224.06.00",
            "newVisitorCookie": True,
        },
        "user": {
            "lockedSafetyMode": False,
        }
    }
}
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

videoElementKey = 'videoRenderer'
channelElementKey = 'channelRenderer'
playlistElementKey = 'playlistRenderer'
shelfElementKey = 'shelfRenderer'
itemSectionKey = 'itemSectionRenderer'
continuationItemKey = 'continuationItemRenderer'
playerResponseKey = 'playerResponse'
richItemKey = 'richItemRenderer'
hashtagElementKey = 'hashtagTileRenderer'
hashtagBrowseKey = 'FEhashtag'
hashtagVideosPath = ['contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content',
                     'richGridRenderer', 'contents']
hashtagContinuationVideosPath = ['onResponseReceivedActions', 0, 'appendContinuationItemsAction', 'continuationItems']
searchKey = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
contentPath = ['contents', 'twoColumnSearchResultsRenderer', 'primaryContents', 'sectionListRenderer', 'contents']
fallbackContentPath = ['contents', 'twoColumnSearchResultsRenderer', 'primaryContents', 'richGridRenderer', 'contents']
continuationContentPath = ['onResponseReceivedCommands', 0, 'appendContinuationItemsAction', 'continuationItems']
continuationKeyPath = ['continuationItemRenderer', 'continuationEndpoint', 'continuationCommand', 'token']
playlistInfoPath = ['response', 'sidebar', 'playlistSidebarRenderer', 'items']
playlistVideosPath = ['response', 'contents', 'twoColumnBrowseResultsRenderer', 'tabs', 0, 'tabRenderer', 'content',
                      'sectionListRenderer', 'contents', 0, 'itemSectionRenderer', 'contents', 0,
                      'playlistVideoListRenderer', 'contents']
playlistPrimaryInfoKey = 'playlistSidebarPrimaryInfoRenderer'
playlistSecondaryInfoKey = 'playlistSidebarSecondaryInfoRenderer'
playlistVideoKey = 'playlistVideoRenderer'


class ResultMode:
    json = 0
    dict = 1


class SearchMode:
    videos = 'EgIQAQ%3D%3D'
    channels = 'EgIQAg%3D%3D'
    playlists = 'EgIQAw%3D%3D'
    livestreams = 'EgJAAQ%3D%3D'


class VideoUploadDateFilter:
    lastHour = 'EgQIARAB'
    today = 'EgQIAhAB'
    thisWeek = 'EgQIAxAB'
    thisMonth = 'EgQIBBAB'
    thisYear = 'EgQIBRAB'


class VideoDurationFilter:
    short = 'EgQQARgB'
    long = 'EgQQARgC'


class VideoSortOrder:
    relevance = 'CAASAhAB'
    uploadDate = 'CAISAhAB'
    viewCount = 'CAMSAhAB'
    rating = 'CAESAhAB'


class ChannelRequestType:
    info = "EgVhYm91dA%3D%3D"
    playlists = "EglwbGF5bGlzdHMYAyABcAA%3D"


CLIENTS = {
    "MWEB": {
        'context': {
            'client': {
                'clientName': 'MWEB',
                'clientVersion': '2.20211109.01.00'
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    },
    "ANDROID": {
        'context': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '16.20'
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    },
    "ANDROID_EMBED": {
        'context': {
            'client': {
                'clientName': 'ANDROID',
                'clientVersion': '16.20',
                'clientScreen': 'EMBED'
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    },
    "TV_EMBED": {
        "context": {
            "client": {
                "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
                "clientVersion": "2.0"
            },
            "thirdParty": {
                "embedUrl": "https://www.youtube.com/",
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    }
}