#WARNING, this script is CHAOTIC and the product of years of spontaneous and random contribution, often in a hurried fashion, proceed at your own risk

import requests, json, urllib.request, pickle, time, sys, os.path, math, copy
from datetime import datetime
from lxml import etree
from lxml.etree import tostring
from operator import itemgetter
from bs4 import BeautifulSoup

banking_alliance_id = '6088' #ID of the alliance the sender is currently in

run_audit = True #True means it'll print out a very basic audit sometime during its run

brick_the_send = False #True means it'll literally crash before sending anything no matter what
brick_resources_low = True #True means it won't send unless it has all it needs, False means it'll send a proportional amount

dump_to_offshore_global = True #True means, after it's done sending, it'll dump to the provided offshore name
offshore_name = 'Rain' #Offshore name to dump to when done sending

API_key = 'xxxxxxxxxxxxx' #API KEY of the sender/user here

alliance_mode = 0 #0 test, 1 eclipse        #Simple switch for servicing multiple branches seperately

if alliance_mode == 0:
    allianceid_apikey_pair_dict_list = [{'key': 'xxxxxxxxxxxxx', 'alliance_id' : '6088'}, {'key': 'xxxxxxxxxxxxx', 'alliance_id' : '9999'}] #Give key with corresponding alliance id
    allianceid_apikey_dict = {'6088' : 'xxxxxxxxxxxxx', '9999' : 'xxxxxxxxxxxxx'} #Give key with corresponding alliance id

    taxid_list = ['11656', '16894'] #Tax ids to check in order with the alliance ids...
    allianceid_list = ['6088', '9999'] #Provided here
    
elif alliance_mode == 1:
    allianceid_apikey_pair_dict_list = [{'key': 'xxxxxxxxxxxxx', 'alliance_id' : '7450'}, {'key': 'xxxxxxxxxxxxx', 'alliance_id' : '9427'}]
    allianceid_apikey_dict = {'7450' : 'xxxxxxxxxxxxx', '9427' : 'xxxxxxxxxxxxx'}

    taxid_list = ['9284', '15214']
    allianceid_list = ['7450', '9427']

user_email = 'EMAIL' #User email of sender
user_password = 'PASSWORD' #User password of sender

accept_applicants_as_programmees = False #If True, applicants in the selected tax bracket(s) will still be sent resources

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'} #Periodcally update with the most common user agent

send_wc = True #if True will send WC based off next two switches, if False it won't send anything regardless of the next two switches
WAR_maint_wc = True #priority 1 "WAR" WC preset
PEACE_maint_WC = True #priority 2 "PEACE" WC preset
wc_money_mult = 1.0 #Multiply WC money by this, regardless of preset

send_resource_multipler = 5.0 #7.09 for a week and a turn, 8.09 for an extra day #How many days worth of raws to send

send_food_and_uranium_buffer = True #If True, uranium and food sent will be multiplied by food_and_uranium_multipler
food_and_uranium_multipler = 2.0 #2.0 for buffer

top_off_mode = True #If True, the script will look at how much the nation has on hand and subtract that from how much the nation needs to function for the amount of time set by send_resource_multipler, if False the script will send the amount calculated regardless with no deductions

trader_id_list = [] #If a nation id is present here, it won't get top off'd no matter what and will get the flat sum regardless



APIKey = API_key
current_weekday = datetime.today().weekday()
print("Current weekday: " + str(current_weekday))

def get_nations_with_given_alliance_id(apiv2_json, alliance_id):
    collected_nations = []
    for nation in apiv2_json:
        if nation['alliance_id'] == alliance_id:
            collected_nations.append(nation)
    return collected_nations

