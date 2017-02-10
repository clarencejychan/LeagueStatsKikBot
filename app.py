from flask import Flask, request, Response
import requests, json
from champion import *
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, StartChattingMessage, IsTypingMessage

app = Flask(__name__)
kik = KikApi("leaguestats", "d7fdd8fa-d642-4517-bda4-2392a5820db4")
api_key = "d7fdd8fa-d642-4517-bda4-2392a5820db4"
riotKey = 'RGAPI-33ddda68-2769-46cc-8a03-1c8c393551ad'

kik.set_configuration(Configuration("https://1556b3a4.ngrok.io/inc"))

@app.route('/inc', methods=['POST'])
def inc():
	if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
		return Response(status=403)
	
	#chatID = None
	chatMessage = None
	greetingMessage = "Welcome to LeagueStats! Type in your summoner name in order to find out your\
	worst 3 champions!"
	userNotExist = "This user doesn't exist, please try to enter another summoner name."



	messages = messages_from_json(request.json['messages'])


	for message in messages:
		if isinstance(message, StartChattingMessage):
			kik.send_messages([
					TextMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						body = greetingMessage
						)


				])

		if isinstance(message, TextMessage):
			kik.send_messages([
					IsTypingMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						is_typing = True	
					)
				])

			searchName = (message.body).lower()
			summInfoJson = requests.get('https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/' + searchName + '?api_key=' + riotKey)
			if summInfoJson.status_code == 404:
				chatMessage = userNotExist

				kik.send_messages([
					TextMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						body = chatMessage
						)
				])
				break


			summInfoId = str(summInfoJson.json()[searchName]['id'])			
			summChampInfoJson = requests.get('https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/' + summInfoId + '/ranked?season=SEASON2017&api_key=' + riotKey)
			summChampInfo = summChampInfoJson.json()

			if summChampInfoJson.status_code == 404:
				chatMessage = userNotExist
				kik.send_messages([
					TextMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						body = chatMessage
						)
				])
				break


			champInfo = summChampInfo['champions']
			champArray = []

			for champion in champInfo:
				if champion['id'] == 0:
					break
				temp = Champion(champion['id'], champion['stats']['totalDeathsPerSession'], champion['stats']['totalChampionKills'], champion['stats']['totalAssists'], champion['stats']['totalSessionsPlayed'])
				champArray.append(temp)


				# sorted by KDA
			sortedChampInfo = sorted(champArray, key=lambda x: x.getKDA())
				
			#sort out the champions -> take top 3 worst KDA.

			top3 = sortedChampInfo[:3]
			finalList = []

			for champion in top3:
				temp = [champion.championName, champion.getChampionImgURL(), champion.getKDA(), champion.numDeaths, champion.numKills, champion.totalSessions]
				finalList.append(temp)

			print(finalList)

			champ1 = finalList[0][0]
			champ2 = finalList[1][0]
			champ3 = finalList[2][0]

			kik.send_messages([
					TextMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						body = "Your top 3 worst champions are " + champ1 + ' , ' + champ2 + ' , ' + champ3
					),
					TextMessage(
						to = message.from_user,
						chat_id = message.chat_id,
						body = "Send another message to search for another summoner."
					)
				])

	return Response(status=200)

if __name__ == "__main__":
	app.run(port=4040, debug=True)
