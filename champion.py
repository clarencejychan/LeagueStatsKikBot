import requests
riotKey = 'RGAPI-33ddda68-2769-46cc-8a03-1c8c393551ad'


class Champion:
	championID = None
	numDeaths = None
	numKills = None
	numAssists = None
	totalSessions = None
	championName = None
	championImageURL = None


	def __init__(self, championID, numDeaths, numKills, numAssists, totalSessions):
		self.championID = championID
		self.numDeaths = numDeaths
		self.numKills = numKills
		self.numAssists = numAssists
		self.totalSessions = totalSessions

		URL = 'https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/' + str(championID) + '?champData=image&api_key=' + riotKey
		r = requests.get(URL)
		self.championName = r.json()['name']
		
		self.championImageURL = 'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/' + r.json()['name'] + '_0.jpg'


	def __repr__(self):
		return str(self.championID)

	def getKDA(self):
		return round(((self.numKills + self.numAssists) / self.numDeaths), 2)

	def getChampionName(self):
		return self.championName

	def getChampionImgURL(self):
		return self.championImageURL