def returnCityDictionary(city_manager_tree, cityCount, nationContinent):
    cityCounter = 3
    cityDict = {}
    
    while cityCounter <= cityCount + 2:
        #city = {"cityAge": 0, "infra": 0, "land": 0, "population": 0, "disease": 0, "crime": 0, "pollution": 0, "commerce": 0, "powered": 0, "coalPower": 0, "oilPower": 0, "nuclearPower": 0, "windPower": 0, "coalMines": 0,"oilWells": 0, "bauxiteMines": 0, "ironMines": 0, "leadMines": 0, "uraniumMines": 0, "farms": 0, "oilRefineries": 0, "steelMills": 0, "aluminumRefineries": 0, "munitionsFactories": 0, "policeStations": 0, "hospitals": 0, "recyclingCenters": 0, "subways": 0, "supermarkets": 0, "banks": 0, "shoppingMalls": 0, "stadiums": 0, "barracks": 0, "factories": 0, "hangars": 0, "drydocks": 0}        
        city = {"population" : 0, "commerce" : 0.0, "land": 0, "coalPower": 0, "oilPower": 0, "nuclearPower": 0, "windPower" : 0, "coalMines": 0,"oilWells": 0, "bauxiteMines": 0, "ironMines": 0, "leadMines": 0, "uraniumMines": 0, "farms": 0, "oilRefineries": 0, "steelMills": 0, "aluminumRefineries": 0, "munitionsFactories": 0}

        city["cityAge"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[2]/td[' + str(cityCounter) + ']/text()')[0].replace(',', '').replace(' days', ''))
        city["infra"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[3]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["land"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[4]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["population"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[5]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["disease"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[6]/td[' + str(cityCounter) + ']/text()')[0].replace('%', ''))
        city["crime"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[7]/td[' + str(cityCounter) + ']/text()')[0].replace('%', ''))
        city["pollution"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[8]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["commerce"] = float(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[9]/td[' + str(cityCounter) + ']/text()')[0].replace('%', ''))
        city["powered"] = str(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[10]/td[' + str(cityCounter) + ']/text()')[0].replace('%', ''))
        
        city["coalPower"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[11]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["oilPower"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[12]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["nuclearPower"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[13]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["windPower"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[14]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        
        city["farms"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[18]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["oilRefineries"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[19]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["steelMills"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[20]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["aluminumRefineries"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[21]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["munitionsFactories"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[22]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))

        city["policeStations"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[23]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["hospitals"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[24]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["recyclingCenters"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[25]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["subways"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[26]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        
        city["supermarkets"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[27]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["banks"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[28]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["shoppingMalls"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[29]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["stadiums"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[30]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        
        city["barracks"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[31]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["factories"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[32]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["hangars"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[33]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        city["drydocks"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[34]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))

        
        if nationContinent == "Europe":
            city["coalMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["ironMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["leadMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "North America":
            city["coalMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["ironMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["uraniumMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "Asia":
            city["oilWells"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["ironMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["uraniumMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "Africa":
            city["oilWells"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["bauxiteMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["uraniumMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "South America":
            city["oilWells"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["bauxiteMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["leadMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "Australia":
            city["coalMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["bauxiteMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["leadMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
        elif nationContinent == "Antarctica":
            city["oilWells"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[16]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["coalMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[15]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))
            city["uraniumMines"] = int(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[17]/td[' + str(cityCounter) + ']/text()')[0].replace(',', ''))

        cityDict[str(cityCounter-2)] = city

        cityCounter += 1
    return cityDict

def print_nations_from_given_list_that_are_lazy(nations):
    flagged_nations = []
    for nation in nations:
        if nation['offensive_wars'] < 1:
            if nation['defensive_wars'] < 2:
                nation_max_planes = nation['cities'] * 90
                if nation['aircraft'] / nation_max_planes > 0.6:
                    flagged_nations.append(nation['nation_id'])
    print("LAZY BOYS: " + str(flagged_nations))

def scan_nation_search_page(loops, taxid):
    looping = True

    '''
    current_datetime = datetime.utcnow().time()
    if (int(current_datetime.hour) % 2) != 0:
        if (60 - int(current_datetime.minute)) <= 2:
            print('DELAYING BY(2): ' + str(((60 - int(current_datetime.minute)) + 3)*60))
            time.sleep(((60 - int(current_datetime.minute)) + 5)*60)
    '''
    
    nations_tree = etree.fromstring(requests.get('https://politicsandwar.com/index.php?id=15&tax_id=' + str(taxid) + '&keyword=&cat=everything&ob=date&od=DESC&maximum=50&minimum=' + str(loops * 50) + '&search=Go', headers=headers).content, etree.HTMLParser())
    #print(tostring(nations_tree))
    #print(nations_tree.xpath('//*[@id="rightcolumn"]/p/text()'))
    #nations_tree = etree.fromstring(requests.get('https://politicsandwar.com/index.php?id=15&keyword=&cat=everything&ob=date&od=DESC&maximum=50&minimum=' + str(loops * 50), headers=headers).content, etree.HTMLParser())
    try:
        total_nations = nations_tree.xpath('//*[@id="rightcolumn"]/p/text()')[0].replace(' Nations', '')
        total_nations = int(total_nations[total_nations.index(' of ')+4:])
        #print(total_nations)
        #total_nations = int(nations_tree.xpath('//*[@id="rightcolumn"]/p/text()')[0][len(str(loops * 50)) + len(str((loops+1) * 50)) + 13:-8])
    except Exception as ex:
        print("scan_nation_search_page FAIL1:" + str('https://politicsandwar.com/index.php?id=15&tax_id=' + str(taxid) + '&keyword=&cat=everything&ob=date&od=DESC&maximum=50&minimum=' + str(loops * 50) + '&search=Go') + ' ' + str(loops))
        print(nations_tree.xpath('//*[@id="rightcolumn"]/p/text()')[0])
        print(nations_tree.xpath('//*[@id="rightcolumn"]/p/text()')[0][len(str(loops * 50)) + len(str((loops+1) * 50)) + 13:-8])
        print(datetime.utcnow().time())
        print(tostring(nations_tree))
        print(ex)
        brick
        return
    #print(nations_tree.xpath('//*[@id="rightcolumn"]/div/div/div/table/tr[*]')) ##//*[@id="rightcolumn"]/div/div/div/table/tr[1]
    nations_found = len(nations_tree.xpath('//*[@id="rightcolumn"]/div/div/div/table/tr[*]')) - 1
    #print(nations_found)
    nation_rows_on_page = nations_tree.xpath('//*[@id="rightcolumn"]/div/div/div/table/tr[*]')[1:]
    try:
        if nation_rows_on_page:
            last_nation_number = int(nation_rows_on_page[-1].xpath('./td[1]/text()')[0][:-1])
        else:
            looping = False
    except:
        looping = False
        return looping, {}
    #print(str(last_nation_number) + "\n")

    #print(total_nations, nations_found, last_nation_number)
    
    if nations_found < 50:
        looping = False
    if total_nations <= last_nation_number:
        looping = False
        
    temp_nation_dict_list = []
    for nation_row in nation_rows_on_page:
        temp_nation_dict = {}
        nation_name_cell_text = nation_row.xpath('./td[2]/text()')
        if len(nation_name_cell_text) == 4:
            temp_nation_dict['leader_name'] = nation_name_cell_text[2][30:-1].replace('            ', '').replace(' \r\n         ', '')
        elif len(nation_name_cell_text) == 3:
            temp_nation_dict['leader_name'] = nation_name_cell_text[2][30:-23].replace('            ', '').replace(' \r\n         ', '')
        else:
            print("ERROR: UNEXPECTED NUMBER OF LINES IN NATION NAME")

        temp_nation_dict['nation_name'] = nation_row.xpath('./td[2]/a/text()')[0][:-1]
        temp_nation_dict['nation_id'] = int(nation_row.xpath('./td[2]/a/@href')[0][37:])
        temp_nation_dict['nation_creation_date'] = nation_row.xpath('./td[3]/text()')[0][:-1]
        temp_nation_dict['nation_color'] = nation_row.xpath('./td[5]/img/@title')[0]
        temp_nation_dict['nation_city_count'] = nation_row.xpath('./td[6]/text()')[0]
        temp_nation_dict['nation_score'] = nation_row.xpath('./td[7]/text()')[0][2:].replace(',', '')
        
        if nation_row.xpath('./td[4]/text()'):
            temp_nation_dict['alliance_name'] = "None"
            temp_nation_dict['alliance_id'] = None
            temp_nation_dict['applicant_bool'] = False
        else:
            temp_nation_dict['alliance_name'] = nation_row.xpath('./td[4]/a/text()')[0]
            temp_nation_dict['alliance_id'] = int(nation_row.xpath('./td[4]/a/@href')[0][39:])
            if nation_row.xpath('./td[4]/span/text()'):
                if nation_row.xpath('./td[4]/span/text()')[0] == 'Applicant':
                    temp_nation_dict['applicant_bool'] = True
            else:
                temp_nation_dict['applicant_bool'] = False
        if temp_nation_dict['applicant_bool'] == False or accept_applicants_as_programmees:
            temp_nation_dict_list.append(temp_nation_dict)
        
    return looping, temp_nation_dict_list
                
def given_nation_list_give_cities_with_attached_nation_id(nation_list):
    nation_list_w_cities = {}
    for nation in nation_list:
        if nation['continent'] == 1:
            nationContinent = "North America"
        elif nation['continent'] == 2:
            nationContinent = "South America"
        elif nation['continent'] == 3:
            nationContinent = "Europe"
        elif nation['continent'] == 4:
            nationContinent = "Africa"
        elif nation['continent'] == 5:
            nationContinent = "Asia"
        elif nation['continent'] == 6:
            nationContinent = "Australia"
        elif nation['continent'] == 7:
            nationContinent = "Antarctica"
        nation_cities = returnCityDictionary(nation['nation'], nation['cities'], nationContinent)
        nation_list_w_cities[str(nation['nation_id'])] = nation_cities
    return nation_list_w_cities
    

def get_growth_programees():
    programmees = []
    for taxid in taxid_list:
        looping, loops = True, 0
        while looping:
            looping, new_programmees = scan_nation_search_page(loops, taxid)
            loops += 1
            #print(new_programmees)
            #brick4
            programmees += new_programmees
    return programmees

def calculate_production_per_day (improvCount, improvCap, baseRate):
    bonus = 1 + ((0.5 * (int(improvCount) - 1)) / (int(improvCap) - 1))
    production = (int(improvCount) * bonus * float(baseRate)) * 12
    if production <= 0:
        production = 0
    return production

def getGlobalRads ():
    globalRads = etree.fromstring(requests.get('https://politicsandwar.com/world/radiation/', headers=headers).content, etree.HTMLParser())
    globalRads = float(globalRads.xpath('//*[@id="rightcolumn"]/div[2]/div/h3/text()')[0].replace(',', ''))
    return globalRads

def calculateResourceProduction(cityDict, projectDict, cityCount, resourceCountDict, nationContinent, nationMilitary, nationSeason, nationRadiation, nationAtWar, globalRads, nationPopulation, nationColorBonus):
    cityCounter = 1
    foodRadMultipler = 1 - ((nationRadiation + globalRads)/1000)
    if foodRadMultipler <= 0:
        foodRadMultipler = 0
    if nationSeason == "spring" or nationSeason == "fall" or nationSeason == "autumn":
        foodSeasonMultipler = 1
    elif nationSeason == "summer":
        #foodSeasonMultipler = 1.2 We want average
        foodSeasonMultipler = 1
    elif nationSeason == "winter":
        #foodSeasonMultipler = 0.8 We want average
        foodSeasonMultipler = 1
    elif nationSeason == "Permanent winter":
        foodSeasonMultipler = 0.5 #WARNING, IF SCRIPT NATION IS ANTARCTICA, IT WILL ALWAYS BE PERM WINTER
    else:
        print("SEASON NOT RECOGNIZED")
        print(nationSeason)
    #resourceCountDict = {"coal": 0, "oil": 0, "uranium": 0, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 0, "munitions": 0, "steel": 0, "aluminum": 0, "food": 0}
        
    #"coalPower": 0, "oilPower": 0, "nuclearPower": 0, "coalMines": 0,"oilWells": 0, "bauxiteMines": 0, "ironMines": 0, "leadMines": 0,
    #"uraniumMines": 0, "farms": 0, "oilRefineries": 0, "steelMills": 0, "aluminumRefineries": 0, "munitionsFactories": 0}
    while cityCounter <= cityCount:
        city = cityDict[str(cityCounter)]

        resourceCountDict["money"] += ((((city["commerce"]/50) * 0.725) + 0.725) * city["population"])

        resourceCountDict["money"] -= (city["coalMines"]*400)
        resourceCountDict["money"] -= (city["oilWells"]*600)
        resourceCountDict["money"] -= (city["bauxiteMines"]*1600)
        resourceCountDict["money"] -= (city["ironMines"]*1600)
        resourceCountDict["money"] -= (city["leadMines"]*1500)
        resourceCountDict["money"] -= (city["uraniumMines"]*5000)
        resourceCountDict["money"] -= (city["farms"]*300)

        resourceCountDict["money"] -= (city["coalPower"]*1200)
        resourceCountDict["money"] -= (city["oilPower"]*1800)
        resourceCountDict["money"] -= (city["nuclearPower"]*10500)
        resourceCountDict["money"] -= (city["windPower"]*500)

        resourceCountDict["money"] -= (city["oilRefineries"]*4000)
        resourceCountDict["money"] -= (city["steelMills"]*4000)
        resourceCountDict["money"] -= (city["aluminumRefineries"]*2500)
        resourceCountDict["money"] -= (city["munitionsFactories"]*3500)

        resourceCountDict["money"] -= (city["policeStations"]*750)
        resourceCountDict["money"] -= (city["hospitals"]*1000)
        resourceCountDict["money"] -= (city["recyclingCenters"]*2500)
        resourceCountDict["money"] -= (city["subways"]*3250)
        resourceCountDict["money"] -= (city["supermarkets"]*600)
        resourceCountDict["money"] -= (city["banks"]*1800)
        resourceCountDict["money"] -= (city["shoppingMalls"]*5400)
        resourceCountDict["money"] -= (city["stadiums"]*12150)
        
        resourceCountDict["coal"] += calculate_production_per_day(city["coalMines"], 10, 0.25)
        resourceCountDict["coal"] -= city["coalPower"] * 1.2
        resourceCountDict["oil"] += calculate_production_per_day(city["oilWells"], 10, 0.25)
        resourceCountDict["oil"] -= city["oilPower"] * 1.2
        resourceCountDict["lead"] += calculate_production_per_day(city["leadMines"], 10, 0.25)
        resourceCountDict["iron"] += calculate_production_per_day(city["ironMines"], 10, 0.25)
        resourceCountDict["bauxite"] += calculate_production_per_day(city["bauxiteMines"], 10, 0.25)

        if nationContinent == "Antarctica":
            if projectDict['massirrigation'] >= 1:
                if ((calculate_production_per_day(city["farms"], 20, (float(city['land'])/400)))*0.5*foodRadMultipler) > 0:
                    resourceCountDict["food"] += (calculate_production_per_day(city["farms"], 20, (float(city['land'])/400)))*0.5*foodRadMultipler
            else:
                if ((calculate_production_per_day(city["farms"], 20, (float(city['land'])/500)))*0.5*foodRadMultipler) > 0:
                    resourceCountDict["food"] += (calculate_production_per_day(city["farms"], 20, (float(city['land'])/500)))*0.5*foodRadMultipler
        else:
            if projectDict['massirrigation'] >= 1:
                if (calculate_production_per_day(city["farms"], 20, (float(city['land'])/400))*foodRadMultipler) > 0:
                    resourceCountDict["food"] += calculate_production_per_day(city["farms"], 20, (float(city['land'])/400))*foodRadMultipler#*foodSeasonMultipler
            else:
                if (calculate_production_per_day(city["farms"], 20, (float(city['land'])/500))*foodRadMultipler) > 0:
                    resourceCountDict["food"] += calculate_production_per_day(city["farms"], 20, (float(city['land'])/500))*foodRadMultipler#*foodSeasonMultipler
                
        if projectDict['uraniumenrich'] >= 1:
            resourceCountDict["uranium"] += calculate_production_per_day(city["uraniumMines"], 5, 0.5)
        else:
            resourceCountDict["uranium"] += calculate_production_per_day(city["uraniumMines"], 5, 0.25)
        #if city["powered"] == "Yes":
        cityInfraCounter, nukePower, oilPower, coalPower, windPower = city["infra"], city["nuclearPower"], city["oilPower"], city["coalPower"], city['windPower']
        while cityInfraCounter > 0:
            if windPower > 0:
                cityInfraCounter -= 250
                windPower -= 1
            elif nukePower > 0:
                nuke_infra_batches = cityInfraCounter / 1000
                if nuke_infra_batches > 1:
                    cityInfraCounter -= 2000
                    resourceCountDict["uranium"] -= 2.4
                else:
                    cityInfraCounter -= 1000 #nuke_infra_batches * 
                    resourceCountDict["uranium"] -= 1.2 #nuke_infra_batches * 
                nukePower -= 1
            elif oilPower > 0:
                if cityInfraCounter <= 100:
                    cityInfraCounter -= 100
                    resourceCountDict["oil"] -= 1.2
                    oilPower -= 1
                elif cityInfraCounter > 100 and cityInfraCounter <= 200:
                    cityInfraCounter -= 200
                    resourceCountDict["oil"] -= 2.4
                    oilPower -= 1
                elif cityInfraCounter > 200 and cityInfraCounter <= 300:
                    cityInfraCounter -= 300
                    resourceCountDict["oil"] -= 3.6
                    oilPower -= 1
                elif cityInfraCounter > 300 and cityInfraCounter <= 400:
                    cityInfraCounter -= 400
                    resourceCountDict["oil"] -= 4.8
                    oilPower -= 1
                elif cityInfraCounter > 400:
                    cityInfraCounter -= 500
                    resourceCountDict["oil"] -= 6.0
                    oilPower -= 1
            elif coalPower > 0:
                if cityInfraCounter <= 100:
                    cityInfraCounter -= 100
                    resourceCountDict["coal"] -= 1.2
                    coalPower -= 1
                elif cityInfraCounter > 100 and cityInfraCounter <= 200:
                    cityInfraCounter -= 200
                    resourceCountDict["coal"] -= 2.4
                    coalPower -= 1
                elif cityInfraCounter > 200 and cityInfraCounter <= 300:
                    cityInfraCounter -= 300
                    resourceCountDict["coal"] -= 3.6
                    coalPower -= 1
                elif cityInfraCounter > 300 and cityInfraCounter <= 400:
                    cityInfraCounter -= 400
                    resourceCountDict["coal"] -= 4.8
                    coalPower -= 1
                elif cityInfraCounter > 400:
                    cityInfraCounter -= 500
                    resourceCountDict["coal"] -= 6.0
                    coalPower -= 1
            elif nukePower  + oilPower + coalPower + windPower <= 0:
                cityInfraCounter = 0
        
        
        if projectDict['emgasreserve'] >= 1:
            resourceProductAmount = calculate_production_per_day(city["oilRefineries"], 5, 1)
            resourceCountDict["gasoline"] += resourceProductAmount
            resourceCountDict["oil"] -= resourceProductAmount / 2
        else:
            resourceProductAmount = calculate_production_per_day(city["oilRefineries"], 5, 0.5)
            resourceCountDict["gasoline"] += resourceProductAmount
            resourceCountDict["oil"] -= resourceProductAmount / 2
            
        if projectDict['armsstockpile'] >= 1:
            resourceProductAmount = calculate_production_per_day(city["munitionsFactories"], 5, 2.01)
            resourceCountDict["munitions"] += resourceProductAmount
            resourceCountDict["lead"] -= resourceProductAmount / 3
        else:
            resourceProductAmount = calculate_production_per_day(city["munitionsFactories"], 5, 1.5)
            resourceCountDict["munitions"] += resourceProductAmount
            resourceCountDict["lead"] -= resourceProductAmount / 3
            
        if projectDict['ironworks'] >= 1:
            resourceProductAmount = calculate_production_per_day(city["steelMills"], 5, 1.02)
            resourceCountDict["steel"] += resourceProductAmount
            resourceCountDict["iron"] -= resourceProductAmount / 3
            resourceCountDict["coal"] -= resourceProductAmount / 3
        else:
            resourceProductAmount = calculate_production_per_day(city["steelMills"], 5, 0.75)
            resourceCountDict["steel"] += resourceProductAmount
            resourceCountDict["iron"] -= resourceProductAmount / 3
            resourceCountDict["coal"] -= resourceProductAmount / 3

        if projectDict['bauxiteworks'] >= 1:
            resourceProductAmount = calculate_production_per_day(city["aluminumRefineries"], 5, 1.02)
            resourceCountDict["aluminum"] += resourceProductAmount
            resourceCountDict["bauxite"] -= resourceProductAmount / 3
        else:
            resourceProductAmount = calculate_production_per_day(city["aluminumRefineries"], 5, 0.75)
            resourceCountDict["aluminum"] += resourceProductAmount
            resourceCountDict["bauxite"] -= resourceProductAmount / 3
        
        

        cityCounter += 1
    resourceCountDict["food"] -= (nationPopulation/1000)
    if not nationAtWar:
        resourceCountDict["food"] -= (nationMilitary["soldiers"]/750)

        resourceCountDict["money"] -= (nationMilitary["soldiers"]*1.25)
        resourceCountDict["money"] -= (nationMilitary["tanks"]*50)
        resourceCountDict["money"] -= (nationMilitary["aircraft"]*500)
        resourceCountDict["money"] -= (nationMilitary["ships"]*3750)
        resourceCountDict["money"] -= (nationMilitary["missiles"]*21000)
        resourceCountDict["money"] -= (nationMilitary["nukes"]*35000)
    else:
        resourceCountDict["food"] -= (nationMilitary["soldiers"]/500)

        resourceCountDict["money"] -= (nationMilitary["soldiers"]*1.88)
        resourceCountDict["money"] -= (nationMilitary["tanks"]*75)
        resourceCountDict["money"] -= (nationMilitary["aircraft"]*750)
        resourceCountDict["money"] -= (nationMilitary["ships"]*5625)
        resourceCountDict["money"] -= (nationMilitary["missiles"]*31500)
        resourceCountDict["money"] -= (nationMilitary["nukes"]*52500)
    resourceCountDict["money"] -= (nationMilitary["spies"]*2400)
    resourceCountDict["money"] += (nationColorBonus * 12)
    return resourceCountDict

def get_nationColorBonuses():
    colorBonusTable = etree.fromstring(requests.get('https://politicsandwar.com/leaderboards/display=color', headers=headers).content, etree.HTMLParser())
    nationColorBonuses = {}
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[2]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[2]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[3]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[3]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[4]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[4]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[5]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[5]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[6]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[6]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[7]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[7]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[8]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[8]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[9]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[9]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[10]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[10]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[11]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[11]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[12]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[12]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[13]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[13]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[14]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[14]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[15]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[15]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[16]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[16]/td[6]/text()')[0].replace(',', '').replace('$', ''))
    nationColorBonuses[colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[17]/td[1]/img/@title')[0].lower()] = float(colorBonusTable.xpath('//*[@id="rightcolumn"]/table/tr[17]/td[6]/text()')[0].replace(',', '').replace('$', ''))
        
    return nationColorBonuses

def login(email, password):
    #given email and password, login to pnw website and return session s
    #print("\nLogging in...")
    with requests.Session() as s:
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        login_payload = {'email':email, 'password':password, 'loginform':'Login'}
        url = 'https://politicsandwar.com/login/'
        s.post(url, data=login_payload)
        #print("Logged in.\n")

        return s

def collect_warchest_data(session):
    nations_tree = etree.fromstring(session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=acp', headers=headers).content, etree.HTMLParser())
    nation_rows_on_page = nations_tree.xpath('//*[@id="scrollme"]/table/tr[*]')[1:]
    
    warchest_info_dict = {}
    
    for row in nation_rows_on_page:
        nation_id = str(row.xpath('./td[1]/a/@href')[0][37:])
        warchest_dict = {}
        
        try:
            warchest_dict['money'] = int(row.xpath('./td[4]/text()[1]')[0].replace(' ', '').replace('$', '').replace(',', '').replace('\n', ''))
        except:
            print(str(nation_id) + " DOES NOT HAVE ALLIANCE ACCESS ENABLED")
            continue

        warchest_dict['money'] = int(row.xpath('./td[4]/text()[1]')[0].replace(' ', '').replace(',', '').replace('$', '').replace('\n', ''))
        warchest_dict['steel'] = int(row.xpath('./td[5]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['aluminum'] = int(row.xpath('./td[6]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['gasoline'] = int(row.xpath('./td[7]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['munitions'] = int(row.xpath('./td[8]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['uranium'] = int(row.xpath('./td[9]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['food'] = int(row.xpath('./td[10]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        warchest_dict['spies'] = int(row.xpath('./td[15]/text()[1]')[0].replace(' ', '').replace(',', '').replace('\n', ''))
        
        warchest_info_dict[str(nation_id)] = warchest_dict

    print(warchest_info_dict)
        

#'money': '43600224.42', 'food': '148588.54', 'coal': '20.09', 'oil': '16989.97', 'uranium': '17948.15', 'bauxite': '9854.29', 'iron': '10810.96', 'lead': '10141.63', 'gasoline': '17992.33', 'munitions': '100.94', 'aluminum': '19254.63', 'steel': '46341.44', 'credits': '3', 'soldiers': '0', 'tanks': '0', 'aircraft': '3078', 'ships': '0', 'missiles': '1', 'nukes': '0', 'spies': '60'}

def getNationsInfo(nationID, alliance_members_api_call):
    nationMilitary = {}
    for nationData in alliance_members_api_call:
        if int(nationData['nationid']) == int(nationID):
            projectDict = {"ironworks": int(nationData['ironworks']), "bauxiteworks": int(nationData['bauxiteworks']), "armsstockpile": int(nationData['armsstockpile']), "emgasreserve": int(nationData['emgasreserve']), "massirrigation": int(nationData['massirrigation']), "uraniumenrich": int(nationData['uraniumenrich']), "inttradecenter": int(nationData['inttradecenter'])}
            nationMilitary['soldiers'] = int(nationData['soldiers'])
            nationMilitary['tanks'] = int(nationData['tanks'])
            nationMilitary['aircraft'] = int(nationData['aircraft'])
            nationMilitary['ships'] = int(nationData['ships'])
            nationMilitary['missiles'] = int(nationData['missiles'])
            nationMilitary['nukes'] = int(nationData['nukes'])
            nationMilitary['spies'] = int(nationData['spies'])
            
            war_policy = str(nationData['war_policy'])

            current_resources_dict = {"money" : nationData['money'], "coal": nationData['coal'], "oil": nationData['oil'], "uranium": nationData['uranium'], "lead": nationData['lead'], "iron": nationData['iron'], "bauxite": nationData['bauxite'], "gasoline": nationData['gasoline'], "munitions": nationData['munitions'], "steel": nationData['steel'], "aluminum": nationData['aluminum'], "food": nationData['food']}
            ##nationContinent = str(nationData['continent']) #moved to pseudo dict
            #nationSeason = str(nationData['season']) #moved to global in main
            #nationRadiation = float(nationData['radiation_index']) scraped
            #nationPopulation = int(nationData['population']) scraped
            if int(nationData['offensivewars']) > 0 or int(nationData['defensivewars']) > 0:
                nationAtWar = True
            else:
                nationAtWar = False
            nationColor = nationData['color']


            nation_id = nationID
            nation_frontpage_tree = (etree.fromstring(requests.post('https://politicsandwar.com/nation/id=' + str(nation_id), headers = headers).content, etree.HTMLParser()))
            try:
                if nation_frontpage_tree.xpath('//*[@id="rightcolumn"]/div[1]/text()')[0][:44] == 'This nation is in Vacation Mode for the next':
                    return
                else:
                    pass
            except:
                pass
            try:
                if nation_frontpage_tree.xpath('//*[@id="rightcolumn"]/p/text()[1]')[0] == "This nation does not exist. It was either deleted for inactivity, or the player controlling the nation deleted their account. Visit ":
                    return
                else:
                    pass

            except:
                pass
            divs = nation_frontpage_tree.xpath('//*[@id="rightcolumn"]/div[*]')[0:]
            div_num = 0
            for div in divs:
                try:
                    if div.xpath('./div[1]/table/tr[2]/td[1]/text()')[0] == 'Nation Name:':
                       row_div_num = div_num
                       rows = div.xpath('./div[1]/table/tr[*]')[1:]
                except:
                    pass
                try:
                    if div.xpath('./div[2]/table/tr[3]/th/text()')[0][-8:] == ' Cities ':
                       city_div_num = div_num
                       city_div = div
                except:
                    pass
                div_num += 1
            
            try:
                for row in rows:
                    try:
                        if row.xpath('./td[1]/text()')[0].replace(' ', '') == 'Population:':
                            nationPopulation = int(row.xpath('./td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
                        elif row.xpath('./td[1]/text()')[0].replace(' ', '') == 'RadiationIndex:':
                            nationRadiation = row.xpath('./td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '')
                            nationRadiation = float(nationRadiation[:nationRadiation.find(' R (')])
                    except:
                        continue
            except Exception as ex:
                print("ROWS FAIL:" + str(nation_id))
                print(datetime.utcnow().time())
                print(ex)
                return
    try:
        return projectDict, nationMilitary, nationRadiation, nationAtWar, nationPopulation, nationColor, current_resources_dict, war_policy
    except:
        print(nationID)
        print(projectDict)
        BRICK

def get_season():
    session = login(user_email, user_password)

    nations_tree = etree.fromstring(session.get('https://politicsandwar.com/', headers=headers).content, etree.HTMLParser())
    season = nations_tree.xpath('//*[@id="leftcolumn"]/div/img/@title')[0]
    season = str(season[:season.find(':')]).replace('S', 's').replace('W', 'w').replace('A', 'a')

    return season
        
def send_resources(programees_and_their_netrevs, programees_and_their_current_resources, alliance_bank_contents, session, allianceNationsDict, programees_and_their_city_counts, programees_and_their_warstatus):
    global_needed_resources_dict = {"money" : 0, "coal": 0, "oil": 0, "uranium": 0, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 0, "munitions": 0, "steel": 0, "aluminum": 0, "food": 0}
    needed_resources_dict_dict = {}
    
    for nation_id, net_rev in programees_and_their_netrevs.items():
        needed_resources_dict = {"money" : 0, "coal": 0, "oil": 0, "uranium": 0, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 0, "munitions": 0, "steel": 0, "aluminum": 0, "food": 0}
        current_res = programees_and_their_current_resources[str(nation_id)]

        #Upkeep settings
        not_trader = True #override, True = current resources calculated, False = Flat sum
        for trader_id in trader_id_list:
            if int(trader_id) == int(nation_id):
                not_trader = False
        
        for resource, amount in net_rev.items():
            if top_off_mode:
                if amount < 0 and not_trader:
                    if programees_and_their_warstatus[str(nation_id)] == False: #food_and_uranium_multipler
                        if float(abs(amount*send_resource_multipler)) > float(current_res[str(resource)]) and ((str(resource) != 'food' and str(resource) != 'uranium') or not send_food_and_uranium_buffer):
                            needed_resources_dict[str(resource)] = (float(abs(amount*send_resource_multipler)) - float(current_res[str(resource)]))
                            #global_needed_resources_dict[str(resource)] = float(global_needed_resources_dict[str(resource)]) + ((abs(amount*5)) - float(current_res[str(resource)]))
                        elif (abs(amount*send_resource_multipler*food_and_uranium_multipler)) > float(current_res[str(resource)]) and (str(resource) == 'food' or str(resource) == 'uranium') and send_food_and_uranium_buffer:
                            needed_resources_dict[str(resource)] = (float(abs(amount*send_resource_multipler*food_and_uranium_multipler)) - float(current_res[str(resource)]))
                    elif programees_and_their_warstatus[str(nation_id)] == True:
                        if float(abs(amount*send_resource_multipler)) > float(current_res[str(resource)]):
                            needed_resources_dict[str(resource)] = float((abs(amount*send_resource_multipler)) - float(current_res[str(resource)]))
                            #global_needed_resources_dict[str(resource)] = float(global_needed_resources_dict[str(resource)]) + ((abs(amount*1)) - float(current_res[str(resource)]))
                    else:
                        print(str(nation_id) + " WAR STATUS FIND FAIL")
                elif not_trader == False and amount < 0 and programees_and_their_warstatus[str(nation_id)] == False: # and current_weekday == 0
                    needed_resources_dict[str(resource)] = abs(amount*send_resource_multipler)#7.09 for a week and a turn, 8.09 for an extra day
                elif not_trader == False and amount < 0 and programees_and_their_warstatus[str(nation_id)] == True: # and current_weekday != 0
                    if (abs(amount*send_resource_multipler)) > float(current_res[str(resource)]):
                        needed_resources_dict[str(resource)] = (float(abs(amount*send_resource_multipler)) - float(current_res[str(resource)]))
            else:
                if amount < 0:
                    if (str(resource) != 'food' and str(resource) != 'uranium') or not send_food_and_uranium_buffer:
                        needed_resources_dict[str(resource)] = abs(amount*send_resource_multipler)
                    elif (str(resource) == 'food' or str(resource) == 'uranium') and send_food_and_uranium_buffer:
                        if abs(amount*send_resource_multipler) >= (float(abs(amount*send_resource_multipler*food_and_uranium_multipler)) - float(current_res[str(resource)])):
                            needed_resources_dict[str(resource)] = abs(amount*send_resource_multipler)
                        else:
                             needed_resources_dict[str(resource)] = (float(abs(amount*send_resource_multipler*food_and_uranium_multipler)) - float(current_res[str(resource)]))

        #On hand WC settings
        city_count = programees_and_their_city_counts[str(nation_id)]
        
        if send_wc:
            if city_count < 20:
                if WAR_maint_wc:
                    if needed_resources_dict['money'] < 0:
                        needed_resources_dict['money'] = 0
                    if float(current_res['food']) < city_count * 3000:
                        needed_resources_dict['food'] += (city_count * 3000) - float(current_res['food'])
                    if float(current_res['uranium']) < city_count * 50:
                        needed_resources_dict['uranium'] += (city_count * 50) - float(current_res['uranium'])
                    if float(current_res['aluminum']) < city_count * 400:
                        needed_resources_dict['aluminum'] += (city_count * 400) - float(current_res['aluminum'])
                        #global_needed_resources_dict['aluminum'] += (city_count * 75 * 2) - float(current_res['aluminum'])
                    if float(current_res['steel']) < city_count * 750:
                        needed_resources_dict['steel'] += (city_count * 750) - float(current_res['steel'])
                        #global_needed_resources_dict['aluminum'] += (city_count * 75 * 2) - float(current_res['aluminum'])
                    if float(current_res['munitions']) < city_count * 650:#should be 900
                        needed_resources_dict['munitions'] += (city_count * 650) - float(current_res['munitions'])#should be 900
                        #global_needed_resources_dict['munitions'] += (city_count * 22.5 * 7) - float(current_res['munitions']) 
                    if float(current_res['gasoline']) < city_count * 625:
                        needed_resources_dict['gasoline'] += (city_count * 625) - float(current_res['gasoline'])
                    if float(current_res['money']) < city_count * 500000 * wc_money_mult:
                        needed_resources_dict['money'] += (city_count * 500000 * wc_money_mult) - float(current_res['money'])
                        
                elif PEACE_maint_WC:
                    if needed_resources_dict['money'] < 0:
                        needed_resources_dict['money'] = 0
                    if float(current_res['food']) < city_count * 1500:
                        needed_resources_dict['food'] += (city_count * 1500) - float(current_res['food'])
                    if float(current_res['uranium']) < city_count * 25:
                        needed_resources_dict['uranium'] += (city_count * 25) - float(current_res['uranium'])
                    if float(current_res['aluminum']) < city_count * 200:
                        needed_resources_dict['aluminum'] += (city_count * 200) - float(current_res['aluminum'])
                        #global_needed_resources_dict['aluminum'] += (city_count * 75 * 2) - float(current_res['aluminum'])
                    if float(current_res['steel']) < city_count * 375:
                        needed_resources_dict['steel'] += (city_count * 375) - float(current_res['steel'])
                        #global_needed_resources_dict['aluminum'] += (city_count * 75 * 2) - float(current_res['aluminum'])
                    if float(current_res['munitions']) < city_count * 325:#should be 900
                        needed_resources_dict['munitions'] += (city_count * 325) - float(current_res['munitions'])#should be 900
                        #global_needed_resources_dict['munitions'] += (city_count * 22.5 * 7) - float(current_res['munitions']) 
                    if float(current_res['gasoline']) < city_count * 313:
                        needed_resources_dict['gasoline'] += (city_count * 313) - float(current_res['gasoline'])
                    if float(current_res['money']) < city_count * 250000 * wc_money_mult:
                        needed_resources_dict['money'] += (city_count * 250000 * wc_money_mult) - float(current_res['money'])
                        

            else:
                if WAR_maint_wc:
                    if needed_resources_dict['money'] < 0:
                        needed_resources_dict['money'] = 0
                    if float(current_res['food']) < city_count * 3000:
                        needed_resources_dict['food'] += (city_count * 3000) - float(current_res['food'])
                    if float(current_res['uranium']) < city_count * 100:
                        needed_resources_dict['uranium'] += (city_count * 100) - float(current_res['uranium'])
                    if float(current_res['aluminum']) < city_count * 500:
                        needed_resources_dict['aluminum'] += (city_count * 500) - float(current_res['aluminum'])
                    if float(current_res['steel']) < city_count * 750:
                        needed_resources_dict['steel'] += (city_count * 750) - float(current_res['steel'])
                    if float(current_res['munitions']) < city_count * 700:#should be 900
                        needed_resources_dict['munitions'] += (city_count * 700) - float(current_res['munitions'])#should be 900
                    if float(current_res['gasoline']) < city_count * 675:
                        needed_resources_dict['gasoline'] += (city_count * 675) - float(current_res['gasoline'])
                    if float(current_res['money']) < city_count * 750000 * wc_money_mult:
                        needed_resources_dict['money'] += (city_count * 750000 * wc_money_mult) - float(current_res['money'])
                        
                elif PEACE_maint_WC:
                    if needed_resources_dict['money'] < 0:
                        needed_resources_dict['money'] = 0
                    if float(current_res['food']) < city_count * 1500:
                        needed_resources_dict['food'] += (city_count * 1500) - float(current_res['food'])
                    if float(current_res['uranium']) < city_count * 50:
                        needed_resources_dict['uranium'] += (city_count * 50) - float(current_res['uranium'])
                    if float(current_res['aluminum']) < city_count * 250:
                        needed_resources_dict['aluminum'] += (city_count * 250) - float(current_res['aluminum'])
                    if float(current_res['steel']) < city_count * 375:
                        needed_resources_dict['steel'] += (city_count * 375) - float(current_res['steel'])
                    if float(current_res['munitions']) < city_count * 350:#should be 900
                        needed_resources_dict['munitions'] += (city_count * 350) - float(current_res['munitions'])#should be 900
                    if float(current_res['gasoline']) < city_count * 338:
                        needed_resources_dict['gasoline'] += (city_count * 338) - float(current_res['gasoline'])
                    if float(current_res['money']) < city_count * 300000 * wc_money_mult:
                        needed_resources_dict['money'] += (city_count * 300000 * wc_money_mult) - float(current_res['money'])
            
                    
        needed_resources_dict_dict[str(nation_id)] = needed_resources_dict
    
    for nation_id, needed_res in needed_resources_dict_dict.items():
        for resource, amount in needed_res.items():
            needed_res[resource] = math.ceil(float(amount))

    for nation_id, needed_res in needed_resources_dict_dict.items():
        for resource, amount in needed_res.items():
            global_needed_resources_dict[resource] += needed_res[resource]
            

    print("\nRESOURCES TO BE SENT TO EACH NATION")
    print(needed_resources_dict_dict)
    print("\nTOTAL RESOURCES TO BE SENT: ")
    print(global_needed_resources_dict)
    #print(needed_resources_dict_dict)

    print("\nLOW ON/LOW BY: ")
    low_resources = []
    for resource, amount in alliance_bank_contents.items():
        if float(global_needed_resources_dict[str(resource)]) > float(amount):
            print(str(math.ceil(float(global_needed_resources_dict[str(resource)])-float(amount))) + ' ' + str(resource))
            low_resources.append(str(resource))
            
    if dump_to_offshore_global:
        dump_to_offshore = True
    else:
        dump_to_offshore = False


    if len(low_resources) > 0:
        if brick_resources_low:
            BRICK
        dump_to_offshore = False
        for nation_id, needed_res in needed_resources_dict_dict.items():
            for resource, amount in needed_res.items():
                for sub_resource in low_resources:
                    if sub_resource == resource:
                        needed_res[str(resource)] = float(amount / global_needed_resources_dict[str(resource)] * alliance_bank_contents[str(resource)])
                if amount < 0.01:
                    needed_res[str(resource)] = 0

    for nation_id, needed_res in needed_resources_dict_dict.items():
        for resource, amount in needed_res.items():
            if amount < 0.01:
                needed_res[str(resource)] = 0
            else:
                needed_res[str(resource)] = math.ceil(float(needed_res[str(resource)]))

    print(needed_resources_dict_dict)

    for nation_id, needed_res in needed_resources_dict_dict.items():
        send = False
        for resource, amount in needed_res.items():
            if amount > 0:
                send = True
                break
        if send == True:
            for psuedo_nation in allianceNationsDict:
                if int(nation_id) == int(psuedo_nation['nation_id']):
                    nation_name = psuedo_nation['nation_name']
            if brick_the_send:
                BRICKSEND
                
            session = send_given_resources_to_given_nation_id(session, needed_res, nation_name)

    if dump_to_offshore: 
        alliance_bank_contents = {}
        alliance_bank_page = etree.fromstring(session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank', headers=headers).content, etree.HTMLParser())
        looking_for_div_index = True
        current_div_index = 0
        
        while looking_for_div_index:
            try:
                if alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[1]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', '').replace(' ', '') == 'Money':
                    looking_for_div_index = False
                else:
                    current_div_index += 1
            except:
                current_div_index += 1
        
        alliance_bank_contents['money'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', ''))
        alliance_bank_contents['food'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[3]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['coal'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[4]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['oil'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[5]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['uranium'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[6]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['lead'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[7]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['iron'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[8]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['bauxite'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[9]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['gasoline'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[10]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['munitions'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[11]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['steel'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[12]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        alliance_bank_contents['aluminum'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[13]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
        send_given_resources_to_given_alliance_name(session, alliance_bank_contents, offshore_name)
        
def send_given_resources_to_given_nation_id(session, needed_res, nation_name):
    #given leader name, send them recruitment message
    #print(nation_name)
    #print(needed_res)
    r = session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank')
    soup = BeautifulSoup(r.content, 'html.parser')
    token = soup.find('input', {'name':'token'})['value']
    
    send_message_payload = {'withmoney':needed_res['money'],
                            'withfood':needed_res['food'],
                            'withcoal':needed_res['coal'],
                            'withoil':needed_res['oil'],
                            'withuranium':needed_res['uranium'],
                            'withlead':needed_res['lead'],
                            'withiron':needed_res['iron'],
                            'withbauxite':needed_res['bauxite'],
                            'withgasoline':needed_res['gasoline'],
                            'withmunitions':needed_res['munitions'],
                            'withsteel':needed_res['steel'],
                            'withaluminum':needed_res['aluminum'],
                            "withtype": "Nation",
                            "withrecipient": nation_name,
                            "withnote": "Covid relief funds",
                            "withsubmit": "Withdraw",
                            "token": token}
    print(send_message_payload)
    send_message_url = 'https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank'
    res = session.post(send_message_url, data=send_message_payload)
    #print(res.text)
    #res = s.get('https://politicsandwar.com/nation/revenue/')
    #print(res.text)

    return session

def send_given_resources_to_given_alliance_name(session, needed_res, alliance_name):
    #given leader name, send them recruitment message
    #print(nation_name)
    #print(needed_res)
    r = session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank')
    soup = BeautifulSoup(r.content, 'html.parser')
    token = soup.find('input', {'name':'token'})['value']
    
    send_message_payload = {'withmoney':needed_res['money'],
                            'withfood':needed_res['food'],
                            'withcoal':needed_res['coal'],
                            'withoil':needed_res['oil'],
                            'withuranium':needed_res['uranium'],
                            'withlead':needed_res['lead'],
                            'withiron':needed_res['iron'],
                            'withbauxite':needed_res['bauxite'],
                            'withgasoline':needed_res['gasoline'],
                            'withmunitions':needed_res['munitions'],
                            'withsteel':needed_res['steel'],
                            'withaluminum':needed_res['aluminum'],
                            "withtype": "Alliance",
                            "withrecipient": alliance_name,
                            "withnote": "Dump to offshore",
                            "withsubmit": "Withdraw",
                            "token": token}
    print(send_message_payload)
    send_message_url = 'https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank'
    res = session.post(send_message_url, data=send_message_payload)
    #print(res.text)
    #res = s.get('https://politicsandwar.com/nation/revenue/')
    #print(res.text)

    return session
    
def audit_nation(cityDict, nationID, war_policy, cityCount, current_resources_dict, nationMilitary, projectDict):
    nation_link = 'https://politicsandwar.com/nation/id=' + str(nationID)
    nation_flags_dict = {'nation_link' : nation_link, 'city_count' : 0, 'needs_food' : 0, 'cities_unpowered' : 0, 'needs_more_commerce' : 0, 'needs_less_commerce' : 0, 'incorrect_commerce_itc' : 0, 'incorrect_crime' : 0, 'incorrect_mil_improvs' : 0, 'unmaxed_air' : 0, 'needs_recycling_center' : 0, 'needs_subway' : 0, 'needs_hospital' : 0, 'refining_without_project' : 0, 'unused_slots' : 0, 'wrong_war_policy' : 0, 'incorrect_disease' : 0, 'manu_incorrect' : 0, 'raws_incorrect' : 0, 'farming_with_low_land' : 0, 'odd_infra' : 0, 'odd_land' : 0, 'infra_too_high' : 0, 'using_oilcoal_power' : 0, 'too_much_wind': 0}
    
    if int(nationMilitary['aircraft']) < (int(cityCount) * 75):
        nation_flags_dict['unmaxed_air'] = 1
        
    if war_policy != 'Fortress':
        nation_flags_dict['wrong_war_policy'] = 1
        
    if current_resources_dict['food'] == 0:
        nation_flags_dict['needs_food'] = 1
        
    nation_flags_dict['city_count'] = cityCount
    
    for cityNum, city in cityDict.items():
        used_improv_count = int(city["coalPower"]) + int(city["oilPower"]) + int(city["nuclearPower"]) + int(city["windPower"]) + int(city["coalMines"]) + int(city["oilWells"]) + int(city["bauxiteMines"]) + int(city["ironMines"]) + int(city["leadMines"]) + int(city["uraniumMines"]) + int(city["farms"]) + int(city["oilRefineries"]) + int(city["steelMills"]) + int(city["aluminumRefineries"]) + int(city["munitionsFactories"]) + int(city["policeStations"]) + int(city["hospitals"]) + int(city["recyclingCenters"]) + int(city["subways"]) + int(city["supermarkets"]) + int(city["banks"]) + int(city["shoppingMalls"]) + int(city["stadiums"]) + int(city["barracks"]) + int(city["factories"]) + int(city["hangars"]) + int(city["drydocks"])
        max_improv_count = int(city["infra"]/50)

        if used_improv_count < max_improv_count:
            nation_flags_dict['unused_slots'] = 1
            
        if city["powered"] == 'No':
            nation_flags_dict['cities_unpowered'] = 1
        if city["infra"] >= 1500 and city["commerce"] < 100 and projectDict['inttradecenter'] <= 0:
            nation_flags_dict['needs_more_commerce'] = 1
        if city["infra"] >= 1500 and city["commerce"] < 114 and projectDict['inttradecenter'] >= 1:
            nation_flags_dict['incorrect_commerce_itc'] = 1
        if city["infra"] >= 1500 and city["crime"] > 0.05:
            nation_flags_dict['incorrect_crime'] = 1
        if cityCount >= 10:
            if city["barracks"] > 0 or city["factories"] > 3 or city["drydocks"] > 0 or city["hangars"] < 4:
                nation_flags_dict['incorrect_mil_improvs'] = 1
        if city["infra"] < 1000 and city["commerce"] > 0:
            nation_flags_dict['needs_less_commerce'] = 1
            
        if city['disease'] > 0.02:
            nation_flags_dict['incorrect_disease'] = 1
            
        if city["infra"] >= 1500 and city["pollution"] >= 70 and city['recyclingCenters'] < 3 and city['disease'] >= 3.5:
            nation_flags_dict['needs_recycling_center'] = 1
        if city["infra"] >= 1500 and city["pollution"] >= 45 and city['subways'] < 1 and city['disease'] >= 2.25:
            nation_flags_dict['needs_subway'] = 1
        if city["infra"] >= 1500 and city['disease'] >= 2.5 and city["hospitals"] < 5:
            nation_flags_dict['needs_hospital'] = 1
            
        if city["oilRefineries"] > 0 and projectDict['emgasreserve'] <= 0:
            nation_flags_dict['refining_without_project'] = 1
        if city["steelMills"] > 0 and projectDict['ironworks'] <= 0:
            nation_flags_dict['refining_without_project'] = 1
        if city["aluminumRefineries"] > 0 and projectDict['bauxiteworks'] <= 0:
            nation_flags_dict['refining_without_project'] = 1
        if city["munitionsFactories"] > 0 and projectDict['armsstockpile'] <= 0:
            nation_flags_dict['refining_without_project'] = 1
            
        if int(city["oilRefineries"]) > 0 and int(city["oilRefineries"]) < 5:
            nation_flags_dict['manu_incorrect'] = 1
        elif int(city["steelMills"]) > 0 and int(city["steelMills"]) < 5:
            nation_flags_dict['manu_incorrect'] = 1
        elif int(city["aluminumRefineries"]) > 0 and int(city["aluminumRefineries"]) < 5:
            nation_flags_dict['manu_incorrect'] = 1
        elif int(city["munitionsFactories"]) > 0 and int(city["munitionsFactories"]) < 5:
            nation_flags_dict['manu_incorrect'] = 1
            
        if int(city["coalMines"]) > 0 and int(city["coalMines"]) < 10:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["oilWells"]) > 0 and int(city["oilWells"]) < 10:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["bauxiteMines"]) > 0 and int(city["bauxiteMines"]) < 10:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["ironMines"]) > 0 and int(city["ironMines"]) < 10:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["leadMines"]) > 0 and int(city["leadMines"]) < 10:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["uraniumMines"]) > 0 and int(city["uraniumMines"]) < 5:
            nation_flags_dict['raws_incorrect'] = 1
        elif int(city["farms"]) > 0 and int(city["farms"]) < 20:
            nation_flags_dict['raws_incorrect'] = 1
            
        if int(city["farms"]) > 0 and int(city["land"]) < 3000:
            nation_flags_dict['farming_with_low_land'] = 1
            
        if int(city['infra']) % 50 != 0:
            nation_flags_dict['odd_infra'] = 1
            
        if int(city['land']) % 100 != 0:
            nation_flags_dict['odd_land'] = 1
            
        if int(city['coalPower']) > 0 or int(city['oilPower']) > 0:
            nation_flags_dict['using_oilcoal_power'] = 1
            
        if int(city['windPower']) > 1:
            nation_flags_dict['too_much_wind'] = 1
            
        if cityCount < 10:
            if int(city['infra']) > 1500:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 10 and cityCount < 16:
            if int(city['infra']) > 2000:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 16 and cityCount < 20:
            if int(city['infra']) > 2250:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 20 and cityCount < 26:
            if int(city['infra']) > 2500:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 26 and cityCount < 30:
            if int(city['infra']) > 2700:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 30 and cityCount < 35:
            if int(city['infra']) > 3000:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 35 and cityCount < 40:
            if int(city['infra']) > 3300:
                nation_flags_dict['infra_too_high'] = 1
        elif cityCount >= 40:
            if int(city['infra']) > 3600:
                nation_flags_dict['infra_too_high'] = 1
                
    return nation_flags_dict

def main():
    print("Omnibus felicitatem.")
    start_time = time.time()
    print("EXECUTING\n")

    
    section_start_time = time.time()
    
    print("\nGetting global rads...")
    globalRads = getGlobalRads()
    print("Global radiation is currently: " + str(globalRads))
    print(str(time.time() - section_start_time) + " seconds elapsed")

    section_start_time = time.time()
    print("\nGetting nation color bonuses...")
    nationColorBonuses = get_nationColorBonuses()
    print(nationColorBonuses)
    print(str(time.time() - section_start_time) + " seconds elapsed")
    

    allianceNationsDict = get_growth_programees()
    
    for allianceid in allianceid_list:
        with urllib.request.urlopen('https://politicsandwar.com/api/v2/nations/' + str(allianceid_apikey_dict[allianceid]) + '/&alliance_id=' + str(allianceid)) as url:
            if 'nations_alliance_api_call' in locals():
                nations_alliance_api_call = nations_alliance_api_call + json.loads(url.read().decode())['data']
            else:
                nations_alliance_api_call = json.loads(url.read().decode())['data']
                
    allianceNationsDict_buffer = allianceNationsDict[:]
    total_cities = 0
    for nation in nations_alliance_api_call:
        for psuedo_nation in allianceNationsDict:
            for alliance_id in allianceid_list:
                if int(nation['alliance_id']) == int(alliance_id):
                    if int(nation['nation_id']) == int(psuedo_nation['nation_id']):
                        if nation['v_mode'] == True:
                            allianceNationsDict_buffer.remove(psuedo_nation)
                            #if nation['v_mode'] == True or str(psuedo_nation['nation_color']) == "beige" or str(psuedo_nation['nation_color']) == "gray" or str(psuedo_nation['nation_color']) == "Gray" or str(psuedo_nation['nation_color']) == "Beige":
                        elif nation['continent'] == 1:
                            psuedo_nation['nation_continent'] = "North America"
                        elif nation['continent'] == 2:
                            psuedo_nation['nation_continent'] = "South America"
                        elif nation['continent'] == 3:
                            psuedo_nation['nation_continent'] = "Europe"
                        elif nation['continent'] == 4:
                            psuedo_nation['nation_continent'] = "Africa"
                        elif nation['continent'] == 5:
                            psuedo_nation['nation_continent'] = "Asia"
                        elif nation['continent'] == 6:
                            psuedo_nation['nation_continent'] = "Australia"
                        elif nation['continent'] == 7:
                            psuedo_nation['nation_continent'] = "Antarctica"
                        total_cities += int(psuedo_nation['nation_city_count'])
                        break
    print("\n")
    print("PROGRAMEES")
    print(allianceNationsDict)
    allianceNationsDict = allianceNationsDict_buffer

    section_start_time = time.time()
    print("\nCollecting city data and calculating resource production...")

    programees_and_their_netrevs = {}
    programees_and_their_current_resources = {}
    programees_and_their_city_counts = {}
    programees_and_their_warstatus = {}

    nationSeason = get_season()
    for allianceid_apikey_pair_dict in allianceid_apikey_pair_dict_list:
        with urllib.request.urlopen('https://politicsandwar.com/api/alliance-members/?allianceid=' + str(allianceid_apikey_pair_dict['alliance_id']) + '&key=' + str(allianceid_apikey_pair_dict['key'])) as url:
            if 'alliance_members_api_call' in locals():
                alliance_members_api_call = alliance_members_api_call + json.loads(url.read().decode())['nations']
            else:
                alliance_members_api_call = json.loads(url.read().decode())['nations']
    if run_audit:
        print('WILL AUDIT')
        audit_result_list = []
    for psuedo_nation in allianceNationsDict:
        resourceCountDict = {"money" : 0, "coal": 0, "oil": 0, "uranium": 0, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 0, "munitions": 0, "steel": 0, "aluminum": 0, "food": 0}
        nationID = psuedo_nation['nation_id']
        nationName = psuedo_nation['nation_name']
        nationContinent = psuedo_nation['nation_continent']
        leader_name = psuedo_nation['leader_name']
        city_manager_tree = etree.fromstring(requests.get('https://politicsandwar.com/index.php?id=62&l=' + str(leader_name), headers=headers).content, etree.HTMLParser())
        projectDict, nationMilitary, nationRadiation, nationAtWar, nationPopulation, nationColor, current_resources_dict, war_policy = getNationsInfo(nationID, alliance_members_api_call)
        cityCount = len(city_manager_tree.xpath('//*[@id="rightcolumn"]/div[3]/table/tr[1]/th[*]'))
        cityDict = returnCityDictionary(city_manager_tree, cityCount, nationContinent)
        resourceCountDict = calculateResourceProduction(cityDict, projectDict, cityCount, resourceCountDict, nationContinent, nationMilitary, nationSeason, nationRadiation, nationAtWar, globalRads, nationPopulation, nationColorBonuses[nationColor])
        programees_and_their_netrevs[str(nationID)] = resourceCountDict
        programees_and_their_current_resources[str(nationID)] = current_resources_dict
        programees_and_their_city_counts[str(nationID)] = int(cityCount)
        programees_and_their_warstatus[str(nationID)] = nationAtWar
        
        if run_audit:
            result_dict = audit_nation(cityDict, nationID, war_policy, cityCount, current_resources_dict, nationMilitary, projectDict)
            audit_result_list.append(result_dict)
    if run_audit:
        print('AUDIT RESULTS:')
        print(audit_result_list)
        print("\n")
    print(str(time.time() - section_start_time) + " seconds elapsed")

    session = login(user_email, user_password)

    alliance_bank_contents = {}
    alliance_bank_page = etree.fromstring(session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank', headers=headers).content, etree.HTMLParser())
    
    looking_for_div_index = True
    current_div_index = 0
    
    while looking_for_div_index:
        try:
            if alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[1]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', '').replace(' ', '') == 'Money':
                looking_for_div_index = False
            else:
                current_div_index += 1
        except:
            current_div_index += 1
    
    alliance_bank_contents['money'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', ''))
    alliance_bank_contents['food'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[3]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['coal'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[4]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['oil'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[5]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['uranium'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[6]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['lead'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[7]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['iron'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[8]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['bauxite'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[9]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['gasoline'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[10]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['munitions'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[11]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['steel'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[12]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['aluminum'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[13]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))

    try:
        pickle.dump(programees_and_their_netrevs, open( "programees_and_their_netrevs.p", "wb" ))
        pickle.dump(programees_and_their_current_resources, open( "programees_and_their_current_resources.p", "wb" ))
        pickle.dump(alliance_bank_contents, open( "alliance_bank_contents.p", "wb" ))
        pickle.dump(allianceNationsDict, open( "allianceNationsDict.p", "wb" ))
        pickle.dump(programees_and_their_city_counts, open( "programees_and_their_city_counts.p", "wb" ))
        pickle.dump(programees_and_their_warstatus, open( "programees_and_their_warstatus.p", "wb" ))
    except:
        programees_and_their_netrevs = pickle.load( open( "programees_and_their_netrevs.p", "rb" ))
        programees_and_their_current_resources = pickle.load( open( "programees_and_their_current_resources.p", "rb" ))
        alliance_bank_contents = pickle.load( open( "alliance_bank_contents.p", "rb" ))
        allianceNationsDict = pickle.load( open( "allianceNationsDict.p", "rb" ))
        programees_and_their_city_counts = pickle.load( open( "programees_and_their_city_counts.p", "rb" ))
        programees_and_their_warstatus = pickle.load( open( "programees_and_their_warstatus.p", "rb" ))

    net_production = {"money" : 0, "coal": 0, "oil": 0, "uranium": 0, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 0, "munitions": 0, "steel": 0, "aluminum": 0, "food": 0}
    for nation_id, needed_res in programees_and_their_netrevs.items():
        for resource, amount in needed_res.items():
            net_production[resource] += needed_res[resource]

    programees_and_their_weekly_netrevs = copy.deepcopy(net_production)
    for netres in programees_and_their_weekly_netrevs:
        programees_and_their_weekly_netrevs[netres] = programees_and_their_weekly_netrevs[netres] * 7#send_resource_multipler

    print("\nTOTAL CITIES: " + str(total_cities))

    print("\nPROGRAMEES AND THEIR DAILY NET PRODUCTION")
    print(programees_and_their_netrevs)
    print("\nPROGRAMEES AND THEIR CURRENT RESOURCES")
    print(programees_and_their_current_resources)
    print("\nPROGRAM DAILY NET PRODUCTION")
    print(net_production)
    print("\nPROGRAM ONE ROTATION (WEEKLYISH) NET PRODUCTION")
    print(programees_and_their_weekly_netrevs)
    print("\nALLIANCE BANK CONTENTS PRE-SEND")
    print(alliance_bank_contents)
    
    send_resources(programees_and_their_netrevs, programees_and_their_current_resources, alliance_bank_contents, session, allianceNationsDict, programees_and_their_city_counts, programees_and_their_warstatus)
    
    alliance_bank_contents = {}
    alliance_bank_page = etree.fromstring(session.get('https://politicsandwar.com/alliance/id=' + banking_alliance_id + '&display=bank', headers=headers).content, etree.HTMLParser())
    
    looking_for_div_index = True
    current_div_index = 0
    
    while looking_for_div_index:
        try:
            if alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[1]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', '').replace(' ', '') == 'Money':
                looking_for_div_index = False
            else:
                current_div_index += 1
        except:
            current_div_index += 1
    
    alliance_bank_contents['money'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[2]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('$', ''))
    alliance_bank_contents['food'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[3]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['coal'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[4]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['oil'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[5]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['uranium'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[6]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['lead'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[7]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['iron'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[8]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['bauxite'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[9]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['gasoline'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[10]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['munitions'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[11]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['steel'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[12]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    alliance_bank_contents['aluminum'] = float(alliance_bank_page.xpath('//*[@id="rightcolumn"]/div[' + str(current_div_index) + ']/div[1]/table/tr[13]/td[2]/text()')[0].replace(',', '').replace('\r', '').replace('\n', '').replace('\t', ''))
    
    print("\nALLIANCE BANK CONTENTS POST-SEND")
    print(alliance_bank_contents)
    print("\nWARCHEST TARGET")
    total_cities_by_CC = total_cities - 223
    warchest_target_dict = {"money" : 60000000 * total_cities_by_CC, "coal": 0, "oil": 0, "uranium": 250 * total_cities_by_CC, "lead": 0, "iron": 0, "bauxite": 0, "gasoline": 3000 * total_cities_by_CC, "munitions": 3000 * total_cities_by_CC, "steel": 3500 * total_cities_by_CC, "aluminum": 2000 * total_cities_by_CC, "food": 10000 * total_cities_by_CC}
    print(warchest_target_dict)
    for res_key in warchest_target_dict:
        alliance_bank_contents[res_key] -= warchest_target_dict[res_key]
    print("\nWARCHEST DIFFERENCE FROM ALLIANCE BANK")
    print(alliance_bank_contents)
    
    

    print("COMPLETE")
    print("Total elapsed time (sec): " + str(time.time() - start_time))

main()
