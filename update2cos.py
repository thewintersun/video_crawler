import os.path

import configinfo
import logging
import argparse
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


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
        self.upload_file_list = os.path.join(self.upload_dir, "temp_video_crawled")
        self.uploaded_file_list = os.path.join(self.upload_dir, "uploaded_list")

        self.upload_list = []
        self.uploaded_dict = {}

        self.bucket_name = 'ml-data-1301298951'

    def load_data(self):
        try:
            if os.path.exists(self.upload_file_list):
                with open(self.upload_file_list, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        self.upload_list.append(line)
        except Exception as e:
            logging.error('Load upload_file_list : {}'.format(e))

        try:
            if os.path.exists(self.uploaded_file_list):
                with open(self.uploaded_file_list, 'r') as fr:
                    for line in fr:
                        line = line.strip()
                        line = line.split(' ')[1]
                        self.uploaded_dict[line] = 1
        except Exception as e:
            logging.error('Load uploaded_list : {}'.format(e))

    def upload(self):
        self.load_data()
        for line in self.upload_list:
            line = line.strip()
            if line in self.uploaded_dict:
                continue

            account_id, video_id = line.split()
            src_dir = os.path.join(self.upload_dir, account_id)
            src_dir = os.path.join(src_dir, video_id)

            for files in os.listdir(src_dir):
                src_path = os.path.join(src_dir, files)
                dest_path = 'audio/video/bilibili/' + account_id + '/' + video_id + '/' + files

                logging.info("Uploading file {}".format(src_path))

                response = self.client.upload_file(
                    Bucket=self.bucket_name,
                    LocalFilePath= src_path,
                    Key=dest_path,
                    PartSize=1,
                    MAXThread=10,
                    EnableMD5=False
                )
                print(response['ETag'])
            self.save_uploaded_list(line)

    def save_uploaded_list(self, line):
        with open(self.uploaded_file_list, 'a') as fw:
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
