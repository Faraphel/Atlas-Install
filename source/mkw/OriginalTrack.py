class OriginalTrackNotFound(Exception):
    def __init__(self, track_data: any):
        super().__init__(f'Can\'t find original track "{track_data}"')


class OriginalTrack:
    all_original_tracks: list[dict] = [
        # wii tracks
        {"name": "beginner_course", "slot": "T11", "nickname": "LC"},
        {"name": "farm_course", "slot": "T12", "nickname": "MMM"},
        {"name": "kinoko_course", "slot": "T13", "nickname": "MG"},
        {"name": "factory_course", "slot": "T14", "nickname": "TF"},
    
        {"name": "castle_course", "slot": "T21", "nickname": "MC"},
        {"name": "shopping_course", "slot": "T22", "nickname": "CM"},
        {"name": "boardcross_course", "slot": "T23", "nickname": "DKS"},
        {"name": "truck_course", "slot": "T24", "nickname": "WGM"},

        {"name": "senior_course", "slot": "T31", "nickname": "DC"},
        {"name": "water_course", "slot": "T32", "nickname": "KC"},
        {"name": "treehouse_course", "slot": "T33", "nickname": "MT"},
        {"name": "volcano_course", "slot": "T34", "nickname": "GV"},

        {"name": "desert_course", "slot": "T41", "nickname": "DDR"},
        {"name": "ridgehighway_course", "slot": "T42", "nickname": "MH"},
        {"name": "koopa_course", "slot": "T43", "nickname": "BC"},
        {"name": "rainbow_course", "slot": "T44", "nickname": "RR"},

        # retro tracks
        {"name": "old_peach_gc", "slot": "T51", "nickname": "gPB"},
        {"name": "old_falls_ds", "slot": "T52", "nickname": "dYF"},
        {"name": "old_obake_sfc", "slot": "T53", "nickname": "sGV2"},
        {"name": "old_mario_64", "slot": "T54", "nickname": "nMR"},

        {"name": "old_sherbet_64", "slot": "T61", "nickname": "nSL"},
        {"name": "old_heyho_gba", "slot": "T62", "nickname": "gSGB"},
        {"name": "old_town_ds", "slot": "T63", "nickname": "dDS"},
        {"name": "old_waluigi_gc", "slot": "T64", "nickname": "gWS"},

        {"name": "old_desert_ds", "slot": "T71", "nickname": "dDH"},
        {"name": "old_koopa_gba", "slot": "T72", "nickname": "gBC3"},
        {"name": "old_donkey_64", "slot": "T73", "nickname": "nDKJP"},
        {"name": "old_mario_gc", "slot": "T74", "nickname": "gMC"},

        {"name": "old_mario_sfc", "slot": "T81", "nickname": "sMC3"},
        {"name": "old_garden_ds", "slot": "T82", "nickname": "dPG"},
        {"name": "old_donkey_gc", "slot": "T83", "nickname": "gDKM"},
        {"name": "old_koopa_64", "slot": "T84", "nickname": "nBC"},

        # wii arena
        {"name": "block_battle", "slot": "A11", "nickname": "aBP"},
        {"name": "venice_battle", "slot": "A12", "nickname": "aDP"},
        {"name": "skate_battle", "slot": "A13", "nickname": "aFS"},
        {"name": "casino_battle", "slot": "A14", "nickname": "aCCW"},
        {"name": "sand_battle", "slot": "A15", "nickname": "aTD"},

        # retro arena
        {"name": "old_battle4_sfc", "slot": "A21", "nickname": "asBC4"},
        {"name": "old_battle3_gba", "slot": "A22", "nickname": "agBC3"},
        {"name": "old_matenro_64", "slot": "A23", "nickname": "anSS"},
        {"name": "old_CookieLand_gc", "slot": "A24", "nickname": "agCL"},
        {"name": "old_House_ds", "slot": "A25", "nickname": "adTH"},
    ]
    
    __slots__ = ("name", "slot", "nickname")
    
    def __init__(self, track_data: any, track_key: str = "slot"):
        colors = list(filter(lambda color: color[track_key] == track_data, self.all_original_tracks))
        if len(colors) == 0: raise OriginalTrackNotFound(track_data)

        for key, value in colors[0].items():
            setattr(self, key, value)
