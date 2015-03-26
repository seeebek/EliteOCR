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
            stations -- List of stations in the system
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
            self.timeStamp = datetime.datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M").isoformat(b" ")
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
        self.parent = parent
        self.path   = path
        self.debug  = debug
        self.mapOCR2TD = {}
        self.addMapping()

    def addMapping(self):
        # TD needs a Category and is case sensitive for Category and Item names!
        self.mapOCR2TD["ADVANCED CATALYSERS"] = [ "Advanced Catalysers", "Technology" ]
        self.mapOCR2TD["AGRI-MEDICINES"] = [ "Agri-Medicines", "Medicines" ]
        self.mapOCR2TD["ALGAE"] = [ "Algae", "Foods" ]
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
        self.mapOCR2TD["CONSUMER TECH"] = [ "Consumer Technology", "Consumer Items" ]
        self.mapOCR2TD["CONSUMER TECHNOLOGY"] = [ "Consumer Technology", "Consumer Items" ]
        self.mapOCR2TD["COPPER"] = [ "Copper", "Metals" ]
        self.mapOCR2TD["CROP HARVESTERS"] = [ "Crop Harvesters", "Machinery" ]
        self.mapOCR2TD["DOM. APPLIANCES"] = [ "Domestic Appliances", "Consumer Items" ]
        self.mapOCR2TD["DOMESTIC APPLIANCES"] = [ "Domestic Appliances", "Consumer Items" ]
        self.mapOCR2TD["EXPLOSIVES"] = [ "Explosives", "Chemicals" ]
        self.mapOCR2TD["FISH"] = [ "Fish", "Foods" ]
        self.mapOCR2TD["FOOD CARTRIDGES"] = [ "Food Cartridges", "Foods" ]
        self.mapOCR2TD["FRUIT AND VEGETABLES"] = [ "Fruit And Vegetables", "Foods" ]
        self.mapOCR2TD["GALLITE"] = [ "Gallite", "Minerals" ]
        self.mapOCR2TD["GALLIUM"] = [ "Gallium", "Metals" ]
        self.mapOCR2TD["GOLD"] = [ "Gold", "Metals" ]
        self.mapOCR2TD["GRAIN"] = [ "Grain", "Foods" ]
        self.mapOCR2TD["H.E. SUITS"] = [ "H.E. Suits", "Technology" ]
        self.mapOCR2TD["HYDROGEN FUEL"] = [ "Hydrogen Fuel", "Chemicals" ]
        self.mapOCR2TD["IMPERIAL SLAVES"] = [ "Imperial Slaves", "Slavery" ]
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
        self.mapOCR2TD["NON-LETHAL WPNS"] = [ "Non-Lethal Weapons", "Weapons" ]
        self.mapOCR2TD["NON-LETHAL WEAPONS"] = [ "Non-Lethal Weapons", "Weapons" ]
        self.mapOCR2TD["PAINITE"] = [ "Painite", "Minerals" ]
        self.mapOCR2TD["PALLADIUM"] = [ "Palladium", "Metals" ]
        self.mapOCR2TD["PERFORMANCE ENHANCERS"] = [ "Performance Enhancers", "Medicines" ]
        self.mapOCR2TD["PERSONAL WEAPONS"] = [ "Personal Weapons", "Weapons" ]
        self.mapOCR2TD["PESTICIDES"] = [ "Pesticides", "Chemicals" ]
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
        self.mapOCR2TD["SLAVES"] = [ "Slaves", "Slavery" ]
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

    def run(self, exportList):

        # export destination
        try:
            exportDir = unicode(self.parent.settings["export_dir"]).encode('windows-1252')
        except:
            exportDir = "."
            pass
        if not isdir(exportDir):
            makedirs(exportDir)
        fileName = exportDir+str("\\import.prices")

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
        for row in exportList:

            if row[0] == "System":
                # skip header line
                continue

            # System, we need a name
            sysName = row[0] # system name
            if not sysName:
                sysName = "!Unknown!"

            if sysName.upper() != oldSysName:
                # check for System
                if self.debug: print("system changed to %s" % sysName)
                system = systemByName.get(sysName.upper(), None)
                oldSysName = sysName.upper()
                station    = None
                oldStnName = None
            if not system:
                # add new system
                if self.debug: print("new system: %s" % sysName)
                system = System(sysName)
                systemList.append(system)
                systemByName[system.name()] = system
                station    = None
                oldStnName = None

            # Station
            stnName = row[1] # station name
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
            item = Item(row[2], # commodity name
                        row[3], # sell
                        row[4], # buy
                        row[5], # demand
                        row[6], # demand level
                        row[7], # supply
                        row[8], # supply level
                        row[9]  # timestamp
                       )
            station.items.append(item)

        naIQL     = "-"
        defIQL    = "?"
        levelDesc = "?0LMH"

        # now generate the price file if we have some data
        if len(systemList) > 0:
            with open(fileName, "w") as exportFile:
                exportFile.write(
                    "#! trade.py import -\n"
                    "\n"
                    "# TradeDangerous prices created by EliteOCR from seeebek\n"
                    "# see http://forums.frontier.co.uk/showthread.php?t=68771\n"
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

                            itmName, catName = self.mapOCR2TD.get(item.name(), [item.itmName, "Unknown"])
                            if self.debug and catName == "Unknown":
                                print("Unknown Commodity: %s" % itmName)
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