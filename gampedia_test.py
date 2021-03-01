import re, pickle, operator
from collections import Counter, OrderedDict
from selenium import webdriver
from pprint import pprint
from tabulate import tabulate

class Match_Set:

	def get_Match_Count(self):
		return len(self.match_list)

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
		self.match_list += l_match_data[:-1]
		self.update += l_match_data[-1]

	def save_Data(self, file):
		self.match_list.append(self.update)
		self.save_obj(self.match_list, file)
		self.match_list = self.match_list[:-1]

	def update(self):
		self.match_list = []
		file_str = ""
		for update in self.update:
			self.get_Data(update[0], update[1], update[2])
			file_str += "{0} {1} {2} - ".format(update[0], update[1], update[2])
		file_str = file_str[:-3]
		self.save_Data(file_str)



	# str = '<tr><td><a href="/LCS/2021_Season/Spring_Season/Picks_and_Bans/4-6#Week_4" title="LCS/2021 Season/Spring Season/Picks and Bans/4-6">Week 4</a></td><td class="pbh-winner">FlyQuest</td><td>TSM</td><td>1 - 0</td><td>11.4</td><td class="pbh-ban pbh-blue pbh-cell">Azir</td><td class="pbh-ban pbh-red pbh-cell">Udyr</td><td class="pbh-ban pbh-blue pbh-cell">Olaf</td><td class="pbh-ban pbh-red pbh-cell">Seraphine</td><td class="pbh-ban pbh-blue pbh-cell">Hecarim</td><td class="pbh-ban pbh-red pbh-cell pbh-divider">Senna</td><td class="pbh-blue pbh-cell">Rell</td><td class="pbh-red pbh-cell">KaiSa, Skarner</td><td class="pbh-blue pbh-cell">Tristana, Gnar</td><td class="pbh-red pbh-cell pbh-divider">Jayce</td><td class="pbh-ban pbh-red pbh-cell">Twisted Fate</td><td class="pbh-ban pbh-blue pbh-cell">Alistar</td><td class="pbh-ban pbh-red pbh-cell">Jarvan IV</td><td class="pbh-ban pbh-blue pbh-cell pbh-divider">Pantheon</td><td class="pbh-red pbh-cell">Syndra</td><td class="pbh-blue pbh-cell">Dr. Mundo, Sylas</td><td class="pbh-red pbh-cell">Rakan</td><td>Support</td><td>Bot</td><td>Top</td><td>Jungle</td><td>Mid</td><td>Bot</td><td>Jungle</td><td>Top</td><td>Mid</td><td>Support</td></tr>'
	# match_list = [re.findall(r'(?<=>)[^<:]+(?=:?<)',x) for x in full_str.split("<tr><td>")[1:]]

	# print(Counter([x[5] for x in match_list if x[4] == "11.4"]))

	# rules for parsing matches from match_list:
	# 	0		Phase (ie, week of split/tournament)
	# 	1-2		Blue Side Team - Red Side Team
	# 	3		Score
	#	4		Patch
	#	5-10	Phase 1 bans (Alternating starting with BB1 and ending with RB3)
	#	11		Blue Side Pick 1
	#	12		Red Side Picks 1-2 (2 values separated by a comma)
	#	13		Blue Side Picks 2-3 (2 values separated by a comma)
	#	14		Red Side Pick 3
	#	15-18	Phase 2 bans (Alternating starting with RB4 and ending with BB5)
	#	19		Red Side Pick 4
	#	20		Blue Side Picks 4-5 (2 values separated by a comma)
	#	21		Red Side Pick 5
	#	22-31	Roles for the picks, going from Blue Side Pick 1 to Red Side Pick 5

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

	def get_BP1_Counts(self, patch=None, team=None, side=None):
		if side == "Blue":
			return Counter(self.get_BBP1_Raw(patch, team))
		elif side == "Red":
			return Counter(self.get_RBP1_Raw(patch, team))
		else:
			return Counter(self.get_Full_BP1_Raw(patch, team))

	def get_BPP1_Raw(self, patch=None, team=None):
		if patch == None:
			if team == None:
				return [x[11] for x in self.match_list]
			else:
				return [x[11] for x in self.match_list if x[1] == team]
		else:
			if team == None:
				return [x[11] for x in self.match_list if x[4] == patch]
			else:
				return [x[11] for x in self.match_list if x[1] == team and x[4] == patch]

	def get_Champ_Percent(self, champ, patch=None, team=None):
		count = 0
		if patch == None:
			if team == None:
				for match in self.match_list:
					found = False
					for slot in (self.ban_pool + self.s_pick_pool):
						if match[slot] == champ:
							count += 1
							found = True
							break
					if not found:
						for slot in self.d_pick_pool:
							champs = match[slot].split(",")
							if champs[0] == champ or champs[1] == champ:
								count += 1
								found = True
								break
				return (count, len(self.match_list))
			else:
				s_match_list = [x for x in self.s_match_history if x[1] == team or x[2] == team]
				for match in s_match_list:
					found = False
					for slot in (self.ban_pool + self.s_pick_pool):
						if match[slot] == champ:
							count += 1
							found = True
							break
					if not found:
						for slot in self.d_pick_pool:
							champs = match[slot].split(",")
							if champs[0] == champ or champs[1] == champ:
								count += 1
								found = True
								break
				return (count, len(s_match_list))
		else:
			if team == None:
				s_match_list = [x for x in self.match_list if x[4] == patch]
				for match in s_match_list:
					found = False
					for slot in (self.ban_pool + self.s_pick_pool):
						if match[slot] == champ:
							count += 1
							found = True
							break
					if not found:
						for slot in self.d_pick_pool:
							champs = match[slot].split(",")
							if champs[0] == champ or champs[1] == champ:
								count += 1
								found = True
								break
				return (count, len(s_match_list))
			else:
				s_match_list = [x for x in self.match_list if (x[1] == team or x[2] == team) and x[4] == patch]
				for match in s_match_list:
					found = False
					for slot in (self.ban_pool + self.s_pick_pool):
						if match[slot] == champ:
							count += 1
							found = True
							break
					if not found:
						for slot in self.d_pick_pool:
							champs = match[slot].split(",")
							if champs[0] == champ or champs[1] == champ:
								count += 1
								found = True
								break
				return (count, len(s_match_list))

	def print_Champ_Percent_by_Patch(self, champ, start, limit, team=None):
		print("Number of {0} Picks/Bans from Patch 11.{1} to 11.{2} in the {3} during {4}:".format(champ, str(start), str(limit), self.league, self.year))
		old_percent = None
		for x in range(start, limit+1):
			patch_str = "11." + str(x)
			patch_stats = self.get_Champ_Percent(champ, patch_str)
			patch_percent = (patch_stats[0]/patch_stats[1]) * 100.00
			if old_percent is None:
				old_percent = patch_percent
			patch_delta = round((patch_percent - old_percent), 2)
			old_percent = patch_percent
			
			print("		{0}: {1}/{2}	|	{3} ({4:+g})".format(patch_str, patch_stats[0], patch_stats[1], format(patch_percent, ".2f"), patch_delta))

	# Implement patch/team functionality
	def get_Picked_Champ_List(self):
		master_list = []
		for match in self.match_list:
			sub_list = []
			sub_list.append(match[11])
			bp23 = match[13].split(",")
			sub_list += bp23
			bp45 = match[20].split(",")
			sub_list += bp45
			rp12 = match[12].split(",")
			sub_list += rp12
			sub_list.append(match[14])
			sub_list.append(match[19])
			sub_list.append(match[21])
			master_list.append(sub_list)
		return master_list

	def get_Champ_Role_Dict(self):
		master_list = []
		for match in self.match_list:
			sub_dict = {}
			for i in range(22, 27):
				q_str = "Blue " + match[i]
				sub_dict[q_str] = i
			for j in range(27, 32):
				q_str = "Red " + match[j]
				sub_dict[q_str] = j
			master_list.append(sub_dict)
		return master_list

	def get_Champ_List_with_Dict(self, patch=None, team=None):
		master_list = []
		master_dict = []
		if patch != None:
			s_match_list = [x for x in self.match_list if x[4] == patch]
		elif team != None:
			s_match_list = [x for x in self.match_list if x[1] == team or x[2] == team]
		else:
			s_match_list = self.match_list
		if team == None:
			for match in s_match_list:
				sub_list = []
				sub_list.append(match[11])
				bp23 = match[13].split(", ")
				sub_list += bp23
				bp45 = match[20].split(", ")
				sub_list += bp45
				rp12 = match[12].split(", ")
				sub_list += rp12
				sub_list.append(match[14])
				sub_list.append(match[19])
				sub_list.append(match[21])
				master_list.append(sub_list)
				sub_dict = {}
				for i in range(22, 27):
					q_str = "Blue " + match[i]
					sub_dict[q_str] = (i-22)
				for j in range(27, 32):
					q_str = "Red " + match[j]
					sub_dict[q_str] = (j-22)
				master_dict.append(sub_dict)
		else:
			for match in s_match_list:
				sub_list = []
				sub_dict = {}
				if match[1] == team:
					sub_list.append(match[11])
					bp23 = match[13].split(", ")
					sub_list += bp23
					bp45 = match[20].split(", ")
					sub_list += bp45
					for i in range(22, 27):
						q_str = match[i]
						sub_dict[q_str] = (i-22)
				else:
					rp12 = match[12].split(", ")
					sub_list += rp12
					sub_list.append(match[14])
					sub_list.append(match[19])
					sub_list.append(match[21])
					for j in range(27, 32):
						q_str = match[j]
						sub_dict[q_str] = (j-27)
				master_list.append(sub_list)
				master_dict.append(sub_dict)
		return (master_list, master_dict)

	def get_Champs_by_Role(self, role, patch=None, team=None):
		list_w_dict = self.get_Champ_List_with_Dict(patch, team)
		champ_list = list_w_dict[0]
		champ_dict_list = list_w_dict[1]
		if team is None:
			blue_role = []
			red_role = []
			for i in range(len(champ_list)):
				champs = champ_list[i]
				champ_dict = champ_dict_list[i]
				blue_role.append(champs[champ_dict["Blue " + role]])
				red_role.append(champs[champ_dict["Red " + role]])
			return (blue_role, red_role)
		else:
			roles = []
			for i in range(len(champ_list)):
				champs = champ_list[i]
				champ_dict = champ_dict_list[i]
				roles.append(champs[champ_dict[role]])
			return (roles, [])

	def print_Blue_vs_Red_by_Role(self, role, patch=None):
		blue_red = self.get_Champs_by_Role(role, patch)
		blue = Counter(blue_red[0])
		red = Counter(blue_red[1])
		total = Counter(blue_red[0] + blue_red[1])
		total_set = set(blue + red)
		champ_arr = []
		for champ in total_set:
			blue_count = "{0}".format(blue[champ])
			blue_percent = "{0}".format(format((blue[champ]/len(blue_red[0]) * 100.00), ".2f"))
			red_count = "{0}".format(red[champ])
			red_percent = "{0}".format(format((red[champ]/len(blue_red[1]) * 100.00), ".2f"))
			total_count = "{0}".format(total[champ])
			total_percent = "{0}".format(format((total[champ]/len(blue_red[0]+blue_red[1]) * 100.00), ".2f"))
			total_sort = total[champ]
			champ_info = [total_sort, champ, blue_count, blue_percent, red_count, red_percent, total_count, total_percent]
			champ_arr.append(champ_info)
		cap1 = [-1, "------------", "------------", "------------", "------------", "------------", "------------", "------------"]
		cap2 = [-2, "TOTAL", sum([float(x[2]) for x in champ_arr]), sum([float(x[3]) for x in champ_arr]), sum([float(x[4]) for x in champ_arr]), sum([float(x[5]) for x in champ_arr]), sum([float(x[6]) for x in champ_arr]), sum([float(x[7]) for x in champ_arr])]
		champ_arr.append(cap1)
		champ_arr.append(cap2)
		if patch != None:
			patch = " on Patch "+patch+" "
		else:
			patch = " "
		print("\nNumber/Percentage for Champs picked as {0} on Blue and Red Side in the {1}{3}during {2}:\n".format(role, self.league, self.year, patch))
		# print("{:>24}{:>12}".format("Blue", "Red"))
		champ_arr = sorted(champ_arr, key=lambda x: x[0], reverse=True)
		# for champ in champ_arr:
		# 	print("{:>12}{:>12}{:>12}".format(champ[0], champ[1], champ[2]))
		print(tabulate([x[1:] for x in champ_arr], headers=["Champion", "Blue Count", "Blue Percentage", "Red Count", "Red Percentage", "Total Count", "Total Percentage"]))



	def __init__(self, input, get=False):
		self.match_list = []
		self.update = []
		self.ban_pool = [5,6,7,8,9,10,15,16,17,18]
		self.s_pick_pool = [11,14,19,21]
		self.d_pick_pool = [12,13,20]
		file_str = ""
		league = ""
		year = set()
		if get:
			self.update = input
			for update in input:
				self.get_Data(update[0], update[1], update[2])
				file_str += "{0} {1} {2} - ".format(update[0], update[1], update[2])
				league += (update[0] + "/")
				year.add(int(update[1]))
			file_str = file_str[:-3]
			self.league = league[:-1]
			self.year = ""
			for y in sorted(list(year)):
				self.year += (str(y) + "/")
			self.year = self.year[:-1]
			self.save_Data(file_str)
		else:
			for file in input:
				file_str += "{0} {1} {2} - ".format(file[0], file[1], file[2])
				league += (file[0] + "/")
				year.add(int(file[1]))
			self.load_Data(file_str[:-3])
			self.league = league[:-1]
			self.year = ""
			for y in sorted(list(year)):
				self.year += (str(y) + "/")
			self.year = self.year[:-1]
			self.save_Data(file_str)

