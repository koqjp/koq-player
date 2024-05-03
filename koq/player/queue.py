class PlayingQueueItem:
    def __init__(self, url: str, title: str, requester: str):
        self.url = url
        self.title = title
        self.requester = requester

    def __str__(self):
        return f"{self.title} - Requested by {self.requester}"


class PlayingQueue:
    def __init__(self):
        self.items = []

    def append(self, url: str, title: str, requester: str):
        self.items.append(PlayingQueueItem(url=url, title=title, requester=requester))

    def pop(self):
        return self.items.pop(0)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return "\n".join([str(item) for item in self.items])
