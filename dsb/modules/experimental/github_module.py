""" Github module for DSB. """

import asyncio
from github import Github, Commit
from dsb.types.module import BaseModule

class GithubModule(BaseModule):
    """ Github module for DSB. """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
        self._github = Github()
        repo_name = dsb.config["repo_name"]
        self._repo = self._github.get_repo(repo_name)

    async def _get_last_commit(self, chat_id: int):
        """ Get the last commit """
        commit: Commit.Commit = self._repo.get_commits()[0]
        if self._dsb.database.load('github', 'last_commit') == commit.sha:
            return
        self._dsb.database.save(commit.sha, 'github', 'last_commit', True)
        commit_info = f"Author: {commit.author.name}" + \
            f"\nTitle: {commit.commit.message.split("\n")[0]}" + \
            f"\nPosted at: {commit.commit.author.date}" + \
            f"\nURL: {commit.html_url}"
        await self._bot.bot.send_message(chat_id, "Last commit:\n" + commit_info)

    def prepare(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._get_last_commit(self._dsb.config["update_channel_id"]))
        return super().prepare()
