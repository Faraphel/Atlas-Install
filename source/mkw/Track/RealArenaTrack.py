from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source import TemplateMultipleSafeEval
    from source.mkw import Tag
    from source.mkw.ModConfig import ModConfig


class RealArenaTrack:
    """
    class shared between all arena and track class that represent a "real" track or arena
    (For example, DefaultTrack is not considered a real track class)
    """

    mod_config: "ModConfig"
    tags: list["Tag"]

    def get_tag_template(self, template_name: str, default: any = None) -> any:
        """
        Return the tag template found in templates. If not found, return default
        :param template_name: name of the template of the tags
        :param default: default value if no tag template is found
        :return: formatted representation of the tag
        """
        for tag in self.tags:
            # if the tag start with an underscore (for example _3DS), it will be found in a get_tag_template,
            # but ignored in the tags_cups list
            tag = tag.removeprefix("_")
            if tag not in self.mod_config.tags_templates[template_name]: continue

            return self.mod_config.multiple_safe_eval(
                template=self.mod_config.tags_templates[template_name][tag],
                args=["tag"],
            )(tag=tag)
        return default

    def repr_format(self, template: "TemplateMultipleSafeEval") -> str:
        return self.mod_config.multiple_safe_eval(
            template=template,
            env={
                "get_tag_template": lambda track, *args, **kwargs: track.get_tag_template(*args, **kwargs),
            },
            args=["track"],
        )(track=self)

    @property
    def filename(self) -> str:
        return self.repr_format(template=self.mod_config.track_file_template)

    def __getattr__(self, item):
        return self.mod_config.default_track_attributes.get(item, None)
