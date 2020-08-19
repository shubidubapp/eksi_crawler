import aiofiles
import aiohttp
import argparse
import asyncio
import random
import re
import sys
from bs4 import BeautifulSoup
from file_read_backwards import FileReadBackwards


def continue_index(filename):
    f = FileReadBackwards(filename)
    last_line = f.__iter__().__next__()
    try:
        print(last_line)
        last_line = last_line.strip().replace('"', '').strip("}").strip("{").split(":", 1)  # because fuck.
        return int(last_line[0])
    except:
        print("Ups. There has been a problem with continue file. Please fix this shit.")
        sys.exit(-1)


class AsyncGenerator:
    def __init__(self, stop, start=0):
        self.i = start
        self.stop = stop

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self.i < self.stop:
            i = self.i
            self.i += 1
            return i
        else:
            raise StopAsyncIteration
    async def finish(self):
        self.i = self.stop


class EksiCrawler:
    def __init__(self, start_index=1, stop_index=100000000, thread_count=4, file_name="eksi_crawler_out.txt"):
        self.starting_index = start_index
        self.thread_count = thread_count
        self.try_limit = 3
        self.base_url = "https://eksisozluk.com/entry/"
        self.index_limit = stop_index
        self.file = file_name
        self.index_iterator = AsyncGenerator(start=self.starting_index, stop=self.index_limit)

    @staticmethod
    async def fetch(url, session):
        async with session.get(url) as response:
            # print(url)
            return await response.text(), response.status

    async def get_page(self, url, session):
        text = ""
        for i in range(self.try_limit):
            asyncio.sleep(random.randrange(15))
            try:
                text, status_code = await self.fetch(url, session)
                if status_code == 404:
                    return None
                elif text is None:
                    continue
                elif status_code == 200:
                    soup = BeautifulSoup(text, "html.parser")
                    entry = soup.find("div", {"class": "content"}).text
                    entry = re.sub("http.*\s", "", entry)
                    entry = re.sub("www.*\s", "", entry)
                    entry = re.sub("\(bkz(\S|\s)*\)", "", entry)
                    return entry
            except:
                asyncio.sleep(10)
                continue

    async def get(self, url, index, session):
        entry = await self.get_page(url, session)
        if entry is not None:
            # print(entry)
            async with aiofiles.open(self.file, "a", encoding="utf-8") as f:
                await f.write("{{\"{}\":\"{}\"}}\n".format(str(index), entry.strip()))
            return True
        return False

    async def thread_handler(self, session):
        while True:
            try:
                new_index = await self.index_iterator.__anext__()
                print("\r{:<30}".format(new_index), end="")
                await self.get(self.base_url + str(new_index), new_index, session)
            except StopAsyncIteration:
                return
    async def start(self):
        tasks = []
        async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
            for i in range(self.thread_count):
                task = asyncio.ensure_future(self.thread_handler(session))
                tasks.append(task)
            await asyncio.gather(*tasks)
    async def stop(self):
        await self.index_iterator.finish()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    file_n = sys.argv[0].replace(".py", "_out.txt") 
    parser.add_argument("-st", "--start", help="Starting entry number for crawler. (included) Default: 1",
                        default=1, type=int)
    parser.add_argument("-sp", "--stop", help="Stopping entry number for crawler. "
                                              "(not included) Default:  1 000 000 000", default=1000000000, type=int)
    parser.add_argument("-o", "--output", help="Output file name. Default: {}".format(file_n), default=file_n)
    parser.add_argument("-tc", "--thread-count", help="Limit the amount of threads created. Default: 4",
                        default=4, type=int)
    parser.add_argument("-c", "--continue-to-file", help="Continue with the stated file from last index outputs"
                                                         " to that file.")
    args = parser.parse_args()

    if args.continue_to_file:
        c_index = continue_index(args.continue_to_file)
        args.output = args.continue_to_file
        args.start = c_index
        print("Continuing from {}".format(c_index))

    if args.start < args.stop:
        crawler = EksiCrawler(start_index=args.start, stop_index=args.stop,
                              thread_count=args.thread_count, file_name=args.output)
        task = asyncio.ensure_future(crawler.start())
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            loop.run_until_complete(crawler.stop())
            task.close()
            loop.run_forever()
            task.exception()
        finally:
            loop.close()
    else:
        print("I think starting index should be smaller than stopping index. If you don't agree."
              " Well, change the code :)")
