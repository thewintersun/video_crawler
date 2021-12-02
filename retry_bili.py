import argparse
import logging

import utils
import os
import codecs

# 过滤视频文件夹，如果是空的，则重新下载一次
already_download_account = "temp_account_crawled"
crawled_video_id_file = "temp_video_crawled"


def save_crawled_video(crawled_video_id_path, account_id, video_id):
    try:
        with open(crawled_video_id_path, 'a') as fw:
            fw.write(account_id + ' ' + video_id + '\n')
    except Exception as e:
        logging.error('Save crawled video_id：{}'.format(e))


def retry_download(data_dir):
    downloaded_account = os.path.join(data_dir, already_download_account)
    with codecs.open(downloaded_account, 'r', 'utf-8') as fr:
        for line in fr:
            line = line.strip()
            account_dir = os.path.join(data_dir, line)
            for vdir in os.listdir(account_dir):
                vdir_path = os.path.join(account_dir, vdir)
                if os.path.isdir(vdir_path):
                    #判断文件夹是否为空
                    if not os.listdir(vdir_path):
                        print(vdir_path)
                        url = "https://www.bilibili.com/video/" + vdir
                        save_dir = vdir_path
                        ret = utils.download_video(url, save_dir, 1)
                        if ret == 0:
                            utils.cut_video_dir(save_dir, 0.3)
                            crawled_video_id_path = os.path.join(data_dir, crawled_video_id_file)
                            save_crawled_video(crawled_video_id_path, line, vdir)
                        else:
                            print("downlaod fail {}".format(url))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='输入的up主主页地址列表文件')
    args = parser.parse_args()
    retry_download(args.input_dir)
