class Player:
    def __init__(self, name, level, tier, rank, lp, mmr, lpdelta, dailywins, wins, losses, yesterdaysDelta):
        self.name = name
        self.level = level
        self.tier = tier
        self.rank = rank
        self.lp = lp
        self.mmr = mmr
        self.lpdelta = lpdelta
        self.dailywins = dailywins
        self.wins = wins
        self.losses = losses
        self.yesterdaysDelta = yesterdaysDelta
