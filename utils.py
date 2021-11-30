#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import random
import logging
import string
import subprocess
import sys
import time

import cv2
import os
import requests
from you_get import common as you_get


CHINESE_PUNC_STOP = '！？｡。'
CHINESE_PUNC_NON_STOP = '＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏'
CHINESE_PUNC_OTHER = '·〈〉-'
CHINESE_PUNC_LIST = CHINESE_PUNC_STOP + CHINESE_PUNC_NON_STOP + CHINESE_PUNC_OTHER

def str_trans(input_text):
    old_chars = CHINESE_PUNC_LIST + string.punctuation  # includes all CN and EN punctuations
    new_chars = ' ' * len(old_chars)
    del_chars = ''
    output_text = input_text.translate(str.maketrans(old_chars, new_chars, del_chars))
    return ''.join(output_text.split())

# User Agent 列表，每次访问随机使用其中一个
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari"
    "/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome"
    "/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari"
    "/535.24",
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; Info'
    'Path.2; MS-RTC LM 8)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; Info'
    'Path.2)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0 Zune 3.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 4.0.20402; MS-RTC LM 8)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; InfoPath.2)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET C'
    'LR 3.5.30729; .NET CLR 3.0.30729)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0; .NET CLR 2.0.50727; S'
    'LCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Tablet PC 2.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0; .NET CLR 2.0.50727; S'
    'LCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 3.0.04506; Media Cen'
    'ter PC 5.0; SLCC1)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0; .NET CLR 2.0.50727; S'
    'LCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30'
    '729; .NET CLR 3.0.30729; Media Center PC 6.0; Tablet PC 2.0; .NET CLR 3.0.04506; Media Center PC 5.0; S'
    'LCC1)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30'
    '729; .NET CLR 3.0.30729; Media Center PC 6.0; FDM; Tablet PC 2.0; .NET CLR 4.0.20506; OfficeLiveConnec'
    'tor.1.4; OfficeLivePatch.1.3)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30'
    '729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 3.0.04506; Media Center PC 5.0; SLCC1; Tab'
    'let PC 2.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30'
    '729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET CLR 1.1.4322; InfoPath.2)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.3'
    '0729; .NET CLR 3.0.3029; Media Center PC 6.0; Tablet PC 2.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .N'
    'ET CLR 3.0.04506.30)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; Media Center PC 3.0; .NET CLR 1.0.3705; .NET CLR 1.1.4'
    '322; .NET CLR 2.0.50727; InfoPath.1)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; FDM; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; InfoPath.1; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; InfoPath.1)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; Alexa Toolbar)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.40607)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1; .NET CLR 1.0.3705; Media Center PC 3.1; Alexa Tool'
    'bar; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; el-GR)',
    'Mozilla/5.0 (MSIE 7.0; Macintosh; U; SunOS; X11; gu; SV1; InfoPath.2; .NET CLR 3.0.04506.30; .NET C'
    'LR 3.0.04506.648)',
    'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; SLCC1; .NET CLR 2.0.50727; Media Cen'
    'ter PC 5.0; c .NET CLR 3.0.04506; .NET CLR 3.5.30707; InfoPath.1; el-GR)',
    'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Cen'
    'ter PC 5.0; c .NET CLR 3.0.04506; .NET CLR 3.5.30707; InfoPath.1; el-GR)',
    'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; fr-FR)',
    'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 6.0; en-US)',
    'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.2; WOW64; .NET CLR 2.0.50727)',
    'Mozilla/4.79 [en] (compatible; MSIE 7.0; Windows NT 5.0; .NET CLR 2.0.50727; InfoPath.2; .NET C'
    'LR 1.1.4322; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648)',
    'Mozilla/4.0 (Windows; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (Mozilla/4.0; MSIE 7.0; Windows NT 5.1; FDM; SV1; .NET CLR 3.0.04506.30)',
    'Mozilla/4.0 (Mozilla/4.0; MSIE 7.0; Windows NT 5.1; FDM; SV1)',
    'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET C'
    'LR 3.0.30729; Media Center PC 6.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0;)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; YPC 3.2.0; SLCC1; .NET CLR 2.0.50727; Media Cen'
    'ter PC 5.0; InfoPath.2; .NET CLR 3.5.30729; .NET CLR 3.0.30618)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; YPC 3.2.0; SLCC1; .NET CLR 2.0.50727; .NET C'
    'LR 3.0.04506)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; SLCC1; Media Center PC 5.0; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; SLCC1; .NET CLR 3.0.04506)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; SLCC1; .NET CLR 2.0.50727; Media Cen'
    'ter PC 5.0; InfoPath.2; .NET CLR 3.5.30729; .NET CLR 3.0.30618; .NET CLR 1.1.4322)',
]

def get_html(url):
    """
    获取URL的源代码
    :param url: 网址
    :return: 网页源代码
    """
    attempts = 0
    attempts_times = 20
    while attempts < attempts_times:
        try:
            headers = {'user-agent': random.choice(USER_AGENT_LIST)}
            req = requests.get(url, timeout=20, headers=headers)
            html = req.text
            return html
        except Exception as e:
            attempts = attempts + 1
            if attempts == attempts_times:
                logging.error('Get html: {0}: {1}'.format(e, url))
                return ''


