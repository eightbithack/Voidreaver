import re, pickle
from collections import Counter
from selenium import webdriver


class Match_Set:
	def save_obj(self, obj, name ):
	    with open('obj/'+ name + '.pkl', 'wb') as f:
	        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

	def load_obj(self, name ):
	    with open('obj/' + name + '.pkl', 'rb') as f:
	        return pickle.load(f)

	def get_Data(self, league, year, split):
		driver = webdriver.Firefox()
		driver.get("https://lol.gamepedia.com/Special:RunQuery/PickBanHistory?PBH%5Bpage%5D={0}+{1}+{2}&PBH%5Btextonly%5D=Yes&pfRunQueryFormName=PickBanHistory".format(league, year, split))

		# This will get the initial html - before javascript
		html1 = driver.page_source

		# This will get the html after on-load javascript
		html2 = driver.execute_script("return document.getElementById('pbh-table').innerHTML;")
		q_match_list = [re.findall(r'(?<=>)[^<:]+(?=:?<)',x) for x in html2.split("<tr><td>")[1:]]
		self.match_list += q_match_list

		driver.close()
		driver.quit()

	def load_Data(self, file):
		l_match_data = self.load_obj(file)
		self.match_list += l_match_data

	def save_Data(self, file):
		self.save_obj(self.match_list, file)


	# str = '<tr><td><a href="/LCS/2021_Season/Spring_Season/Picks_and_Bans/4-6#Week_4" title="LCS/2021 Season/Spring Season/Picks and Bans/4-6">Week 4</a></td><td class="pbh-winner">FlyQuest</td><td>TSM</td><td>1 - 0</td><td>11.4</td><td class="pbh-ban pbh-blue pbh-cell">Azir</td><td class="pbh-ban pbh-red pbh-cell">Udyr</td><td class="pbh-ban pbh-blue pbh-cell">Olaf</td><td class="pbh-ban pbh-red pbh-cell">Seraphine</td><td class="pbh-ban pbh-blue pbh-cell">Hecarim</td><td class="pbh-ban pbh-red pbh-cell pbh-divider">Senna</td><td class="pbh-blue pbh-cell">Rell</td><td class="pbh-red pbh-cell">KaiSa, Skarner</td><td class="pbh-blue pbh-cell">Tristana, Gnar</td><td class="pbh-red pbh-cell pbh-divider">Jayce</td><td class="pbh-ban pbh-red pbh-cell">Twisted Fate</td><td class="pbh-ban pbh-blue pbh-cell">Alistar</td><td class="pbh-ban pbh-red pbh-cell">Jarvan IV</td><td class="pbh-ban pbh-blue pbh-cell pbh-divider">Pantheon</td><td class="pbh-red pbh-cell">Syndra</td><td class="pbh-blue pbh-cell">Dr. Mundo, Sylas</td><td class="pbh-red pbh-cell">Rakan</td><td>Support</td><td>Bot</td><td>Top</td><td>Jungle</td><td>Mid</td><td>Bot</td><td>Jungle</td><td>Top</td><td>Mid</td><td>Support</td></tr>'
	# match_list = [re.findall(r'(?<=>)[^<:]+(?=:?<)',x) for x in full_str.split("<tr><td>")[1:]]

	# print(Counter([x[5] for x in match_list if x[4] == "11.4"]))

	# rules for parsing matchs from match_list:
	# 	0		Phase (ie, week of split/tournament)
	# 	1-2		Blue Side Team - Red Side Team
	# 	3		Score
	#	4		Patch
	#	5-10	Phase 1 bans (Alternating starting with BB1 and ending with RB3)

	def get_column(self, col):
		return [x[col] for x in self.match_list]
	              
	def get_BBP1_Raw(self, patch=None, team=None):
		if patch == None:
			if team == None:
				BB1 = [x[5] for x in self.match_list]
				BB2 = [x[7] for x in self.match_list]
				BB3 = [x[9] for x in self.match_list]
			else:
				BB1 = [x[5] for x in self.match_list if x[1] == team]
				BB2 = [x[7] for x in self.match_list if x[1] == team]
				BB3 = [x[9] for x in self.match_list if x[1] == team]
		else:
			if team == None:
				BB1 = [x[5] for x in self.match_list if x[4] == patch]
				BB2 = [x[7] for x in self.match_list if x[4] == patch]
				BB3 = [x[9] for x in self.match_list if x[4] == patch]
			else:
				BB1 = [x[5] for x in self.match_list if x[4] == patch and x[1] == team]
				BB2 = [x[7] for x in self.match_list if x[4] == patch and x[1] == team]
				BB3 = [x[9] for x in self.match_list if x[4] == patch and x[1] == team]
		BB_full = BB1 + BB2 + BB3
		return(BB_full)

	def get_RBP1_Raw(self, patch=None, team=None):
		if patch == None:
			if team == None:
				RB1 = [x[6] for x in self.match_list]
				RB2 = [x[8] for x in self.match_list]
				RB3 = [x[10] for x in self.match_list]
			else:
				RB1 = [x[6] for x in self.match_list if x[2] == team]
				RB2 = [x[8] for x in self.match_list if x[2] == team]
				RB3 = [x[10] for x in self.match_list if x[2] == team]
		else:
			if team == None:
				RB1 = [x[6] for x in self.match_list if x[4] == patch]
				RB2 = [x[8] for x in self.match_list if x[4] == patch]
				RB3 = [x[10] for x in self.match_list if x[4] == patch]
			else:
				RB1 = [x[6] for x in self.match_list if x[4] == patch and x[2] == team]
				RB2 = [x[8] for x in self.match_list if x[4] == patch and x[2] == team]
				RB3 = [x[10] for x in self.match_list if x[4] == patch and x[2] == team]
		RB_full = RB1 + RB2 + RB3
		return(RB_full)

	def get_Full_BP1_Raw(self, patch=None, team=None):
		BBP1 = self.get_BBP1_Raw(patch, team)
		RBP1 = self.get_RBP1_Raw(patch, team)
		return(BBP1 + RBP1)

	def get_BP_Counts(self, patch=None, team=None, side=None):
		if side == "Blue":
			return Counter(self.get_BBP1_Raw(patch, team))
		elif side == "Red":
			return Counter(self.get_RBP1_Raw(patch, team))
		else:
			return Counter(self.get_Full_BP1_Raw(patch, team))

	def __init__(self, update_params=None, get_files=None):
		self.match_list = []
		if update_params != None:
			for update in update_params:
				self.get_Data(update[0], update[1], update[2])
		if get_files != None:
			for file in get_files:
				self.load_Data(file)

# test = Match_Set([["LCS", "2021", "Spring"], ["LEC", "2021", "Spring"]], None)
# test.save_Data("LCS-LEC 2021 Spring (2-28)")

LCS_Set = Match_Set([["LCS", "2021", "Spring"]], None)
LCS_Set.save_Data("LCS 2021 Spring (2-28)")
LEC_Set = Match_Set([["LEC", "2021", "Spring"]], None)
LEC_Set.save_Data("LEC 2021 Spring (2-28)")

# def get_BBP1_spec(patch, team):


# print(get_BP_Counts())
# print(len(match_list[0]))

# for match in match_list[:1]:
# 	match = re.findall(r'(?<=>)[^<:]+(?=:?<)',str)
# 	print(match)
