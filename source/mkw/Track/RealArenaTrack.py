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

    tags: list["Tag"]

    def get_tag_template(self, mod_config: "ModConfig", template_name: str, default: any = None) -> any:
        """
        Return the tag template found in templates. If not found, return default
        :param mod_config: mod configuration
        :param template_name: name of the template of the tags
        :param default: default value if no tag template is found
        :return: formatted representation of the tag
        """
        for tag in filter(lambda tag: tag in mod_config.tags_templates[template_name], self.tags):
            return mod_config.multiple_safe_eval(
                mod_config.tags_templates[template_name][tag],
                args=["tag"],
            )(tag=tag)
        return default

    def repr_format(self, mod_config: "ModConfig", template: "TemplateMultipleSafeEval") -> str:
        return mod_config.multiple_safe_eval(
            template,
            args=["track", "get_tag_template"]
        )(
            track=self,
            get_tag_template=lambda *args, **kwargs: self.get_tag_template(mod_config, *args, **kwargs)
            # get_tag_template can't be in env because it is dependent of the track self
        )

    def get_filename(self, mod_config: "ModConfig") -> str:
        return self.repr_format(mod_config=mod_config, template=mod_config.track_file_template)
