
import requests, re, os, concurrent.futures


class TwitchData():
    def __init__(self):
        self.liveChannels = []

    def requestData(self, data):
        r = requests.post("https://gql.twitch.tv/gql", data = data, headers = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko", "Connection": "close"})
        return r

    def getData(self, channels, progress):
        self.liveChannels = []
        dataList = ["""[{"operationName":"ChannelShell","variables":{"login":"""+f'"{channel}"'+"""},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"580ab410bcd0c1ad194224957ae2241e5d252b2c5173d8e0cce9d32d5bb14efe"}}}, {"operationName":"ComscoreStreamingQuery","variables":{"channel":"""+f'"{channel}"'+""","clipSlug":"","isClip":false,"isLive":true,"isVodOrCollection":false,"vodID":""},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"e1edae8122517d013405f237ffcc124515dc6ded82480a88daef69c83b53ac01"}}}]""" for channel in channels]


        with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
            futures = [executor.submit(self.requestData, data) for data in dataList]

            for n, future in enumerate(concurrent.futures.as_completed(futures)):
                progress.setText(str(n + 1) + " / " + str(len(channels)))
                r = future.result().text

                if not any(i in r for i in ["userDoesNotExist", 'stream":null']):
                    channel = re.search('Name":"(.*?)",', r).group(1)
                    viewers = int(re.search('viewersCount":(\d*)', r).group(1))
                    title = re.search('title":"(.*?)","', r).group(1)
                    game = re.search('"name":"(.*?)",', r)
                    game = game.group(1) if game else ""

                    self.liveChannels.append({"channel": channel, "title": title, "viewers": viewers, "game": game})
  

                    if not os.path.exists("images"):
                        os.makedirs("images")
                    if not os.path.exists("images/"+channel+".png"):
                        self.getImage(r, channel)
                    elif os.path.getsize("images/"+channel+".png") == 0:
                        self.getImage(r, channel)


    def getImage(self, r, channel):
        try:
            with open("images/"+channel+".png", "wb") as f:
                f.write(requests.get(re.search('profileImageURL":"(.*?)","', r).group(1)).content)
        except:
            pass




