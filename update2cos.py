import os.path

import configinfo
import logging
import argparse
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import utils
import codecs

class CosClient(object):
    def __init__(self, args):
        secret_id = configinfo.COS_SID      # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
        secret_key = configinfo.COS_SKEY    # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
        region = configinfo.COS_REGION      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
        # COS支持的所有region列表参见https://www.qcloud.com/document/product/436/6224
        token = None
        # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
        scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        self.client = CosS3Client(config)

        self.upload_dir = args.upload_dir
        self.account_crawled_file = os.path.join(self.upload_dir, "temp_account_crawled")
        self.uploaded_file_list = os.path.join(self.upload_dir, "uploaded_list")
        self.meta_file = os.path.join(self.upload_dir, "meta_info")

        self.account_crawled_list = []
        self.uploaded_dict = {}

        self.bucket_name = 'ml-data-1301298951'

    def load_data(self):
        try:
            if os.path.exists(self.account_crawled_file):
                with codecs.open(self.account_crawled_file, 'r', 'utf-8') as fr:
                    for line in fr:
                        line = line.strip()
                        self.account_crawled_list.append(line)
        except Exception as e:
            logging.error('Load upload_file_list : {}'.format(e))

        try:
            if os.path.exists(self.uploaded_file_list):
                with codecs.open(self.uploaded_file_list, 'r', 'utf-8') as fr:
                    for line in fr:
                        line = line.strip()
                        self.uploaded_dict[line] = 1
        except Exception as e:
            logging.error('Load uploaded_list : {}'.format(e))

    def upload(self):
        self.load_data()
        file_suffix_list = ['mp4', 'flv']
        for line in self.account_crawled_list:
            account_id = line.strip()
            account_path = os.path.join(self.upload_dir, account_id)
            if not os.path.exists(account_path):
                logging.error(account_path + "not exist")
                continue

            for video_id in os.listdir(account_path):

                src_dir = os.path.join(account_path, video_id)
                if not os.path.isdir(src_dir):
                    continue

                for files in os.listdir(src_dir):
                    file_suffix = files.split('.')[-1]
                    file_prefix = '.'.join(files.split('.')[:-1])
                    tag = account_id + "_" + video_id + "_" + file_prefix
                    if tag in self.uploaded_dict:
                        continue

                    if file_suffix in file_suffix_list:
                        file_prefix = file_prefix.replace("-", "_")
                        src_path = os.path.join(src_dir, files)
                        wav_src_path = os.path.join(src_dir, file_prefix+".wav")

                        utils.video2wav(src_path, wav_src_path)

                        cos_dir = 'audio/video/bilibili/'

                        cos_video_dest_path = cos_dir + account_id + '/' + video_id + '/' + file_prefix+ "." + file_suffix
                        cos_wav_dest_path = cos_dir + account_id + '/' + video_id + '/' + file_prefix+".wav"

                        logging.warning("Uploading file {}".format(src_path))

                        response = self.client.upload_file(
                            Bucket=self.bucket_name,
                            LocalFilePath= src_path,
                            Key=cos_video_dest_path,
                            PartSize=1,
                            MAXThread=10,
                            EnableMD5=False
                        )

                        response = self.client.upload_file(
                            Bucket=self.bucket_name,
                            LocalFilePath=wav_src_path,
                            Key=cos_wav_dest_path,
                            PartSize=1,
                            MAXThread=10,
                            EnableMD5=False
                        )

                        meta_line = tag + " https://" + self.bucket_name + ".cos." + configinfo.COS_REGION + ".myqcloud.com/" \
                                + cos_dir + account_id + '/' + video_id + "/" + file_prefix+ "." + file_suffix
                        logging.info(meta_line)
                        self.save_meta_info(meta_line)
                        self.save_uploaded_list(tag)
                        self.uploaded_dict[tag] = 1
                    else:
                        logging.info("file suffix not video format: {}".format(files))

    def save_uploaded_list(self, line):
        with codecs.open(self.uploaded_file_list, 'a', 'utf-8') as fw:
            line = line.strip()
            fw.write(line + '\n')

    def save_meta_info(self, line):
        with codecs.open(self.meta_file, 'a', 'utf-8') as fw:
            line = line.strip()
            fw.write(line + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('upload_dir', help='之前下载的文件夹，会将这个文件夹下的文件上传到cos上')
    parser.add_argument('--log', help='输出log到文件，否则输出到控制台', action='store_true')
    args = parser.parse_args()

    log_flag = args.log
    if log_flag:
        log_flag = args.upload_dir + '/log.txt'

    logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s',
                        level=logging.DEBUG, filename=log_flag)

    client = CosClient(args)
    client.upload()

if __name__ == "__main__":
    main()
