# This file is part of OpenHatch.
# Copyright (C) 2010 Jack Grigg
# Copyright (C) 2010 John Stumpo
# Copyright (C) 2010, 2011 OpenHatch, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mysite.missions.base.controllers import *

class GitRepository(object):
    
    def __init__(self, username):
        self.username = username
        self.repo_path = os.path.join(settings.GIT_REPO_PATH, username)
        self.file_url = 'file://' + self.repo_path
        self.public_url = settings.GIT_REPO_URL_PREFIX + username
        
    def reset(self):
        if os.path.isdir(self.repo_path):
            shutil.rmtree(self.repo_path)
        subprocess.check_call(['git', 'init', self.repo_path])
        subprocess.Popen(['git', 'config', 'user.name', '"The Brain"'], cwd=self.repo_path)
        subprocess.Popen(['cp', '../../../missions/git/data/hello.py', '.'], cwd=self.repo_path)
        subprocess.Popen(['git', 'add', '.'], cwd=self.repo_path)
        subprocess.Popen(['git', 'commit', '-m', '"Initial commit"'], cwd=self.repo_path)

        # Touch the git-daemon-export-ok file
        file_obj = file(os.path.join(self.repo_path, '.git', 'git-daemon-export-ok'), 'w')
        file_obj.close()

        person = Person.objects.get(user__username=self.username)
        
    def exists(self):
        return os.path.isdir(self.repo_path)

class GitDiffMission(object):

    @classmethod
    def validate_diff_and_commit_if_ok(cls, username, diff):
        EXPECTED_DIFF_LINE = '+print "Hello world!"'
        success_count = diff.find(EXPECTED_DIFF_LINE)
        repo = GitRepository(username)
        if success_count != -1:
            subprocess.Popen(['git', 'apply', '../../../missions/git/data/hello.patch'], cwd=repo.repo_path)
            commit_msg = """Fixed a terrible mistake. Thanks for reporting this %s. 
                Come to my house for a dinner party.  
                Knock 3 times and give the secret password: Pinky.""" % username
            subprocess.Popen(['git', 'commit', '-a', '-m', '"' + commit_msg + '"'], cwd=repo.repo_path)
            return True
        else:
            return False