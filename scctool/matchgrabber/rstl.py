"""Provide match grabber for AlphaTL."""

import logging
import os
import scctool.settings

from urllib.request import urlretrieve
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

# create logger
module_logger = logging.getLogger('scctool.matchgrabber.rstl')


class MatchGrabber(MatchGrabberParent):
    """Grabs match data from Russian StarCraft 2 Teamleague."""

    def __init__(self, *args):
        """Init match grabber."""
        super(MatchGrabber, self).__init__(*args)
        self._provider = "RSTL"
        self._urlprefix = \
            "http://hdgame.net/en/tournaments/list/tournament"\
            + "/rstl-13/tmenu/tmatches/?match="
        self._apiprefix = \
            "http://hdgame.net/index.php?ajax=1&do=tournament&act=api"\
            + "&data_type=json&lang=en&service=match&match_id="

    def grabData(self):
        """Grab match data."""
        data = self._getJson()
        if(data['code'] != "200"):
            msg = 'API-Error: ' + data['code']
            raise ValueError(msg)

        data = data['data']
        self._rawData = data

        if(data['game_format'] == "3"):
            self._matchData.setNoSets(7, 6, resetPlayers=True)
            self._matchData.setMinSets(4)
            self._matchData.resetLabels()
            self._matchData.setSolo(False)
            self._matchData.setLeague(data['tournament']['name'])

            for set_idx in range(7):
                self._matchData.setMap(
                    set_idx, data['start_maps'][str(set_idx)]['name'])

            for team_idx in range(2):
                for set_idx in range(4):
                    try:
                        lu = 'lu' + str(team_idx + 1)
                        self._matchData.setPlayer(
                            team_idx, set_idx,
                            data[lu][str(set_idx)]['member_name'],
                            data[lu][str(set_idx)]['r_name'])
                    except Exception:
                        pass

                for set_idx in range(4, 7):
                    try:
                        player = data['result']['8']['member_name' +
                                                    str(team_idx + 1)]
                        race = data['result']['8']['r_name' + str(team_idx + 1)]
                    except Exception:
                        pass

                    try:
                        idx = str(4 + set_idx)

                        try:
                            idx = str(5 + set_idx)
                            temp_race = data['result'][idx]['r_name' +
                                                            str(team_idx + 1)]
                            if temp_race is not None:
                                race = temp_race
                        finally:
                            if race is None:
                                race = "Random"
                        try:
                            temp_player = data['result'][str(
                                5 + set_idx)]['member_name' + str(team_idx + 1)]
                            if temp_player is not None:
                                player = temp_player
                        finally:
                            if temp_player is None:
                                player = "TBD"

                        self._matchData.setPlayer(team_idx, set_idx,
                                                  player, race)
                    except Exception:
                        pass

                team = data['member' + str(team_idx + 1)]
                self._matchData.setTeam(team_idx, team['name'], team['tag'])

            self._matchData.setLabel(4, "Ace Map 1")
            self._matchData.setLabel(5, "Ace Map 2")
            self._matchData.setLabel(6, "Ace Map 3")

            for set_idx in range(4):
                try:
                    score1 = int(
                        data['result'][str(set_idx * 2)]['score1'])
                    score2 = int(
                        data['result'][str(set_idx * 2)]['score2'])
                except Exception:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0

                self._matchData.setMapScore(set_idx, score)

            for set_idx in range(4, 7):
                try:
                    score1 = int(
                        data['result'][str(5 + set_idx)]['score1'])
                    score2 = int(
                        data['result'][str(5 + set_idx)]['score2'])
                except Exception:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0
                self._matchData.setMapScore(set_idx, score)

            self._matchData.setAllKill(False)

        elif(data['game_format'] == "2"):  # All-Kill BoX

            self._matchData.resetData()
            bo = int(data['game_format_bo'])
            self._matchData.setNoSets(bo, bo, resetPlayers=True)
            self._matchData.setMinSets(0)
            self._matchData.setSolo(False)
            self._matchData.setLeague(data['tournament']['name'])

            for set_idx in range(1):
                self._matchData.setMap(
                    set_idx, data['start_maps'][str(set_idx)]['name'])

            for team_idx in range(2):
                for set_idx in range(1):
                    try:
                        lu = 'lu' + str(team_idx + 1)
                        self._matchData.setPlayer(
                            team_idx, set_idx,
                            data[lu][str(set_idx)]['member_name'],
                            data[lu][str(set_idx)]['r_name'])
                    except Exception:
                        pass

                for set_idx in range(1, bo):
                    try:
                        idx = str(set_idx * 2)
                        if(not data['result'][idx]['r_name' +
                                                   str(team_idx + 1)]):
                            try:
                                idx = str(set_idx * 2 + 1)
                                race = data['result'][idx]['r_name'
                                                           + str(team_idx + 1)]
                            except Exception:
                                race = "Random"
                        else:
                            race = data['result'][str(
                                set_idx * 2)]['r_name' + str(team_idx + 1)]
                        player = data['result'][str(
                            set_idx * 2)]['member_name' + str(team_idx + 1)]
                        self._matchData.setPlayer(team_idx, set_idx,
                                                  player, race)
                    except Exception:
                        pass

                team = data['member' + str(team_idx + 1)]
                self._matchData.setTeam(team_idx, team['name'], team['tag'])

            for set_idx in range(bo):
                try:
                    score1 = int(
                        data['result'][str(set_idx * 2)]['score1'])
                    score2 = int(
                        data['result'][str(set_idx * 2)]['score2'])
                except Exception:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0

                self._matchData.setMapScore(set_idx, score)
                self._matchData.resetLabels()

            self._matchData.setAllKill(True)
        else:
            module_logger.info("RSTL Format Unknown")

    def downloadLogos(self, logoManager):
        """Download team logos."""
        dir = scctool.settings.OBSdataDir

        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")
                
        for idx in range(1,3):
            try:
                logo = logoManager.newLogo()
                logo.fromURL("http://hdgame.net" + self._rawData['member' + str(idx)]['img_m'])
                getattr(logoManager, 'setTeam{}Logo'.format(idx))(logo)

                # self._controller.ftpUploader.cwd(dir)
                # self._controller.ftpUploader.upload(
                #     fname,
                #     "logo" + str(idx + 1) + ext)
                # self._controller.ftpUploader.cwd("..")
            except Exception as e:
                module_logger.exception("message")
