
import requests, re, os, concurrent.futures


class YoutubeData():
    def __init__(self):
        self.liveChannels = []

    def requestData(self, url, login):
        r = requests.get(url).text

        try:
            name = re.search("link itemprop=\"name\" content=\"(.*?)\">", r).group(1)
            image = re.search("url\":\"(https://yt3.{1,150})=s", r).group(1).replace("ggpht", "googleusercontent") + "=s100"
            #"livedvr" often is only present with 1 livestream, which will filter out recommendations. A channel with more than 1 livestream has no recommendations, then we should get live ids with "hqdefault_live", as it is "hqdefault" in past livestreams
            oneStream = re.search("isLiveDvrEnabled.*/vi/([A-Za-z0-9_\-]{11})(/hqdefault_live|.{1,1000}playerAnnotations)", r)
            oneStreamAuthor = re.search("/vi/([A-Za-z0-9_\-]{11})/hqdefault_live.{1,2000}author\":\""+name+"", r)
            manyStreamsThumb = set(re.findall("/vi/([A-Za-z0-9_\-]{11})/hqdefault_live", r))

            if oneStream:
                videoId = [oneStream.group(1)]
            elif oneStreamAuthor:
                videoId = [oneStreamAuthor.group(1)]
            else:
                videoId = manyStreamsThumb
        except:
            videoId = []

        data = []
        for i in videoId:
            r = requests.post("https://www.youtube.com/youtubei/v1/updated_metadata?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false", data = """{"context":{"client":{"clientName":"WEB","clientVersion":"2.20230420.00.00"}},"videoId":"""+f'"{i}"'+"""}""").text
            data.append([r, login, name, image, i])
        return data


    def getData(self, channels, count):
        self.liveChannels = []

        with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
            futures = [executor.submit(self.requestData, "https://www.youtube.com/@"+channel+"/live", channel) for channel in channels]

            for n, future in enumerate(concurrent.futures.as_completed(futures)):
                if n == 1:
                    count.show()
                count.setText("Youtube - " + str(n + 1) + " / " + str(len(channels)))

                for data in future.result():
                    if data and not "waiting" in data[0]:
                        r = data[0]
                        viewers = re.search("simpleText\":\"(.*?) watching now", r)
                        viewers = int(viewers.group(1).replace(",", "")) if viewers else -1
                        title = re.search("runs\":\[{\"text\":\"(.*?)\"}", r).group(1)
                        login = data[1]


                        self.liveChannels.append({"platform": "youtube", "stream": "https://www.youtube.com/watch?v="+data[4]+"", "login": login, "channel": data[2], "title": title, "viewers": viewers, "game": ""})


                        if not os.path.exists("images/youtube"):
                            os.makedirs("images/youtube")
                        if not os.path.exists("images/youtube/"+login+".png"):
                            self.getImage(r, login, data[3])
                        elif os.path.getsize("images/youtube/"+login+".png") == 0:
                            self.getImage(r, login, data[3])


    def getImage(self, r, login, image):
        try:
            with open("images/youtube/"+login+".png", "wb") as f:
                f.write(requests.get(image).content)
        except:
            pass