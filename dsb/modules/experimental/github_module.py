""" Github module for DSB. """

import asyncio
from github import Github, Commit
from dsb.types.module import BaseModule

class GithubModule(BaseModule):
    """ Github module for DSB. """
    def __init__(self, bot, dsb):
        super().__init__(bot, dsb)
        try:
            self._github = Github()
        except Exception as e: # pylint: disable=broad-except
            self._github = None
            self._dsb.error(f"Failed to connect to Github: {e}")
            return
        self._repo_name = dsb.config["repo_name"]
        self._repo = None

    async def _get_last_commit(self, chat_id: int):
        """ Get the last commit """
        if not self._github:
            return
        commit: Commit.Commit = self._repo.get_commits()[0]
        commits = self._dsb.database.get_table("last_commits")
        last_commits = commits.get_rows()
        if last_commits:
            last_commit = last_commits[-1][1]
            if last_commit == commit.sha:
                return
        commits.remove_rows(lambda x: True)
        commits.add_row([commit.sha])
        commits.save()
        commit_info = f"Author: {commit.author.name}" + \
            f"\nTitle: {commit.commit.message.split("\n")[0]}" + \
            f"\nPosted at: {commit.commit.author.date}" + \
            f"\nURL: {commit.html_url}"
        await self._bot.bot.send_message(chat_id, "Last commit:\n" + commit_info)

    def prepare(self):
        self._github.get_repo(self._repo_name)
        self._dsb.database.add_table("last_commits", [("commits", str, False)], True)
        loop = asyncio.get_event_loop()
        loop.create_task(self._get_last_commit(self._dsb.config["update_channel_id"]))
        return super().prepare()
