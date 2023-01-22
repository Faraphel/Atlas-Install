import os

# metadata
__version__ = (0, 12, 0)
__author__ = 'Faraphel'


# external links
discord_url = "https://discord.gg/HEYW5v8ZCd"
github_wiki_url = "https://github.com/Faraphel/MKWF-Install/wiki/help"
readthedocs_url = "https://mkwf-install.readthedocs.io/"


# constant declaration
Ko: int = 1_000
Mo: int = 1_000 * Ko
Go: int = 1_000 * Mo

minimum_space_available: int = 15*Go
file_block_size: int = 128*Ko

system = "win64" if os.name == "nt" else "lin64"

# global type hint
TemplateSafeEval: str
TemplateMultipleSafeEval: str
Env: dict[str, any]
