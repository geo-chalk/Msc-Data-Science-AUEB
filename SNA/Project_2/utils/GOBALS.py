BASIC_COLS: list = ["Nodes", "NodeOutDeg", "RewireProb"]
DEGREE_COLS: list = ["highest_deg_ID", "highest_deg_degree"]
HUB_COLS: list = ["highest_hubscore_ID", "highest_hubscore_degree"]
AUTH_COLS: list = ["highest_authscore_ID", "highest_authscore_degree"]
COMMUNITLY_COLS: dict = {"CommunityCNM": ["CommunityCNM_time_s", "CommunityCNM_modularity"],
                         "CommunityGirvanNewman": ["CommunityGirvanNewman_time_s", "CommunityGirvanNewman_modularity"]
                         }
