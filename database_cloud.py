import yadisk
import os


class DatabaseCloud:

    def __init__(self, token):
        self.disk = yadisk.YaDisk(token=token)

    def upload(self, user_file, disk_file, remove=True):
        if disk_file in self.listdir() and remove:
            self.remove(disk_file)
        self.disk.upload(user_file, f'database/{disk_file}')

    def download(self, user_file, disk_file):
        os.remove(user_file)
        self.disk.download(f'database/{disk_file}', user_file)

    def listdir(self):
        return [i.name for i in list(self.disk.listdir("/database"))]

    def remove(self, disk_file):
        self.disk.remove(f'database/{disk_file}')