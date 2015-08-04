#!/usr/bin/python

__author__ = 'urfrendlipiro'

print("hello from injury_risk_robot")

def set_info(player_history_init, year):
    global player_history
    global current_year
    player_history = player_history_init
    current_year = year

    # ##   To help visualize the data given on player history uncomment this block to see it printed out
    # ##   once for each position.
    #
    #first_pos = {"QB": True, "RB": True, "WR": True, "TE": True, "K": True, "DEF": True}
    #for player in player_history:
    #    if first_pos[player.position]:
    #        print(str(player))
    #        first_pos[player.position] = False

def get_missed_game_score(available_players, team):
    global current_year
    # we don't want to accidentally return a player for a filled position, so get a list of open slots
    open_positions = []
    for i in ["QB","RB","WR","TE","FLEX","K","DEF"]:
        if team.is_position_open(i):
            open_positions.append(i)

    # run through the list of available players and find their injury risk
    all_available_missed_games_scores = {}
    for i in range(0, len(available_players)):
        # Access the players projections as well as past yearly and weekly stats to make your decision
        player = player_history[available_players[i]]
        projection = player.yearly_data["Projected"].season_totals
        """
        our score calculates the percentage of games played each year and then weights the most recent
        years more heavily.
        example: if player played 3 years, last year is worth 3, year before 2, and his rookie year is 1
        """

        # skip players at a position that's already filled
        if player.position in open_positions:
            # get the year and how many games played that year. add to a dict
            years_dict = {}
            for y in player.yearly_data:
                if player.yearly_data[y].season_totals != None and y != "Projected":
                    yearly_gp = player.yearly_data[y].season_totals.games_played
                    """
                    there is a bug with the games_played api
                    some players played for multiple teams in one year
                    the csv file lists that as BUF | SEA, which screws up the api
                    for simplicity sakes, just set the yearly_gp to 16
                    """
                    if yearly_gp == "|":
                        yearly_gp = 16
                    years_dict[y] = yearly_gp

            # get the total number of years played
            years_played = len(years_dict)
            # set up another var that we can decrement
            years_played_var = years_played

            # all of our picks have to be safe. without gp info on rookies, they can't be trusted.
            if years_played != 0:
                # for each year, calculate percentage of games played and weight it
                year_scores = []
                for y in sorted(years_dict, reverse=True):
                    games_played = float(years_dict[y])
                    percentage_games_played = games_played/16
                    weighted_percentage_games_played = percentage_games_played*years_played_var
                    # add it to the list and decrement years_played_var so the weight for the previous
                    # year is correct
                    year_scores.append((weighted_percentage_games_played))
                    years_played_var -= 1

                # get weighted total years possible
                total_years_possible = (((years_played)*(years_played+1))/2)
                # get weighted total years
                total_years = sum(year_scores)
                # calculate score, rounded to 3 decimal points
                missed_game_score = round((total_years/total_years_possible),3)

                # create a dict with available players and their missed game scores
                all_available_missed_games_scores[available_players[i]] = missed_game_score

    return all_available_missed_games_scores



"""
    get a missed game score for all players and then remove players don't meet your risk
    threshold. select the player with the highest ADP that meets your risk threshold

"""

def get_top_player(available_players, team):
    all_scores = get_missed_game_score(available_players, team)

    # now that we have our data, we'll remove all the players that have a score less than x%
    risk_aversion = .85  #change this based on how risk averse you are. higher = more risk averse
    acceptable_players = {k: v for k, v in all_scores.items() if k > risk_aversion}
    top_player_id = min(acceptable_players)

    # return the id/adp for the top player. This is who we'll draft
    return top_player_id

def draft_player(available_players, team):
    top_player_id = get_top_player(available_players, team)
    return top_player_id