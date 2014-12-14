#!/usr/bin/env python
#---------------------------------------------------------------------
# Copyright (C) Bernd Gollesch 2014 <bgollesch@speed.at>:
#  You are free to use, redistribute, or even print and eat a copy of
#  this software so long as you include this copyright notice.
#  I guarantee there is at least one bug neither of us knew about.
#---------------------------------------------------------------------

######################################################################
# Imports

# python 2 <-> 3
from __future__ import absolute_import, with_statement, print_function, division, unicode_literals

import datetime         # some time handling

from os import listdir, remove, makedirs
from os.path import isdir

######################################################################
# Helper Classes

class System(object):
    """
        Describes a star system.

        Attributes:
            sysName  -- Name of the system
            stations -- List of Items from the commodity market
    """
    __slots__ = ('sysName', 'stations')

    def __init__(self, sysName):
        self.sysName  = sysName
        self.stations = []

    def name(self):
        return self.sysName.upper()

    def __str__(self):
        return self.sysName

######################################################################

class Station(object):
    """
        Describes a station

        Attributes:
            stnName -- Name of the station
            system  -- System the station is in
            items   -- List of Items from the commodity market
    """
    __slots__ = ('stnName', 'system', 'items')

    def __init__(self, stnName, system):
        self.stnName = stnName
        self.system  = system
        self.items   = []

    def name(self):
        return '%s/%s' % (self.system.name(), self.stnName)

    def __str__(self):
        return self.stnName

######################################################################

dictLevels = {
                "LOW":  1,
                "MED":  2,
                "HIGH": 3,
             }

class Item(object):
    """
        Describes a commodity

        Attributes:
            itmName     -- Name of the commodity
            tdCategory  -- Name of the Category for TD
            tdItem      -- Name of the Item for TD
            sell_to     -- Sell price of the station
            buy_from    -- Buy price of the station
            demand      -- Quantity of the demand
            demandLevel -- Level of the demand
            supply      -- Quantity of the supply
            supplyLevel -- Level of the supply
            timeStamp   -- Timestamp of the data
    """
    __slots__ = ('itmName', 'sell_to', 'buy_from', 'demand', 'demandLevel', 'supply', 'supplyLevel', 'timeStamp')

    def __init__(self, itmName, sell_to, buy_from=0, demand=0, demandLevel=None,
                 supply=0, supplyLevel=None, timeStamp=None):

        self.itmName     = itmName
        self.sell_to     = int(sell_to or 0)
        self.buy_from    = int(buy_from or 0)
        self.demand      = int(demand or 0)
        self.demandLevel = dictLevels.get(demandLevel.upper(), -1)
        self.supply      = int(supply or 0)
        self.supplyLevel = dictLevels.get(supplyLevel.upper(), 0)
        if timeStamp:
            self.timeStamp = datetime.datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M").isoformat(" ")
        else:
            self.timeStamp = "now"

    def name(self):
        return self.itmName.upper()

    def __str__(self):
        return self.itmName

######################################################################
# plugin Class