# test = Match_Set([["LCS", "2021", "Spring"], ["LEC", "2021", "Spring"]], None)
# test.save_Data("LCS-LEC 2021 Spring (2-28)")

def get_Count_Percent(counter):
	count_len = sum(counter.values())
	percent_count = sorted([(i, counter[i]/count_len * 100.0) for i in counter], key=lambda x: x[1], reverse=True)
	return(percent_count) 

def print_Format_Count(count, rec=None, rev=False):
	count = sorted(count.items(), key=operator.itemgetter(1), reverse=rev)
	if rec != None:
		for x in count:
			p_string = "	{0}: {1}%".format(x[0], round(x[1], 2))
			r_string = p_string + (" " * (40 - len(p_string))) + rec[x[0]]
			print(r_string)
	else:
		for x in count:
			p_string = "	{0}: {1}".format(x[0], round(x[1], 2))
			print(p_string)

# print_Count_Compare(lcs_bbp1, lec_bbp1, "LCS", "LEC", "PHASE 1 BANS")
def print_Count_Compare(c1, c2, n1="SET 1", n2="SET 2", term="SELECTIONS"):
	p1 = get_Count_Percent(c1)
	p2 = get_Count_Percent(c2)
	base_insec = set(c1.keys()).intersection(c2.keys())
	difference = {}
	rec = {}
	for k in base_insec:
		difference[k] = dict(p1)[k] - dict(p2)[k]
		rec[k] = "( {0} [{2}] - {1} [{3}] )".format(c1[k], c2[k], n1, n2)
	unique1 = sorted([v for v in c1.keys() if v not in c2.keys()], key=lambda x: c1[x], reverse=True)
	unique2 = sorted([v for v in c2.keys() if v not in c1.keys()], key=lambda x: c2[x], reverse=True)
	print("DIFFERENCES IN {0}: ".format(term))
	print_Format_Count(difference, rec, True)
	print("UNIQUE {0} FOR {1}: ".format(term, n1))
	for k1 in unique1:
		print("	{0} ({1})".format(k1, c1[k1]))
	print("UNIQUE {0} FOR {1}: ".format(term, n2))
	for k2 in unique2:
		print("	{0} ({1})".format(k2, c2[k2]))

