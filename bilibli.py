import json
import logging
import math
import multiprocessing
import os
import re
import argparse
import time
import utils


def get_account_id(url):
    '''
    :arget count id from original bilibili url
    :param url:  文本中人工找到的url
    :return: account_id
    '''
    matches = re.findall('https://space.bilibili.com/(\d+)', url)
    if matches is not None:
        return matches[0]
    else:
        return ""


def get_accout_videoinfo(jsonstr):
    """
    通过jsonstr数据获取视频id的列表，视频数量，页数
    :param jsonstr: 通过api获取到的jsonstr数据
    :return: video id list, total video number, page number
    """
    json_data = json.loads(jsonstr)
    video_id_list = []
    total_video_number = 0
    video_number_one_page = 1
    if 'code' in json_data and json_data['code'] == 0 \
            and json_data['data'] != "":
        if json_data['data']['list'] != '' and json_data['data']['list']['vlist'] != '':
            # add video_list
            for video_list in json_data['data']['list']['vlist']:
                video_id_list.append(video_list['bvid'])
        if 'page' in json_data['data'] and json_data['data']['page'] != '':
            page_info = json_data['data']['page']
            total_video_number = page_info['count']
            video_number_one_page = page_info['ps']
    return video_id_list, total_video_number, video_number_one_page



class BiliBiliSpider(object):
    def __init__(self, args):

        self.process_num = args.n

        self.input_file = args.input_file

        # 输出文件夹
        self.output_dir = args.output_dir

        self.low_res_ratio = args.low_res_ratio

        self.cut_ratio = args.cut_ratio

        self.crawled_account_id_file = os.path.join(self.output_dir, 'temp_account_crawled')
        self.crawled_video_id_file = os.path.join(self.output_dir, 'temp_video_crawled')
        self.skip_file = os.path.join(self.output_dir, 'temp_skip')

        # 保存已经爬取过的账号id
        self.crawled_account_dict = multiprocessing.Manager().dict()

        # 保存已经爬取过的视频id
        self.crawled_video_dict = multiprocessing.Manager().dict()

        self.skip_video_dict = multiprocessing.Manager().dict()

        self.input_list = multiprocessing.Manager().list()

    def load_data(self):
        # 载入link到内存
        try:
            if os.path.exists(self.crawled_account_id_file):
                with open(self.crawled_account_id_file, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        self.crawled_account_dict[line] = 1
        except Exception as e:
            logging.error('Load crawled_account_id_file to crawled list: {}'.format(e))

        try:
            if os.path.exists(self.crawled_video_id_file):
                with open(self.crawled_video_id_file, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        line = line.split(' ')[1]
                        self.crawled_video_dict[line] = 1
        except Exception as e:
            logging.error('Load crawled_video_id_file to crawled list: {}'.format(e))

        try:
            if os.path.exists(self.input_file):
                with open(self.input_file, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        self.input_list.append(line)
            else:
                logging.warning("input file not exist. {}".format(self.input_file))
                exit(1)
        except Exception as e:
            logging.error('Load input_list: {}'.format(e))


        try:
            if os.path.exists(self.skip_file):
                with open(self.skip_file, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        self.skip_video_dict[line] = 1
        except Exception as e:
            logging.error('Load skip_file : {}'.format(e))

        logging.warning("Load data success")
        logging.warning("{} video already download".format(len(self.crawled_video_dict)))
        logging.warning("{} input url already download".format(len(self.input_list)))

    def save_crawled_video(self, account_id, video_id):
        try:
            with open(self.crawled_video_id_file, 'a') as fw:
                fw.write(account_id + ' ' + video_id + '\n')
        except Exception as e:
            logging.error('Save crawled video_id：{}'.format(e))

    def save_crawled_account(self, account_id):
        try:
            with open(self.crawled_account_id_file, 'a') as fw:
                fw.write(account_id + '\n')
        except Exception as e:
            logging.error('Save crawled account_id：{}'.format(e))

    def run(self):
        # 多进程主循环
        while True:
            try:
                if len(self.input_list) == 0:
                    logging.warning("all data process over, exit.")
                    break
                accout_url = self.input_list.pop(0)
                accout_id = get_account_id(accout_url)

                if accout_id in self.crawled_account_dict:
                    logging.warning("account : {} already crawled, next one".format(accout_id))
                    continue

                output_dir = os.path.join(self.output_dir, accout_id)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)

                logging.warning("Processing account {}".format(accout_id))
                page_id = 1
                total_page_number = 1000000
                while page_id <= total_page_number:
                    api_url = "https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&tid=0&pn={}&keyword=&order=pubdate&jsonp=jsonp".format(
                        accout_id, page_id)
                    logging.warning(api_url)
                    json_str = utils.get_html(api_url)
                    # 这些json数据里会获取到以下信息： 本页视频的id列表，一页有多少个视频，一共有多少个视频
                    video_id_list, total_video_number, video_number_one_page = get_accout_videoinfo(json_str)
                    total_page_number = math.ceil(total_video_number / video_number_one_page)

                    for video_id in video_id_list:
                        if video_id in self.crawled_video_dict:
                            logging.warning("video_id : {} already crawled, next one".format(video_id))
                            continue
                        if video_id in self.skip_video_dict:
                            logging.warning("video_id : {} skip , next one".format(video_id))
                            continue

                        video_url = "https://www.bilibili.com/video/" + video_id
                        logging.warning("Downloading video {}, url: {}".format(video_id, video_url))

                        video_output_dir = os.path.join(output_dir, video_id)

                        ret = utils.download_video(video_url, video_output_dir, self.low_res_ratio)

                        self.save_crawled_video(accout_id, video_id)

                        if ret != 0:
                            continue

                        if self.cut_ratio < 1.0:
                            utils.cut_video_dir(video_output_dir, self.cut_ratio)
                    page_id += 1
                self.save_crawled_account(accout_id)

            except Exception as e:
                logging.critical('un-exception error: {}'.format(e))

    def start(self):
        self.load_data()
        processes = []
        for i in range(self.process_num):
            t = multiprocessing.Process(target=self.run, args=())
            t.start()
            processes.append(t)

        for t in processes:
            t.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='输入的up主主页地址列表文件')
    parser.add_argument('output_dir', help='输出文件夹路径，末尾不要带斜杠')
    parser.add_argument('-n', help='多进程数量（默认为1）', type=int, default=1)
    parser.add_argument('-low_res_ratio', help='是否开启低分辨率下载。有时候下载低分辨率有问题，需要下载默认的',  default=1)
    parser.add_argument('--cut_ratio', help='因为只需要字幕，节省存储资源，将视频画面裁剪，保留底部开始的比例', type=float, default=0.3)
    parser.add_argument('--log', help='输出log到文件，否则输出到控制台', action='store_true')
    args = parser.parse_args()

    log_flag = args.log
    if log_flag:
        log_flag = args.output_dir + '/log.txt'

    logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s',
                        level=logging.DEBUG, filename=log_flag)

    spider = BiliBiliSpider(args)
    spider.start()


def test():
    matches = re.findall('https://space.bilibili.com/(\d+)', 'https://space.bilibili.com/300750508/video')
    print(matches)

if __name__ == "__main__":
    main()