class TD_Export():
    def __init__(self, parent, path, debug=False):
        self.parent   = parent
        self.path     = path
        self.debug    = debug
        self.priceDir = self.path+"\\plugins\\TD_Export\\Prices"
        self.addPricesDir()
        self.mapOCR2TD = {}
        self.addMapping()

    def addPricesDir(self):
        if not isdir(self.priceDir):
            makedirs(self.priceDir)

    def addMapping(self):
        # TD needs a Category and is case sensitive for Category and Item names!
        self.mapOCR2TD["ADVANCED CATALYSERS"] = [ "Advanced Catalysers", "Technology" ]
        self.mapOCR2TD["AGRI-MEDICINES"] = [ "Agri-Medicines", "Medicines" ]
        self.mapOCR2TD["ALGAE"] = [ "Algae", "Foods" ]
        self.mapOCR2TD["ALLOYS"] = [ "Alloys", "Industrial Materials" ]
        self.mapOCR2TD["ALUMINIUM"] = [ "Aluminium", "Metals" ]
        self.mapOCR2TD["ANIMAL MEAT"] = [ "Animal Meat", "Foods" ]
        self.mapOCR2TD["ANIMAL MONITORS"] = [ "Animal Monitors", "Technology" ]
        self.mapOCR2TD["AQUAPONIC SYSTEMS"] = [ "Aquaponic Systems", "Technology" ]
        self.mapOCR2TD["ATMOSPHERIC PROCESSORS"] = [ "Atmospheric Processors", "Machinery" ]
        self.mapOCR2TD["AUTO-FABRICATORS"] = [ "Auto-Fabricators", "Technology" ]
        self.mapOCR2TD["BASIC MEDICINES"] = [ "Basic Medicines", "Medicines" ]
        self.mapOCR2TD["BATTLE WEAPONS"] = [ "Battle Weapons", "Weapons" ]
        self.mapOCR2TD["BAUXITE"] = [ "Bauxite", "Minerals" ]
        self.mapOCR2TD["BEER"] = [ "Beer", "Legal Drugs" ]
        self.mapOCR2TD["BERTRANDITE"] = [ "Bertrandite", "Minerals" ]
        self.mapOCR2TD["BERYLLIUM"] = [ "Beryllium", "Metals" ]
        self.mapOCR2TD["BIOREDUCING LICHEN"] = [ "Bioreducing Lichen", "Technology" ]
        self.mapOCR2TD["BIOWASTE"] = [ "Biowaste", "Waste" ]
        self.mapOCR2TD["CHEMICAL WASTE"] = [ "Chemical Waste", "Waste" ]
        self.mapOCR2TD["CLOTHING"] = [ "Clothing", "Consumer Items" ]
        self.mapOCR2TD["COBALT"] = [ "Cobalt", "Metals" ]
        self.mapOCR2TD["COFFEE"] = [ "Coffee", "Foods" ]
        self.mapOCR2TD["COLTAN"] = [ "Coltan", "Minerals" ]
        self.mapOCR2TD["COMBAT STABILISERS"] = [ "Combat Stabilisers", "Medicines" ]
        self.mapOCR2TD["COMPUTER COMPONENTS"] = [ "Computer Components", "Technology" ]
        self.mapOCR2TD["CONSUMER TECHNOLOGY"] = [ "Consumer Tech", "Consumer Items" ]
        self.mapOCR2TD["COPPER"] = [ "Copper", "Metals" ]
        self.mapOCR2TD["COTTON"] = [ "Cotton", "Textiles" ]
        self.mapOCR2TD["CROP HARVESTERS"] = [ "Crop Harvesters", "Machinery" ]
        self.mapOCR2TD["DOM. APPLIANCES"] = [ "Dom. Appliances", "Consumer Items" ]
        self.mapOCR2TD["EXPLOSIVES"] = [ "Explosives", "Chemicals" ]
        self.mapOCR2TD["FISH"] = [ "Fish", "Foods" ]
        self.mapOCR2TD["FOOD CARTRIDGES"] = [ "Food Cartridges", "Foods" ]
        self.mapOCR2TD["FRUIT AND VEGETABLES"] = [ "Fruit and Vegetables", "Foods" ]
        self.mapOCR2TD["GALLITE"] = [ "Gallite", "Minerals" ]
        self.mapOCR2TD["GALLIUM"] = [ "Gallium", "Metals" ]
        self.mapOCR2TD["GOLD"] = [ "Gold", "Metals" ]
        self.mapOCR2TD["GRAIN"] = [ "Grain", "Foods" ]
        self.mapOCR2TD["H.E. SUITS"] = [ "H.E. Suits", "Technology" ]
        self.mapOCR2TD["HYDROGEN FUEL"] = [ "Hydrogen Fuel", "Chemicals" ]
        self.mapOCR2TD["INDITE"] = [ "Indite", "Minerals" ]
        self.mapOCR2TD["INDIUM"] = [ "Indium", "Metals" ]
        self.mapOCR2TD["LAND ENRICHMENT SYSTEMS"] = [ "Land Enrichment Systems", "Technology" ]
        self.mapOCR2TD["LEATHER"] = [ "Leather", "Textiles" ]
        self.mapOCR2TD["LEPIDOLITE"] = [ "Lepidolite", "Minerals" ]
        self.mapOCR2TD["LIQUOR"] = [ "Liquor", "Legal Drugs" ]
        self.mapOCR2TD["LITHIUM"] = [ "Lithium", "Metals" ]
        self.mapOCR2TD["MARINE EQUIPMENT"] = [ "Marine Equipment", "Machinery" ]
        self.mapOCR2TD["MICROBIAL FURNACES"] = [ "Microbial Furnaces", "Machinery" ]
        self.mapOCR2TD["MINERAL EXTRACTORS"] = [ "Mineral Extractors", "Machinery" ]
        self.mapOCR2TD["MINERAL OIL"] = [ "Mineral Oil", "Chemicals" ]
        self.mapOCR2TD["NARCOTICS"] = [ "Narcotics", "Legal Drugs" ]
        self.mapOCR2TD["NATURAL FABRICS"] = [ "Natural Fabrics", "Textiles" ]
        self.mapOCR2TD["NON-LETHAL WPNS"] = [ "Non-Lethal Wpns", "Weapons" ]
        self.mapOCR2TD["PALLADIUM"] = [ "Palladium", "Metals" ]
        self.mapOCR2TD["PERFORMANCE ENHANCERS"] = [ "Performance Enhancers", "Medicines" ]
        self.mapOCR2TD["PERSONAL WEAPONS"] = [ "Personal Weapons", "Weapons" ]
        self.mapOCR2TD["PESTICIDES"] = [ "Pesticides", "Chemicals" ]
        self.mapOCR2TD["PLASTICS"] = [ "Plastics", "Industrial Materials" ]
        self.mapOCR2TD["PLATINUM"] = [ "Platinum", "Metals" ]
        self.mapOCR2TD["POLYMERS"] = [ "Polymers", "Industrial Materials" ]
        self.mapOCR2TD["POWER GENERATORS"] = [ "Power Generators", "Machinery" ]
        self.mapOCR2TD["PROGENITOR CELLS"] = [ "Progenitor Cells", "Medicines" ]
        self.mapOCR2TD["REACTIVE ARMOUR"] = [ "Reactive Armour", "Weapons" ]
        self.mapOCR2TD["RESONATING SEPARATORS"] = [ "Resonating Separators", "Technology" ]
        self.mapOCR2TD["ROBOTICS"] = [ "Robotics", "Technology" ]
        self.mapOCR2TD["RUTILE"] = [ "Rutile", "Minerals" ]
        self.mapOCR2TD["SCRAP"] = [ "Scrap", "Waste" ]
        self.mapOCR2TD["SEMICONDUCTORS"] = [ "Semiconductors", "Industrial Materials" ]
        self.mapOCR2TD["SILVER"] = [ "Silver", "Metals" ]
        self.mapOCR2TD["SUPERCONDUCTORS"] = [ "Superconductors", "Industrial Materials" ]
        self.mapOCR2TD["SYNTHETIC FABRICS"] = [ "Synthetic Fabrics", "Textiles" ]
        self.mapOCR2TD["SYNTHETIC MEAT"] = [ "Synthetic Meat", "Foods" ]
        self.mapOCR2TD["TANTALUM"] = [ "Tantalum", "Metals" ]
        self.mapOCR2TD["TEA"] = [ "Tea", "Foods" ]
        self.mapOCR2TD["TITANIUM"] = [ "Titanium", "Metals" ]
        self.mapOCR2TD["TOBACCO"] = [ "Tobacco", "Legal Drugs" ]
        self.mapOCR2TD["URANINITE"] = [ "Uraninite", "Minerals" ]
        self.mapOCR2TD["URANIUM"] = [ "Uranium", "Metals" ]
        self.mapOCR2TD["WATER PURIFIERS"] = [ "Water Purifiers", "Machinery" ]
        self.mapOCR2TD["WINE"] = [ "Wine", "Legal Drugs" ]

    def run(self, testMode=False):
        fileName = self.priceDir+"\\import.prices"
        if testMode:
            allRows = len(self.parent)
        else:
            allRows = self.parent.result_table.rowCount()

        # python 2 <-> 3
        try:
            xrange
        except NameError:
            xrange = range

        # initialization
        system  = None
        station = None
        oldSysName = None
        oldStnName = None

        systemList   = []
        systemByName = {}
        for row in xrange(0, allRows):

            if testMode:
                lineIn = [
                    self.parent[row][0], # station name
                    self.parent[row][1], # commodity name
                    self.parent[row][2], # sell
                    self.parent[row][3], # buy
                    self.parent[row][4], # demand
                    self.parent[row][5], # demand level
                    self.parent[row][6], # supply
                    self.parent[row][7], # supply level
                    self.parent[row][8], # timestamp
                    self.parent[row][9]  # system name
                ]
            else:
                lineIn = [
                    self.parent.result_table.item(row,0).text(), # station name
                    self.parent.result_table.item(row,1).text(), # commodity name
                    self.parent.result_table.item(row,2).text(), # sell
                    self.parent.result_table.item(row,3).text(), # buy
                    self.parent.result_table.item(row,4).text(), # demand
                    self.parent.result_table.item(row,5).text(), # demand level
                    self.parent.result_table.item(row,6).text(), # supply
                    self.parent.result_table.item(row,7).text(), # supply level
                    self.parent.result_table.item(row,8).text(), # timestamp
                    self.parent.result_table.item(row,9).text()  # system name
                ]


            # System
            sysName = lineIn[9] # system name
            if sysName.upper() != oldSysName:
                # check for System
                if self.debug: print("system changed to %s" % sysName)
                system = systemByName.get(sysName.upper(), None)
                oldSysName = sysName.upper()
                station = None
            if not system:
                # add new system
                if self.debug: print("new system: %s" % sysName)
                system = System(sysName)
                systemList.append(system)
                systemByName[system.name()] = system
                station = None

            # Station
            stnName = lineIn[0] # station name
            if stnName.upper() != oldStnName:
                # check for Station
                if self.debug: print("station changed to %s" % stnName)
                try:
                    station = next(x for x in system.stations if x.stnName.upper() == stnName.upper())
                except StopIteration:
                    station = None
                    pass
                oldStnName = stnName.upper()
            if not station:
                # add new station to system
                if self.debug: print("new station: %s" % stnName)
                station = Station(stnName, system)
                system.stations.append(station)

            # Item
            item = Item(lineIn[1], # commodity name
                        lineIn[2], # sell
                        lineIn[3], # buy
                        lineIn[4], # demand
                        lineIn[5], # demand level
                        lineIn[6], # supply
                        lineIn[7], # supply level
                        lineIn[8]  # timestamp
                       )
            station.items.append(item)

        naIQL     = "-"
        defIQL    = "?"
        levelDesc = "?0LMH"

        # now generate the price file if we have some data
        if len(systemList) > 0:
            with open(fileName, "w") as exportFile:
                exportFile.write(
                    "#! trade.py import -"
                    "\n"
                    "# TradeDangerous prices created by seeebek EliteOCR"
                    "\n"
                    "# File syntax:\n"
                    "# <item name> <sell> <buy> [<demand> <stock> [<timestamp>]]\n"
                    "#   Use '?' for demand/stock when you don't know/care,\n"
                    "#   Use '-' for demand/stock to indicate unavailable,\n"
                    "#   Otherwise use a number followed by L, M or H, e.g.\n"
                    "#     1L, 23M or 30000H\n"
                    "\n"
                )

                exportFile.write("#     {:<23}"
                                 " {:>7}"
                                 " {:>7}"
                                 "  {:>9}"
                                 " {:>9}"
                                 "  {}\n".format("Item Name",
                                                 "SellCr",
                                                 "BuyCr",
                                                 "Demand",
                                                 "Stock",
                                                 "Timestamp")
                                )


                for system in systemList:
                    for station in system.stations:
                        exportFile.write("\n\n@ %s\n" % station.name())
                        oldCategory = ""
                        for item in station.items:

                            itmName, catName = self.mapOCR2TD[item.name()]
                            if oldCategory != catName:
                                exportFile.write("   + {}\n".format(catName))
                                oldCategory = catName

                            if item.buy_from > 0:
                                # Zero demand-price gets default demand.
                                # If there is a price, always default to unknown
                                # because it can be sold here but the demand is just
                                # not useful as data.
                                demandStr = defIQL
                                if item.supplyLevel == 0:
                                    stockStr = naIQL
                                elif item.supplyLevel < 0 and item.supply <= 0:
                                    stockStr = defIQL
                                else:
                                    units = "?" if item.supply < 0 else str(item.supply)
                                    level = levelDesc[item.supplyLevel + 1]
                                    stockStr = units + level
                            else:
                                if item.demandLevel == 0:
                                    demandStr = naIQL
                                elif item.demandLevel < 0 and item.demand <= 0:
                                    demandStr = defIQL
                                else:
                                    units = "?" if item.demand < 0 else str(item.demand)
                                    level = levelDesc[item.demandLevel + 1]
                                    demandStr = units + level
                                stockStr = naIQL
                            exportFile.write("      {:<23}"
                                             " {:>7}"
                                             " {:>7}"
                                             "  {:>9}"
                                             " {:>9}"
                                             "  {}\n".format(itmName,
                                                             item.sell_to,
                                                             item.buy_from,
                                                             demandStr,
                                                             stockStr,
                                                             item.timeStamp)
                                            )


