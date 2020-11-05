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


    def download_image(self, job):
        if not job:
            return
        print("JobID:{0}".format(job['id']))
        print("JobName:{0}".format(job['name']))
        print("Branch:{0}".format(job['ref']))
        print("Author:{0}".format(job['commit']['author_name']))
        print("Commit: {0}".format(job['commit']['short_id']))
        print("BuildFinishedTime:{0}".format(job['finished_at']))
        artifact_url = self.jobs_url + '/' + str(job['id']) + '/artifacts'
        cmd = "curl --output ..\\artifacts.zip --header \"PRIVATE-TOKEN: {0}\" {1}".format(self.access_token, artifact_url)      
        if os.system(cmd) == 0:
            print("Download image successfully")
            return True
        else:
            print("Download image fail")
      
    
    def download_latest_image_master(self):
        latest_job = self.get_latest_job_master()
        if self.download_image(latest_job):
            return True
            
        

    def fetch_latest_image():
        pass




if __name__ == '__main__':
    gitlab_icx = Gitlab(12, 'PbLqm_njsnGxCQBtHoMG')
    print(gitlab_icx.download_latest_image_master())