

def get_finished_installation_message(mod_config: "ModConfig") -> str:
    message: str = translate_external(
        mod_config, mod_config.messages.get("installation_completed", {}).get("text", {})
    )

    return f"{_('TEXT_INSTALLATION_FINISHED_SUCCESSFULLY')}" + (
        f"\n{_('TEXT_MESSAGE_FROM_AUTHOR')} :\n\n{message}" if message != "" else ""
    )