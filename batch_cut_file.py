import utils
import os

def batch_cut_file(videoDir, cut_ratio):
    for d in os.listdir(videoDir):
        account_dir = os.path.join(videoDir, d)
        if os.path.isdir(account_dir):
            for subd in os.listdir(account_dir):
                subdir = os.path.join(account_dir, subd)
                if os.path.isdir(subdir):
                    print(subdir)
                    utils.cut_video_dir(subdir, cut_ratio)


if __name__ == "__main__":
    video_dir = ""
    batch_cut_file(video_dir, 0.3)