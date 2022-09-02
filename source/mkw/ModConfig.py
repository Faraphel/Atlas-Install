import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Callable, Iterator, TYPE_CHECKING
import json
from PIL import Image

from source.mkw.collection.Region import Region
from source.utils import threaded
from source.mkw import Tag
from source.mkw.ModSettings.ModSettingsGroup import ModSettingsGroup
from source.mkw.Track.Cup import Cup
from source.mkw.collection import MKWColor, Slot
from source.mkw.Track import CustomTrack, DefaultTrack, Arena
from source.progress import Progress
from source.safe_eval.safe_eval import safe_eval
from source.safe_eval.multiple_safe_eval import multiple_safe_eval
from source.wt.szs import SZSPath
from source.translation import translate as _

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval, TemplateSafeEval, Env


CT_ICON_SIZE: int = 128


default_global_settings: dict[str, dict[str, str]] = {
    "replace_random_new": {
        "text": {
            "en": "Replace random new tracks by",
            "fr": "Remplacer les courses aléatoires nouvelle par"
        },
        "description": {
            "en": "The \"Random: New track\" option in the game will select any track respecting this condition.",
            "fr": "L'option \"Aléatoire: Nouvelle course\" dans le jeu va sélectionner n'importe quel course qui "
                  "respecte cette condition."
        },
        "type": "string",
        "preview": "track_selecting"
    },
    "include_track_if": {
        "text": {
            "en": "Include track if",
            "fr": "Inclure la course si"
        },
        "description": {
            "en": "Only the tracks respecting the condition will be in the patched game.",
            "fr": "Seulement les courses respectant la condition seront présente dans le jeu patché."
        },
        "type": "string",
        "preview": "track_selecting"
    },
    "sort_tracks": {
        "text": {
            "en": "Sort tracks by",
            "fr": "Trier les courses par"
        },
        "description": {
            "en": "Define how the tracks should be sorted in the mod.",
            "fr": "Défini comment les courses devrait être trié dans le mod."
        },
        "type": "string",
        "preview": "track_sorting"
    }
}


