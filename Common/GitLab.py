#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.


# Project ID, HwICX: 31, Moc25: 12, Byo: 34

import requests
import zipfile
import json
import os

class Gitlab():
    def __init__(self, projectid, access_token):
        self.projectid = projectid
        self.access_token = access_token
        self.base_url = 'http://221.228.236.229:28090/api/v4/projects/'
        self.header = {'PRIVATE-TOKEN': self.access_token}
        self.jobs_url = ''
 

    def get_latest_job_master(self):
        self.jobs_url = self.base_url + str(self.projectid) + '/jobs'
        res = requests.get(self.jobs_url, headers=self.header)
        job_list = json.loads(res.content)
        if not job_list:
            print("Job list is empty")
            return
        latest_job = []
        for i in range(len(job_list)):
            if job_list[i]['ref'] == 'master' and job_list[i]['status'] == 'success':
                latest_job = job_list[i]
                break
        return latest_job

    @staticmethod
    def print_msg(job):
        print("JobID:{0}".format(job['id']))
        print("JobName:{0}".format(job['name']))
        print("Branch:{0}".format(job['ref']))
        print("Author:{0}".format(job['commit']['author_name']))
        print("Commit: {0}".format(job['commit']['short_id']))
        print("BuildFinishedTime:{0}".format(job['finished_at']))


    def download_image(self, job, dir):
        img_zip = os.path.join(dir, "artifacts.zip")
        if os.path.exists(img_zip):
            os.remove(img_zip)
        if not job:
            return

        self.print_msg(job)

        artifact_url = self.jobs_url + '/' + str(job['id']) + '/artifacts'
        cmd = "curl --output {0} --header \"PRIVATE-TOKEN: {1}\" {2}".format(img_zip, self.access_token, artifact_url)      
        if os.system(cmd) == 0:
            print("Download image successfully")
            image_path = self.unzip(img_zip, dir)
            os.remove(img_zip)
            return image_path
        else:
            print("Download image fail")
      
    
    def download_latest_image_master(self, dir):
        latest_job = self.get_latest_job_master()
        return self.download_image(latest_job, dir)

    @staticmethod        
    def unzip(file, dst):
        uz = zipfile.ZipFile(file, 'r')
        for file in uz.namelist():
            if '.bin' in file:
                file_path =  os.path.join(dst, file.replace("/", "\\"))
                if os.path.exists(file_path):
                    print("Delete old file")
                    os.remove(file_path)
                uz.extract(file, dst)
                return os.path.join(dst, file_path)



if __name__ == '__main__':
    dir = "c:\\daily"
    gitlab_icx = Gitlab(12, 'PbLqm_njsnGxCQBtHoMG')
    print(gitlab_icx.download_latest_image_master(dir))