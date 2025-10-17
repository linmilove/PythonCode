#修改自：https://github.com/xsrazy/Download-All-Tiktok-Videos

import requests
from bs4 import BeautifulSoup
from concurrent import futures
from tqdm import tqdm
import argparse
import os
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.4',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://tmate.cc',
    'Connection': 'keep-alive',
    'Referer': 'https://tmate.cc/',
}

parser = argparse.ArgumentParser(description="Download-All-Tiktok-Videos: A simple script that downloads TikTok videos concurrently.")
watermark_group = parser.add_mutually_exclusive_group()
parser.add_argument("--links", default=r"links.txt", help="The path to the .txt file that contains the TikTok links. (Default: links.txt)")
watermark_group.add_argument("--no-watermark", action="store_true", help="Download videos without watermarks. (Default)")
watermark_group.add_argument("--watermark", action="store_true", help="Download videos with watermarks.")
parser.add_argument("--workers", default=3, help="Number of concurrent downloads. (Default: 3)", type=int)

args = parser.parse_args()


with open(args.links, "r") as links:
    tiktok_links = links.read().split("\n")

    def download(link):
        with requests.Session() as s:
            try:
                response = s.get("https://tmate.cc/", headers=headers)

                soup = BeautifulSoup(response.content, 'html.parser')
                token = soup.find("input", {"name": "token"})["value"]

                data = {'url': link, 'token': token,}

                response = s.post('https://tmate.cc/action', headers=headers, data=data)

                raw =response.content  # 返回内容
                data = json.loads(raw.decode('utf-8'))
                html = data["data"]



                soup = BeautifulSoup(html, 'html.parser')

                if args.no_watermark:
                    download_link = soup.find(class_="downtmate-right is-desktop-only right").find_all("a")[0]["href"]
                elif args.watermark:
                    download_link = soup.find(class_="downtmate-right is-desktop-only right").find_all("a")[3]["href"]
                else:
                    download_link = soup.find(class_="downtmate-right is-desktop-only right").find_all("a")[0]["href"]

                response = requests.get(download_link, stream=True, headers=headers)

                file_size = int(response.headers.get("content-length", 0))
                file_name = link.split("/")[-1]
                folder_name = link.split("/")[-3]

                # if not os.path.exists(folder_name):
                #     os.mkdir(folder_name)
                #     print("Folder created:", folder_name)
                file_name=file_name.split('?')[0]+".mp4"
                download_video(download_link, f"{file_name}.mp4")

                # with open(f"{folder_name}/{file_name}.mp4", 'wb') as video_file, tqdm(
                
                #     total=file_size,
                #     unit='iB',
                #     unit_scale=True,
                #     unit_divisor=1024,
                #     bar_format='{percentage:3.0f}%|{bar:20}{r_bar}{desc}', colour='green', desc=f"[{file_name}]"
                # ) as progress_bar:
                #     for data in response.iter_content(chunk_size=1024):
                #         size = video_file.write(data)
                #         progress_bar.update(size)
            except:
                with open("errors.txt", 'a') as error:
                    error.write(link + "\n")


def download_video(url: str, filename: str):
    resp = requests.get(url)
    resp.raise_for_status()  # 检查是否返回错误
    # 将二进制内容写入本地文件
    with open(filename, "wb") as f:
        f.write(resp.content)

    print(f"视频已保存为 {filename}")

def download_video2(url: str, filename: str):
    # 用流式请求，避免一次性把整个视频加载到内存里
    resp = requests.get(url, stream=True)
    resp.raise_for_status()  # 如果发生 HTTP 错误（如 404、403），抛异常

    with open(filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024*1024):  # 每次读 1 MB
            if chunk:
                f.write(chunk)

    print(f"视频已保存为 {filename}")



if __name__ == "__main__":                
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        executor.map(download, tiktok_links)
