import os
import sys
from git import Repo


class BranchReseter:

	def __init__(self, repo_url, local_folder_path, base_branch_name, new_branch_name='forno', branches_to_merge=[]):
		print('Init new BranchReseter instance using the following parameters:')
		print('Repository URL: {}'.format(repo_url))
		print('Local repository folder: {}'.format(local_folder_path))
		print('Base branch ({}) to be used as base to create new branch {}'.format(base_branch_name, new_branch_name))
		print('Branches to merge in {}: {}'.format(new_branch_name, branches_to_merge))
		self.cloned_repo = self.clone_repository(repo_url, local_folder_path)
		self.base_branch_name = base_branch_name
		self.new_branch_name = new_branch_name
		self.branches_to_merge = branches_to_merge

	def clone_repository(self, final_url, destination_folder):
		if not os.path.exists(destination_folder):
			print('Cloning new repository {} to {}'.format(final_url, destination_folder))
			cloned_repo = Repo.clone_from(final_url, destination_folder)
		else:
			print('Repository already exists, using local folder... {}'.format(destination_folder))
			cloned_repo = Repo(destination_folder)
			print('Fetching... {}'.format(destination_folder))
			cloned_repo.remotes.origin.fetch()

		return cloned_repo

	def delete_branch(self, branch_to_delete):
		print('Deleting... {}'.format(branch_to_delete))
		self.cloned_repo.git.branch('-D', branch_to_delete)

	def merge_branch(self, branch_to_merge):
		self.cloned_repo.heads[self.new_branch_name].checkout()
		print('Merging branch {} into {}'.format(branch_to_merge, self.cloned_repo.active_branch))
		base_branch_merge = self.cloned_repo.active_branch
		branch_to_merge_reference = self.cloned_repo.refs['origin/{}'.format(branch_to_merge)]
		base = self.cloned_repo.merge_base(base_branch_merge, branch_to_merge_reference)
		self.cloned_repo.index.merge_tree(branch_to_merge_reference, base=base)

		self.cloned_repo.index.commit('Merge branch {} into {} using BranchReseter by BotEizo'.format(branch_to_merge, self.new_branch_name),
		                              parent_commits = (base_branch_merge.commit, branch_to_merge_reference.commit))

		base_branch_merge.checkout(force=True)

	def init_branch(self):
		self.cloned_repo.heads[self.base_branch_name].checkout()
		print('Current branch {}'.format(self.cloned_repo.active_branch))
		print('All heads {}'.format(self.cloned_repo.heads))

	def merge_branches(self):
		self.init_branch()
		print('Merging branches {} into {}'.format(self.branches_to_merge, self.cloned_repo.active_branch))
		for branch_to_merge in self.branches_to_merge:
			self.merge_branch(branch_to_merge)

	def merge(self):
		self.merge_branches()
		self.push_merge()

	def push_merge(self):
		print('Pushing to remote branch {}'.format(self.cloned_repo.active_branch))
		self.cloned_repo.remotes.origin.push(refspec='{}:{}'.format(self.new_branch_name, self.new_branch_name),
											 force=True)
	def reset_hard(self):

		self.init_branch()

		if self.new_branch_name in self.cloned_repo.heads:
			self.delete_branch(self.new_branch_name)

		print('Creating and checkouting... {}'.format(self.new_branch_name))
		self.cloned_repo.create_head(self.new_branch_name).checkout()
		print('Current branch {}'.format(self.cloned_repo.active_branch))

		self.merge_branches()
		self.push_merge()


GB_FORMAT_FINAL_URL  = 'https://{}:x-oauth-basic@github.com/{}/{}'
GB_PRIVATE_TOKEN = os.environ.get('GB_PRIVATE_TOKEN')
ORGANIZATION = os.environ.get('GB_ORGANIZATION')

repo_name = sys.argv[1]
branch_from = sys.argv[2]
branch_to = sys.argv[3]
branches_to_merge_together = sys.argv[4].split(',') if len(sys.argv) > 4 else []

final_url = GB_FORMAT_FINAL_URL.format(GB_PRIVATE_TOKEN, ORGANIZATION, repo_name)
destination_folder = 'repos/{}'.format(repo_name)

branch_reseter = BranchReseter(repo_url=final_url,
                               local_folder_path=destination_folder,
                               base_branch_name=branch_from,
                               new_branch_name=branch_to,
                               branches_to_merge=branches_to_merge_together)

branch_reseter.reset_hard()
#branch_reseter.merge()