# LCS_Set = Match_Set(None, ["LCS 2021 Spring (2-28)"])
# LEC_Set = Match_Set(None, ["LEC 2021 Spring (2-28)"])
# West_Set = Match_Set(None, ["LCS-LEC 2021 Spring (2-28)"])

LCS_Set = Match_Set([["LCS", "2021", "Spring"]])
LEC_Set = Match_Set([["LEC", "2021", "Spring"]])
West_Set = Match_Set([["LCS", "2021", "Spring"], ["LEC", "2021", "Spring"]])



# lcs_bbp1 = LCS_Set.get_BP1_Counts(None, None, "Blue")
# lec_bbp1 = LEC_Set.get_BP1_Counts(None, None, "Blue")
# print_Count_Compare(lcs_bbp1, lec_bbp1, "LCS", "LEC", "PHASE 1 BANS")
# print("LCS BLUE SIDE BAN PHASE 1: ")
# print_Format_Count(lcs_bbp1, None, True)

# lcs_bpp1 = Counter(LCS_Set.get_BPP1_Raw())
# lec_bpp1 = Counter(LEC_Set.get_BPP1_Raw())
 

# print_Format_Count(Counter(LCS_Set.get_BPP1_Raw()), None, True)
# print_Count_Compare(lcs_bpp1, lec_bpp1, "LCS", "LEC", "FIRST PICK")

# print(LCS_Set.get_Champ_Percent("Kai'Sa", "11.4"))
# print(LEC_Set.get_Champ_Percent("Kai'Sa", "11.4"))

# LCS_Set.print_Champ_Percent_by_Patch("Kai'Sa", 2, 4)

# pprint(LCS_Set.get_Picked_Champ_List())
# pprint(LCS_Set.get_Champs_by_Role("Bot"))
# pprint(LCS_Set.print_Blue_vs_Red_by_Role("Bot"))
# pprint(LEC_Set.print_Blue_vs_Red_by_Role("Top", None))
# pprint(Counter(LCS_Set.get_Champs_by_Role("Bot", None,"Cloud9")[0]))
test = Counter(LCS_Set.get_Champs_by_Role("Bot", None,"Cloud9")[0])
print_Format_Count(test, None, True)

# pprint(West_Set.print_Blue_vs_Red_by_Role("Bot"))
# return "	{0}: {1}/{2}".format("", count, len(s_match_list))