def remove_html_tag(html):
    # 去掉正文里夹带的HTML标签
    if html:
        html = html.strip()
        dr = re.compile(r'<[^>]+>', re.S)
        html = dr.sub('', html)
    return html


def save_content(path, content, mode):
    """
    保存文本
    :param path: 保存的文件路径
    :param content: 内容
    :param mode: save模式， 'a' 或者 'w'
    """
    try:
        with open(path, mode, encoding='utf-8') as fw:
            fw.write(content)
    except Exception as e:
        logging.error('Save content with {1} mode: {0}'.format(e, mode))

def cut_video(input_path, output_path, cut_ratio):
    logging.info("opencv cut : {}".format(input_path))

    video_capture = cv2.VideoCapture(input_path)
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)

    height_start = int(height * (1 - cut_ratio))
    height_end = int(height)
    new_height = height - height_start

    size = (int(width), int(new_height))
    videp_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    have_more_frame, frame_src = video_capture.read()
    while have_more_frame:
        frame_src2 = frame_src[height_start:height_end, 0:int(width)]  # 注意这里是高宽
        videp_writer.write(frame_src2)
        have_more_frame, frame_src = video_capture.read()
    videp_writer.release()
    video_capture.release()

def cut_video_ffmpeg(input_path, output_path, cut_ratio):
    logging.warning("ffmpeg cut : {}".format(input_path))

    video_capture = cv2.VideoCapture(input_path)
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    height_start = int(height * (1 - cut_ratio))
    new_height = height - height_start

    cmd_str = f'ffmpeg -i "' + input_path + '" -strict -2 -vf crop=' + str(width) + ':' + str(new_height) + ':0:' + str(height_start) + ' -y ' + output_path
    logging.warning(cmd_str)
    ret = subprocess.run(cmd_str, encoding="utf-8", shell=True)
    return ret.returncode


def cut_video_dir(dir, cut_ratio):
    '''
    裁剪一个文件夹下所有视频文件，保留底部开始一定比例
    :param dir:
    :param cut_ratio:
    :return:
    '''

    # same to not cut the video
    if cut_ratio == 1:
        return

    format_list = ['mp4', 'flv']

    for f in os.listdir(dir):

        file_name = '.'.join(f.split('.')[:-1])
        file_suffix = f.split('.')[-1]

        if file_suffix in format_list and not file_name.endswith('cut'):
            input_path = os.path.join(dir, f)
            print(input_path)
            output_filename = str_trans(file_name) + "_cut."+file_suffix
            output_path = os.path.join(dir, output_filename)

            ret = cut_video_ffmpeg(input_path, output_path, cut_ratio)
            if ret == 0:
                os.remove(input_path)


def download_video(url, save_dir, low_res_ratio):
    """
    通过you-get来下载某个视频到指定文件夹
    :param save_dir: 下载到的文件夹
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    if low_res_ratio == 0:
        cmd_str = f'you-get -f -o ' + save_dir + ' --playlist ' + url
        logging.warning(cmd_str)
        ret = subprocess.run(cmd_str, encoding="utf-8", shell=True)
        ret = ret.returncode
        # sleep 5 secs after every download
        time.sleep(5)
        #如果下载不成功，可能被限制了，sleep 100秒
        if ret != 0:
            logging.warning("download error : {} sleep 100s".format(url))
            time.sleep(100)
        return ret

    # low_res_ratio == 1
    opt_list = ['dash-flv480', 'dash-flv720', 'dash-flv1080']
    i = 0
    ret = 2
    while i < len(opt_list) and ret != 0:
        try:
            cmd_str = f'you-get -f -o ' + save_dir + ' --playlist -F ' + opt_list[i] + ' ' + url
            logging.warning(cmd_str)
            ret = subprocess.run(cmd_str, encoding="utf-8", shell=True)
            ret = ret.returncode
            # sleep 5 secs after every download
            time.sleep(5)
        except Exception as e:
            logging.error("download fail : {}".format(e))
        finally:
            i = i + 1
    return ret

def video2wav(input_path, output_path):
    logging.warning("video2wav : {}".format(input_path))
    cmd_str = f'ffmpeg -i "' + input_path + '" -ab 16 -ar 16000 -ac 1 -y "' + output_path + '"'
    logging.warning(cmd_str)
    ret = subprocess.run(cmd_str, encoding="utf-8", shell=True)
    return ret.returncode

if __name__ == "__main__":
    files = "c:\\work\\剧情和战斗超燃的国产漫画没做成动画实在是可惜_cut.mp4"
    file_suffix = files.split('.')[-1]
    file_prefix = '.'.join(files.split('.')[:-1])
    print(file_suffix)
    print(file_prefix)

    #video2wav("c:\\work\\剧情和战斗超燃的国产漫画没做成动画实在是可惜_cut.mp4", "c:\\work\\剧情和战斗超燃的国产漫画没做成动画实在是可惜_cut.wav")
    pass