if __name__ == "__main__":
    test = [
                ["AUBAKIROV ORBITAL","EXPLOSIVES","311","","6461","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","HYDROGEN FUEL","101","102","","","12866","HIGH","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","MINERAL OIL","200","","24507","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","CLOTHING","471","","4007","HIGH","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","CONSUMER TECHNOLOGY","7088","","334","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","DOM. APPLIANCES","598","","756","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","ANIMAL MEAT","1641","","959","HIGH","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","COFFEE","1415","","140","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","FISH","670","","897","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","FOOD CARTRIDGES","245","","930","HIGH","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","FRUIT AND VEGETABLES","326","","391","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","GRAIN","259","","3738","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","SYNTHETIC MEAT","321","","506","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","TEA","1819","","840","HIGH","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","POLYMERS","87","103","","","741","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","SEMICONDUCTORS","884","907","","","997","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","SUPERCONDUCTORS","6957","7032","","","1021","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","BEER","182","","1350","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","LIQUOR","691","","100","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","WINE","261","","1414","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","MINERAL EXTRACTORS","652","","9425","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","MICROBIAL FURNACES","262","","46575","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","POWER GENERATORS","634","","3523","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","WATER PURIFIERS","311","","530","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","BASIC MEDICINES","471","","486","HIGH","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","PERFORMANCE ENHANCERS","7086","","423","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","PROGENITOR CELLS","7086","","155","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","ALUMINIUM","296","310","","","2514","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","BERYLLIUM","8613","8613","","","173","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","COBALT","694","713","","","2314","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","COPPER","443","462","","","1757","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","GALLIUM","5340","5398","","","248","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","GOLD","9896","9896","","","299","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","INDIUM","6125","6192","","","2257","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","LITHIUM","1615","1634","","","627","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","PALLADIUM","13665","13666","","","105","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","SILVER","5012","5067","","","499","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","TANTALUM","4060","4106","","","3074","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","TITANIUM","1014","1040","","","9021","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","URANIUM","2738","2769","","","416","LOW","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","BAUXITE","159","","11742","LOW","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","BERTRANDITE","2173","2198","","LOW","10098","HIGH","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","COLTAN","1612","","17936","MED","","","2014-12-06T18:15","Frigaha"],
                ["AUBAKIROV ORBITAL","GALLITE","1642","1661","","LOW","23379","HIGH","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","INDITE","2488","","13154","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","LEPIDOLITE","543","566","","","9364","MED","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","RUTILE","342","","27397","LOW","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","URANINITE","964","","15394","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","ADVANCED CATALYSERS","3076","","1197","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","BIOREDUCING LICHEN","1093","","8425","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","H.E. SUITS","346","","8923","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","RESONATING SEPARATORS","6223","","4515","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","SYNTHETIC FABRICS","133","148","","","5158","LOW","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","BIOWASTE","21","27","","","91","LOW","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","CHEMICAL WASTE","127","","1368","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","SCRAP","107","","2818","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","NON-LETHAL WPNS","1991","","28","MED","","","2014-12-06T18:16","Frigaha"],
                ["AUBAKIROV ORBITAL","REACTIVE ARMOUR","2260","","17","MED","","","2014-12-06T18:16","Frigaha"],
                ["ENGLE ORBITAL","EXPLOSIVES","311","","4140","LOW","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","HYDROGEN FUEL","101","102","","","18193","HIGH","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","MINERAL OIL","200","","52967","LOW","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","CLOTHING","468","","5578","HIGH","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","CONSUMER TECHNOLOGY","7087","","472","MED","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","DOM. APPLIANCES","723","","2028","HIGH","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","ANIMAL MEAT","1336","","459","LOW","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","COFFEE","1417","","254","MED","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","FISH","670","","1267","LOW","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","FOOD CARTRIDGES","242","","1294","HIGH","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","FRUIT AND VEGETABLES","346","","715","MED","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","GRAIN","326","","8890","HIGH","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","SYNTHETIC MEAT","321","","715","MED","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","TEA","1602","","647","MED","","","2014-12-06T19:07","Frigaha"],
                ["ENGLE ORBITAL","POLYMERS","87","103","","","1603","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","SEMICONDUCTORS","884","907","","","2159","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","SUPERCONDUCTORS","6956","7032","","","2209","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BEER","298","","7385","HIGH","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","LIQUOR","644","","142","LOW","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","WINE","287","","2863","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","MINERAL EXTRACTORS","608","","3630","LOW","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","MICROBIAL FURNACES","262","","100662","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","POWER GENERATORS","612","","6244","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","WATER PURIFIERS","311","","749","LOW","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BASIC MEDICINES","454","","521","HIGH","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","PERFORMANCE ENHANCERS","7086","","598","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","PROGENITOR CELLS","7086","","219","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","ALUMINIUM","296","310","","","5434","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BERYLLIUM","8612","8612","","","375","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","COBALT","694","713","","","3273","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","COPPER","443","462","","","3796","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","GALLIUM","5338","5396","","","539","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","GOLD","9895","9896","","","423","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","INDIUM","6125","6192","","","4878","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","LITHIUM","1614","1634","","","1357","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","PALLADIUM","13694","13695","","","54","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","SILVER","5012","5067","","","706","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","TANTALUM","4060","4106","","","6646","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","TITANIUM","1014","1040","","","19498","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","URANIUM","2738","2769","","","900","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BAUXITE","159","","24331","LOW","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BERTRANDITE","2788","","14344","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","COLTAN","1428","","17543","LOW","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","GALLITE","2333","","52258","HIGH","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","INDITE","2350","","19202","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","LEPIDOLITE","729","","12426","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","RUTILE","463","","155410","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","URANINITE","1130","","62895","HIGH","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","ADVANCED CATALYSERS","3076","","2587","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BIOREDUCING LICHEN","1093","","4817","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","H.E. SUITS","346","","16495","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","RESONATING SEPARATORS","6223","","9759","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","SYNTHETIC FABRICS","133","148","","","11149","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","BIOWASTE","24","30","","","121","LOW","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","CHEMICAL WASTE","127","","2956","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","SCRAP","93","","4410","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","NON-LETHAL WPNS","1990","","39","MED","","","2014-12-06T19:08","Frigaha"],
                ["ENGLE ORBITAL","REACTIVE ARMOUR","2257","","24","MED","","","2014-12-06T19:08","Frigaha"],
                ["ONIZUKA LANDING","EXPLOSIVES","315","","5765","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","HYDROGEN FUEL","101","102","","","15757","HIGH","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","MINERAL OIL","200","","39076","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","CLOTHING","471","","5835","HIGH","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","CONSUMER TECHNOLOGY","7087","","409","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","DOM. APPLIANCES","660","","1338","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","ANIMAL MEAT","1641","","1252","HIGH","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","COFFEE","1322","","133","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","FISH","670","","1098","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","FOOD CARTRIDGES","148","","399","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","FRUIT AND VEGETABLES","326","","479","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","GRAIN","215","","2557","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","SYNTHETIC MEAT","321","","619","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","TEA","1622","","604","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","POLYMERS","87","103","","","1182","LOW","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","SEMICONDUCTORS","884","907","","","1593","LOW","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","SUPERCONDUCTORS","6957","7032","","","1629","LOW","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","BEER","182","","1653","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","LIQUOR","717","","189","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","WINE","261","","1732","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","MINERAL EXTRACTORS","733","","12109","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","MICROBIAL FURNACES","262","","74261","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","POWER GENERATORS","723","","8127","HIGH","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","WATER PURIFIERS","311","","648","LOW","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","BASIC MEDICINES","394","","310","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","PERFORMANCE ENHANCERS","7086","","518","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","PROGENITOR CELLS","7087","","190","MED","","","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","ALUMINIUM","296","310","","","4009","LOW","2014-12-06T20:17","Frigaha"],
                ["ONIZUKA LANDING","BERYLLIUM","8613","8613","","","276","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","COBALT","694","713","","","2835","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","COPPER","443","462","","","2801","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","GALLIUM","5339","5397","","","397","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","GOLD","9896","9896","","","366","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","INDIUM","6125","6192","","","3599","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","LITHIUM","1614","1634","","","1001","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","PALLADIUM","13662","13663","","","86","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","SILVER","5012","5067","","","611","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","TANTALUM","4060","4106","","","4903","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","TITANIUM","1014","1040","","","14385","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","URANIUM","2738","2769","","","663","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","BAUXITE","165","","20418","LOW","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","BERTRANDITE","2173","2198","","LOW","19968","HIGH","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","COLTAN","1677","","32443","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","GALLITE","1931","","10545","LOW","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","INDITE","2195","","8115","LOW","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","LEPIDOLITE","810","","","","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","RUTILE","342","","41928","LOW","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","URANINITE","1171","","54225","HIGH","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","ADVANCED CATALYSERS","3076","","1909","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","BIOREDUCING LICHEN","1093","","2041","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","H.E. SUITS","346","","12072","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","RESONATING SEPARATORS","6223","","7200","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","SYNTHETIC FABRICS","133","148","","","8223","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","BIOWASTE","21","27","","","114","LOW","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","CHEMICAL WASTE","127","","2181","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","SCRAP","75","","1824","LOW","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","NON-LETHAL WPNS","1990","","34","MED","","","2014-12-06T20:18","Frigaha"],
                ["ONIZUKA LANDING","REACTIVE ARMOUR","2273","","22","MED","","","2014-12-06T20:18","Frigaha"],
    ]

    tdexporter = TD_Export(test, "..\\..", debug=True)
    tdexporter.run(testMode=True)