@dataclass(init=True, slots=True)
class ModConfig:
    """
    Representation of a mod
    """

    path: Path | str
    name: str
    nickname: str = None
    version: str = "v1.0.0"
    gameid_template: "TemplateMultipleSafeEval" = "RMC{{region}}01"

    _tracks: list["Track | TrackGroup | dict"] = field(default_factory=list)
    default_track_attributes: dict[str, any] = field(default_factory=dict)
    _arenas: list["Arena | dict"] = field(default_factory=list)
    track_file_template: "TemplateMultipleSafeEval" = "{{ getattr(track, 'sha1', '_') }}"
    multiplayer_disable_if: "TemplateSafeEval" = "False"

    tags_cups: list[Tag] = field(default_factory=list)
    tags_templates: dict[str, "TemplateMultipleSafeEval"] = field(default_factory=dict)

    original_track_prefix: bool = True
    swap_original_order: bool = True
    keep_original_track: bool = True
    enable_random_cup: bool = True

    macros: dict[str, "TemplateSafeEval"] = field(default_factory=dict)
    messages: dict[str, dict[str, "TemplateMultipleSafeEval"]] = field(default_factory=dict)

    global_settings: ModSettingsGroup = field(default_factory=ModSettingsGroup)
    specific_settings: ModSettingsGroup = field(default_factory=ModSettingsGroup)

    lpar_template: "TemplateMultipleSafeEval" = "normal.lpar"

    def __post_init__(self):
        self.path = Path(self.path)
        if self.nickname is None: self.nickname = self.name

        self._tracks = [CustomTrack.from_dict(self, track) for track in self._tracks if isinstance(track, dict)]
        self._arenas = [Arena.from_dict(self, arena) for arena in self._arenas if isinstance(arena, dict)]

        # Settings
        user_global_settings = self.global_settings
        self.global_settings = ModSettingsGroup(default_global_settings)
        self.global_settings.import_values(user_global_settings)

        self.specific_settings = ModSettingsGroup(self.specific_settings)

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<ModConfig name={self.name} version={self.version}>"

    def __str__(self) -> str:
        return f"{self.name} {self.version}"

    @classmethod
    def from_dict(cls, path: Path | str, config_dict: dict, macros: dict, messages: dict) -> "ModConfig":
        """
        Create a ModConfig from a dict
        :param messages: messages that can be shown to the user at some moment
        :param path: path of the mod_config.json
        :param config_dict: dict containing the configuration
        :param macros: macro that can be used for safe_eval
        :return: ModConfig
        """
        kwargs = config_dict | {
            "path": path,

            "_tracks": config_dict.pop("tracks", []),
            "_arenas": config_dict.pop("arenas", []),

            "macros": macros,
            "messages": messages,
        }

        return cls(**kwargs)

    @classmethod
    def from_file(cls, config_file: str | Path) -> "ModConfig":
        """
        Create a ModConfig from a file
        :param config_file: file containing the configuration
        :return: ModConfig
        """
        config_file = Path(config_file)
        macros_file = config_file.parent / "macros.json"
        messages_file = config_file.parent / "messages.json"

        return cls.from_dict(
            path=config_file,
            config_dict=json.loads(config_file.read_text(encoding="utf8")),
            macros=json.loads(macros_file.read_text(encoding="utf8")) if macros_file.exists() else None,
            messages=json.loads(messages_file.read_text(encoding="utf8")) if messages_file.exists() else None,
        )

    def get_safe_eval_env(self, base_env: "Env" = None) -> dict[str, any]:
        """
        Return the env for the modconfig safe_eval function
        :param base_env: additional environment
        :return: the modconfig environment
        """
        return {
            "mod_config": self,
            "get_color": MKWColor.get
        } | (
            base_env if base_env is not None else {}
        )

    def safe_eval(self, *args, env: "Env" = None, **kwargs) -> Callable:
        """
        Safe eval with useful modconfig environment
        :return: the result of the evaluation
        """
        return safe_eval(*args, env=self.get_safe_eval_env(base_env=env), macros=self.macros, **kwargs)

    def multiple_safe_eval(self, *args, env: "Env" = None, **kwargs) -> Callable:
        """
        Multiple safe eval with useful modconfig environment
        :return: the str result of the evaluation
        """
        return multiple_safe_eval(*args, env=self.get_safe_eval_env(base_env=env), macros=self.macros, **kwargs)

    def get_mod_directory(self) -> Path:
        """
        Get the directory of the mod
        :return: directory of the mod
        """
        return self.path.parent

    def get_all_arenas_tracks(self, *args, **kwargs) -> Generator["CustomTrack", None, None]:
        """
        Same as get_all_tracks, but arenas are included
        """
        yield from self.get_all_tracks(*args, **kwargs)
        yield from self.get_arenas()

    def get_arenas(self) -> Generator["Arena", None, None]:
        """
        Yield all arenas of the mod
        """
        yield from self._arenas

    def get_all_tracks(self, *args, **kwargs) -> Generator["CustomTrack", None, None]:
        """
        Same as get_tracks, but track group are divided into subtracks
        """

        for track in self.get_tracks(*args, **kwargs):
            yield from track.get_tracks()

    def get_tracks(self, ignore_filter: bool = False,
                   sorting_template: str = None,
                   ignore_sorting: bool = False) -> Generator["Track | TrackGroup", None, None]:
        """
        Get all the tracks or tracks groups elements
        :ignore_filter: should the tracks filter be ignored
        :return: track or tracks groups elements
        """

        filter_template: "TemplateSafeEval | None" = self.global_settings["include_track_if"].value \
            if not ignore_filter else None
        settings_sort: "TemplateSafeEval | None" = self.global_settings["sort_tracks"].value

        # filter_template_func is the function checking if the track should be included. If no parameter is set,
        # then always return True
        filter_template_func: Callable = self.safe_eval(
            template=filter_template if filter_template is not None else "True", args=["track"]
        )

        # if a sorting function is set, use it. If no function is set, but sorting is not disabled, use settings.
        iterator: Iterator = filter(lambda track: filter_template_func(track=track) is True, self._tracks)
        if not ignore_sorting and (sorting_template is not None or settings_sort is not None):
            # get the sorting_template_func. If not defined, use the settings one.
            sorting_template_func: Callable = self.safe_eval(
                template=sorting_template if sorting_template is not None else settings_sort, args=["track"]
            )

            # wrap the iterator inside a sort function
            iterator = sorted(iterator, key=sorting_template_func)

        # Go through all the tracks and filter them if enabled
        for track in iterator:
            yield track

    def get_ordered_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups with cup tags
        :return: cups with cup tags
        """
        # for track that have a tag in self.tags_cups
        for tag_cup in self.tags_cups:
            track_buffer: "Track | TrackGroup" = []
            current_tag_name, current_tag_count = tag_cup, 0

            # every four 4 tracks, create a cup
            for track in filter(lambda track: tag_cup in getattr(track, "tags", []), self.get_tracks()):
                track_buffer.append(track)

                if len(track_buffer) > 4:
                    current_tag_count += 1
                    yield Cup(mod_config=self, tracks=track_buffer, cup_name=f"{current_tag_name}/{current_tag_count}")
                    track_buffer = []

            # if there is still tracks in the buffer, create a cup with them and fill with default>
            if len(track_buffer) > 0:
                track_buffer.extend([DefaultTrack(mod_config=self)] * (4 - len(track_buffer)))
                yield Cup(mod_config=self, tracks=track_buffer, cup_name=f"{current_tag_name}/{current_tag_count + 1}")

    def get_unordered_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups with no cup tags
        :return: cups with no cup tags
        """
        # for track that have don't have a tag in self.tags_cups
        track_buffer: "Track | TrackGroup" = []
        for track in filter(
                lambda track: not any(item in getattr(track, "tags", []) for item in self.tags_cups),
                self.get_tracks()
        ):
            track_buffer.append(track)

            if len(track_buffer) > 4:
                yield Cup(mod_config=self, tracks=track_buffer)
                track_buffer = []

        # if there is still tracks in the buffer, create a cup with them and fill with default
        if len(track_buffer) > 0:
            track_buffer.extend([DefaultTrack(mod_config=self)] * (4 - len(track_buffer)))
            yield Cup(mod_config=self, tracks=track_buffer)

    def get_cups(self) -> Generator["Cup", None, None]:
        """
        Get all the cups
        :return: cups
        """
        yield from self.get_ordered_cups()
        yield from self.get_unordered_cups()

    def get_ctfile(self, template: "TemplateMultipleSafeEval") -> str:
        """
        Return the ct_file generated from the ModConfig
        :template: template for the track name
        :return: ctfile content
        """
        lecode_flags = filter(lambda v: v is not None, [
            "N$SHOW" if self.keep_original_track else "N$NONE",
            "N$F_WII" if self.original_track_prefix else None,
            "N$SWAP" if self.swap_original_order else None
        ])

        ctfile = (
            f"#CT-CODE\n"  # magic number
            f"[RACING-TRACK-LIST]\n"  # start of the track section
            f"%LE-FLAGS=1\n"  # enable lecode mode
            f"%WIIMM-CUP={int(self.enable_random_cup)}\n"  # enable random cup
            f"N {' | '.join(lecode_flags)}\n"  # other flags to disable default tracks, ...
            f"\n"
        )

        for cup in self.get_cups():
            # get all the cup ctfile, use "-" for the template since the track's name are not used here
            ctfile += cup.get_ctfile(template=template)

        ctfile_override_property = "[SETUP-ARENA]\n"
        for arena in self.get_arenas():
            arena_definition, arena_override_property = arena.get_ctfile(template=template)
            ctfile += arena_definition
            ctfile_override_property += arena_override_property

        ctfile += ctfile_override_property

        return ctfile

    def get_base_cticons(self) -> Generator[Image.Image, None, None]:
        """
        Return the base cticon
        :return:
        """
        icon_names = ["left", "right"]

        if self.keep_original_track:
            icon_names += [
                f"_DEFAULT/{name}"
                for name in (
                    ["mushroom", "shell", "flower", "banana", "star", "leaf", "special", "lightning"]
                    if self.swap_original_order else
                    ["mushroom", "flower", "star", "special", "shell", "banana", "leaf", "lightning"]
                )
            ]
        if self.enable_random_cup: icon_names.append("random")

        for icon_name in icon_names:
            yield Image.open(self.get_mod_directory() / f"_CUPS/{icon_name}.png").resize((CT_ICON_SIZE, CT_ICON_SIZE))

    def get_custom_cticons(self) -> Generator[Image.Image, None, None]:
        """
        Return the custom ct_icon generated from the ModConfig
        :return:
        """
        for cup in self.get_cups():
            yield cup.get_cticon(mod_config=self).resize((CT_ICON_SIZE, CT_ICON_SIZE))

    def get_cticons(self) -> Generator[Image.Image, None, None]:
        """
        Return all the ct_icon generated from the ModConfig
        :return:
        """
        yield from self.get_base_cticons()
        yield from self.get_custom_cticons()

    @staticmethod
    def get_default_font() -> Path:
        """
        Return the default font for creating ct_icons
        :return: the path to the default font file
        """
        return Path("./assets/SuperMario256.ttf")

    def get_full_cticon(self) -> Image.Image:
        """
        Return the full ct_icon generated from the ModConfig
        :return:
        """
        cticons = list(self.get_cticons())

        full_cticon = Image.new("RGBA", (CT_ICON_SIZE, CT_ICON_SIZE * len(cticons)))
        for i, cticon in enumerate(cticons): full_cticon.paste(cticon, (0, i * CT_ICON_SIZE))

        return full_cticon

    def normalize_all_tracks(self, autoadd_path: "Path | str", destination_path: "Path | str",
                             original_tracks_path: "Path | str",
                             thread_amount: int = 8) -> Generator[Progress, None, None]:
        """
        Convert all tracks of the mod to szs into the destination_path
        :param original_tracks_path: path to the originals tracks (if a track is disabled for multiplayer)
        :param thread_amount: number of thread to use
        :param autoadd_path: autoadd directory
        :param destination_path: destination where the files are converted
        """
        destination_path = Path(destination_path)
        original_tracks_path = Path(original_tracks_path)
        destination_path.mkdir(parents=True, exist_ok=True)

        normalize_threads: list[dict] = []
        all_arenas_tracks = list(self.get_all_arenas_tracks())

        def remove_finished_threads() -> Generator[Progress, None, None]:
            """
            Remove all the thread that stopped in a thread list
            :return: the list without the stopped thread
            """
            nonlocal normalize_threads

            yield Progress(
                description=_("TEXT_NORMALIZING_TRACKS") % "\n".join(thread['name'] for thread in normalize_threads)
            )

            normalize_threads = list(filter(lambda thread: thread["thread"].is_alive(), normalize_threads))

        track_directory = self.path.parent / "_TRACKS"
        multiplayer_disable_if_func: Callable = self.safe_eval(
            self.multiplayer_disable_if, args=["track"]
        )

        yield Progress(
            determinate=True,
            max_step=len(all_arenas_tracks)+1,
            set_step=0,
        )

        for track in all_arenas_tracks:
            yield Progress(step=1)

            track_file: Path = next(
                track_directory.rglob(f"{track.repr_format(template=self.track_file_template)}.*")
            )

            @threaded
            def normalize_track(track: CustomTrack, track_file: Path):
                SZSPath(track_file).normalize(
                    autoadd_path,
                    destination_path / f"{track_file.stem}.szs",
                    format="szs"
                )

                if multiplayer_disable_if_func(track=track) is True:
                    # if the track should use the default track instead in multiplayer,
                    # copy the default track to the same file but with a _d at the end
                    shutil.copy(
                        original_tracks_path / f"{Slot.get(normal=track.special).track_name}_d.szs",
                        destination_path / f"{track_file.stem}_d.szs"
                    )

                else:
                    # delete the _d file if it exists
                    (destination_path / f"{track_file.stem}_d.szs").unlink(missing_ok=True)

            normalize_threads.append({"name": track_file.name, "thread": normalize_track(track, track_file)})
            while len(normalize_threads) > thread_amount: yield from remove_finished_threads()
            # if there is more than the max amount of thread running, wait for one to finish
        while len(normalize_threads) > 0: yield from remove_finished_threads()
        # if there is no longer any track to add, wait for all process to finish

    def get_gameid(self, region: Region):
        pass
