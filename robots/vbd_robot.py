#!/usr/bin/python

__author__ = 'urfrendlipiro'

print("hello from vbd_robot")

def set_info(player_history_init, year):
    global player_history
    global current_year
    player_history = player_history_init
    current_year = year

    # ##   To help visualize the data given on player history uncomment this block to see it printed out
    # ##   once for each position.
    #
    # first_pos = {"QB": True, "RB": True, "WR": True, "TE": True, "K": True, "DEF": True}
    # for player in player_history:
    #     if first_pos[player.position]:
    #         print(str(player))
    #         first_pos[player.position] = False

"""
    the purpose of this function is to calculate the baselines for VBD (value based drafting scores).
    we only care about the scores for the number of starters in the league.
    for example, a 1 QB, 12 team league would have 12 starters
    a 2 RB, 14 team league would have 28 starters
    for the flex, typically we divide the teams in the league by the eligible position, (12/3 in this case)
    but we're going to weight RB and WR more than TE because a bad WR/RB typically produces
    more than an average TE. we'll use a 40/40/20 split. so if it's a 12 team league with 1 QB, 2 RB, 3 WR, 1 TE. 1 WR/RB/TE
    we'll say the starters are 12 QB, 29 RB (12*2+(12*.4)), 41 WR (12*3+(12*.4)), and 14 TE (12*1+(12*.2))
"""
def calculate_vbd_baselines(pos,starters):
    all_scores = []
    for i in player_history:
         if i.position == pos:
            # get all the score for the position and append to the all_scores list
            all_scores.append(i.yearly_data["Projected"].season_totals.points)
    # get the list in highest to lowest order
    all_scores.sort(reverse=True)
    # get the scores for the number of starters only
    top_scores = all_scores[:starters]
    # get the average of the top scores
    average_starter = sum(top_scores)/float(len(top_scores))
    # get the lowest score of a starter
    worst_starter = top_scores[-1]
    return average_starter, worst_starter
"""
    of the available players, figures out which has the highest VBD score
"""
def get_top_player(available_players, team):
    global current_year
    qb_avg, qb_worst = calculate_vbd_baselines("QB",12)
    rb_avg, rb_worst = calculate_vbd_baselines("RB",29)
    wr_avg, wr_worst = calculate_vbd_baselines("WR",29)
    te_avg, te_worst = calculate_vbd_baselines("TE",14)
    k_avg, k_worst = calculate_vbd_baselines("K",12)
    def_avg, def_worst = calculate_vbd_baselines("DEF",12)

    """ printing the VBD baselines. Just informational
    print("The VBD baselines are as follows:")
    print("QB Average: %s. QB Worst: %s" %(qb_avg,qb_worst))
    print("RB Average: %s. RB Worst: %s" %(rb_avg,rb_worst))
    print("WR Average: %s. WR Worst: %s" %(wr_avg,wr_worst))
    print("TE Average: %s. TE Worst: %s" %(te_avg,te_worst))
    print("K Average: %s. K Worst: %s" %(k_avg,k_worst))
    print("DEF Average: %s. DEF Worst: %s" %(def_avg,def_worst))
    """

    all_available_vbd_scores = {}
    # we don't want to accidentally return a player for a filled position, so get a list of open slots
    open_positions = []
    for i in ["QB","RB","WR","TE","FLEX","K","DEF"]:
        if team.is_position_open(i):
            open_positions.append(i)

    # run through the list of available players and calculate their VBD score
    for i in range(0, len(available_players)):
        # Access the players projections as well as past yearly and weekly stats to make your decision
        player = player_history[available_players[i]]
        projection = player.yearly_data["Projected"].season_totals
        # skip players at a position that's already filled
        if player.position in open_positions:
            # get the VBD baselines for the various positions
            if player.position == "QB":
                avg_starter = qb_avg
                worst_starter = qb_worst
            if player.position == "RB":
                avg_starter = rb_avg
                worst_starter = rb_worst
            if player.position == "WR":
                avg_starter = wr_avg
                worst_starter = wr_worst
            if player.position == "TE":
                avg_starter = te_avg
                worst_starter = te_worst
            if player.position == "K":
                avg_starter = k_avg
                worst_starter = k_worst
            if player.position == "DEF":
                avg_starter = def_avg
                worst_starter = def_worst
            # calculate the vbd score for the player
            score_above_avg = projection.points - avg_starter
            score_above_worst = projection.points - worst_starter
            vbd_score = ((((score_above_avg*2)+(score_above_worst))/3)*.01)

            # create a dict matching the vbd score to the available players
            all_available_vbd_scores[vbd_score] = available_players[i]

    # get the top player score
    top_player_score = min(all_available_vbd_scores.keys(), key=(lambda k: all_available_vbd_scores[k]))
    # get the id/adp for the top player
    top_player_id = all_available_vbd_scores[top_player_score]
    return top_player_id

def draft_player(available_players, team):
    top_player_id = get_top_player(available_players, team)
    return top_player_id