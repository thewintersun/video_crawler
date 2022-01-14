
## How to use
- Clone the repo
``` sh
git clone https://github.com/thewintersun/video_crawler.git
```

- Install require package
``` sh
apt install python3-opencv
pip3 install --upgrade pip
python3 -m pip install opencv-python
pip3 install -r requirements.txt
```
- Prepare bilibili url list file

The file conntent must be url list. The url must the mainpage of the account.
The format is like this:

``` sh
https://space.bilibili.com/6733376?spm_id_from=333.788.b_765f7570696e666f.1
https://space.bilibili.com/319762851?spm_id_from=333.788.b_765f7570696e666f.1
https://space.bilibili.com/520155988?spm_id_from=333.788.b_765f7570696e666f.1
https://space.bilibili.com/419452613?spm_id_from=333.788.b_765f7570696e666f.1
https://space.bilibili.com/510856133?spm_id_from=333.788.b_765f7570696e666f.1
```

- run 
```sh
python3 bilibili.py urllistfile output_dir -n 4

'-n 4' represents 4 concurrent tasks to download
```
