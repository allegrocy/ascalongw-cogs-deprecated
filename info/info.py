import discord
import time
import datetime
from discord.ext import commands
from redbot.core import checks

zm=["Sanctum Cay", "Rilohn Refuge", "Warband of Brothers", "Borlis Pass", "Imperial Sanctum", "Moddok Crevice", "Nolani Academy", "Destruction's Depths", "Venta Cemetery", "Fort Ranik", "A Gate Too Far", "Minister Cho's Estate", "Thunderhead Keep", "Tihark Orchard", "Finding the Bloodstone", "Dunes of Despair", "Vizunah Square", "Jokanur Diggings", "Iron Mines of Moladune", "Kodonur Crossroads", "G.O.L.E.M.", "Arborstone", "Gates of Kryta", "Gate of Madness", "The Elusive Golemancer", "Riverside Province", "Boreas Seabed", "Ruins of Morah", "Hell's Precipice", "Ruins of Surmia", "Curse of the Nornbear", "Sunjiang District", "Elona Reach", "Gate of Pain", "Blood Washes Blood", "Bloodstone Fen", "Jennur's Horde", "Gyala Hatchery", "Abaddon's Gate", "The Frost Gate", "Augury Rock", "Grand Court of Sebelkeh", "Ice Caves of Sorrow", "Raisu Palace", "Gate of Desolation", "Thirsty River", "Blacktide Den", "Against the Charr", "Abaddon's Mouth", "Nundu Bay", "Divinity Coast", "Zen Daijun", "Pogahn Passage", "Tahnnakai Temple", "The Great Northern Wall", "Dasha Vestibule", "The Wilds", "Unwaking Waters", "Chahbek Village", "Aurora Glade", "A Time for Heroes", "Consulate Docks", "Ring of Fire", "Nahpui Quarter", "The Dragon's Lair", "Dzagonur Bastion", "D'Alessio Seaboard", "Assault on the Stronghold", "The Eternal Grove"]
zb=["Forgewight", "Baubao Wavewrath", "Joffs the Mitigator", "Rragar Maneater", "Chung, the Attuned", "Lord Jadoth", "Nulfastu, Earthbound", "The Iron Forgeman", "Magmus", "Mobrin, Lord of the Marsh", "Jarimiya the Unmerciful", "Duncan the Black", "Quansong Spiritspeak", "The Stygian Underlords", "Fozzy Yeoryios", "The Black Beast of Arrgh", "Arachni", "The Four Horsemen", "Remnant of Antiquities", "Arbor Earthcall", "Prismatic Ooze", "Lord Khobay", "Jedeh the Mighty", "Ssuns, Blessed of Dwayna", "Justiciar Thommis", "Harn and Maxine Coldstone", "Pywatt the Swift", "Fendi Nin", "Mungri Magicbox", "Priest of Menzies", "Ilsundur, Lord of Fire", "Kepkhet Marrowfeast", "Commander Wahli", "Kanaxai", "Khabuus", "Molotov Rocktail", "The Stygian Lords", "Dragon Lich", "Havok Soulwail", "Ghial the Bone Dancer", "Murakai, Lady of the Night", "Rand Stormweaver", "Verata", "Droajam, Mage of the Sands", "Royen Beastkeeper", "Eldritch Ettin", "Vengeful Aatxe", "Fronis Irontoe", "Urgoz", "Fenrir", "Selvetarm", "Mohby Windbeak", "Charged Blackness", "Rotscale", "Zoldark the Unholy", "Korshek the Immolated", "Myish, Lady of the Lake", "Frostmaw the Kinslayer", "Kunvie Firewing", "Z'him Monns", "The Greater Darkness", "TPS Regulator Golem", "Plague of Destruction", "The Darknesses", "Admiral Kantoh", "Borrguus Blisterbark"]
zv=["Reed Bog", "Unwaking Waters", "Stingray Strand", "Sunward Marches", "Regent Valley", "Wajjun Bazaar", "Yatendi Canyons", "Twin Serpent Lakes", "Sage Lands", "Xaquang Skyway", "Zehlon Reach", "Tangle Root", "Silverwood", "Zen Daijun", "The Arid Sea", "Nahpui Quarter", "Skyward Reach", "The Scar", "The Black Curtain", "Panjiang Peninsula", "Snake Dance", "Traveler's Vale", "The Breach", "Lahtenda Bog", "Spearhead Peak", "Mount Qinkai", "Marga Coast", "Melandru's Hope", "The Falls", "Joko's Domain", "Vulture Drifts", "Wilderness of Bahdza", "Talmark Wilderness", "Vehtendi Valley", "Talus Chute", "Mineral Springs", "Anvil Rock", "Arborstone", "Witman's Folly", "Arkjok Ward", "Ascalon Foothills", "Bahdok Caverns", "Cursed Lands", "Alcazia Tangle", "Archipelagos", "Eastern Frontier", "Dejarin Estate", "Watchtower Coast", "Arbor Bay", "Barbarous Shore", "Deldrimor Bowl", "Boreas Seabed", "Cliffs of Dohjok", "Diessa Lowlands", "Bukdek Byway", "Bjora Marches", "Crystal Overlook", "Diviner's Ascent", "Dalada Uplands", "Drazach Thicket", "Fahranur, the First City", "Dragon's Gullet", "Ferndale", "Forum Highlands", "Dreadnought's Drift", "Drakkar Lake", "Dry Top", "Tears of the Fallen", "Gyala Hatchery", "Ettin's Back", "Gandara, the Moon Fortress", "Grothmar Wardowns", "Flame Temple Corridor", "Haiju Lagoon", "Frozen Forest", "Garden of Seborhin", "Grenth's Footprint", "Jaya Bluffs", "Holdings of Chokhin", "Ice Cliff Chasms", "Griffon's Mouth", "Kinya Province", "Issnur Isles", "Jaga Moraine", "Ice Floe", "Maishang Hills", "Jahai Bluffs", "Riven Earth", "Icedome", "Minister Cho's Estate", "Mehtani Keys", "Sacnoth Valley", "Iron Horse Mine", "Morostav Trail", "Plains of Jarin", "Sparkfly Swamp", "Kessex Peak", "Mourning Veil Falls", "The Alkali Pan", "Varajar Fells", "Lornar's Pass", "Pongmei Valley", "The Floodplain of Mahnkelon", "Verdant Cascades", "Majesty's Rest", "Raisu Palace", "The Hidden City of Ahdashim", "Rhea's Crater", "Mamnoon Lagoon", "Shadow's Passage", "The Mirror of Lyss", "Saoshang Trail", "Nebo Terrace", "Shenzun Tunnels", "The Ruptured Heart", "Salt Flats", "North Kryta Province", "Silent Surf", "The Shattered Ravines", "Scoundrel's Rise", "Old Ascalon", "Sunjiang District", "The Sulfurous Wastes", "Magus Stones", "Perdition Rock", "Sunqua Vale", "Turai's Procession", "Norrhart Domains", "Pockmark Flats", "Tahnnakai Temple", "Vehjin Mines", "Poisoned Outcrops", "Prophet's Path", "The Eternal Grove", "Tasca's Demise", "Resplendent Makuun"]
zc=["Fort Aspenwood", "Heroes' Ascent", "Alliance Battles", "Guild Versus Guild", "Codex Arena", "Random Arena", "Fort Aspenwood", "Alliance Battles", "Jade Quarry", "Codex Arena", "Heroes' Ascent", "Guild Versus Guild", "Alliance Battles", "Heroes' Ascent", "Guild Versus Guild", "Codex Arena", "Fort Aspenwood", "Jade Quarry", "Random Arena", "Codex Arena", "Guild Versus Guild", "Jade Quarry", "Alliance Battles", "Heroes' Ascent", "Random Arena", "Fort Aspenwood", "Jade Quarry", "Random Arena"]
nickitem=["3 Mummy Wrappings", "2 Shadowy Remnants", "3 Ancient Kappa Shells", "1 Geode", "2 Fibrous Mandragor Roots", "3 Gruesome Ribcages", "2 Kraken Eyes", "3 Bog Skale Fins", "2 Sentient Spores", "2 Ancient Eyes", "3 Copper Shillings", "3 Frigid Mandragor Husks", "3 Bolts of Linen", "3 Charr Carvings", "3 Red Iris Flowers", "3 Feathered Avicara Scalps", "2 Margonite Masks", "2 Quetzal Crests", "3 Plague Idols", "2 Azure Remains", "1 Mandragor Root Cake", "1 Mahgo Claw", "5 Mantid Pincers", "3 Sentient Seeds", "2 Stone Grawl Necklaces", "1 Herring", "3 Naga Skins", "1 Gloom Seed", "1 Charr Hide", "1 Ruby Djinn Essence", "2 Thorny Carapaces", "3 Bone Charms", "3 Modniir Manes", "3 Superb Charr Carvings", "5 Rolls of Parchment", "2 Roaring Ether Claws", "3 Branches of Juni Berries", "3 Shiverpeak Manes", "3 Fetid Carapaces", "2 Moon Shells", "1 Massive Jawbone", "1 Chromatic Scale", "3 Mursaat Tokens", "1 Sentient Lodestone", "3 Jungle Troll Tusks", "1 Sapphire Djinn Essence", "1 Stone Carving", "3 Feathered Caromi Scalps", "1 Pillaged Goods", "1 Gold Crimson Skull Coin", "3 Jade Bracelets", "2 Minotaur Horns", "2 Frosted Griffon Wings", "2 Silver Bullion Coins", "1 Truffle", "3 Skelk Claws", "2 Dessicated Hydra Claws", "3 Frigid Hearts", "3 Celestial Essences", "1 Phantom Residue", "1 Drake Kabob", "3 Amber Chunks", "2 Glowing Hearts", "5 Saurian Bones", "2 Behemoth Hides", "1 Luminous Stone", "3 Intricate Grawl Necklaces", "3 Jadeite Shards", "1 Gold Doubloon", "2 Shriveled Eyes", "2 Icy Lodestones", "1 Keen Oni Talon", "2 Hardened Humps", "2 Piles of Elemental Dust", "3 Naga Hides", "3 Spiritwood Planks", "1 Stormy Eye", "3 Skree Wings", "3 Soul Stones", "1 Spiked Crest", "1 Dragon Root", "3 Berserker Horns", "1 Behemoth Jaw", "1 Bowl of Skalefin Soup", "2 Forest Minotaur Horns", "3 Putrid Cysts", "2 Jade Mandibles", "2 Maguuma Manes", "1 Skull Juju", "3 Mandragor Swamproots", "1 Bottle of Vabbian Wine", "2 Weaver Legs", "1 Topaz Crest", "2 Rot Wallow Tusks", "2 Frostfire Fangs", "1 Demonic Relic", "2 Abnormal Seeds", "1 Diamond Djinn Essence", "2 Forgotten Seals", "5 Copper Crimson Skull Coins", "3 Mossy Mandibles", "2 Enslavement Stones", "5 Elonian Leather Squares", "2 Cobalt Talons", "1 Maguuma Spider Web", "5 Forgotten Trinket Boxes", "3 Icy Humps", "1 Sandblasted Lodestone", "3 Black Pearls", "3 Insect Carapaces", "3 Mergoyle Skulls", "3 Decayed Orr Emblems", "5 Tempered Glass Vials", "3 Scorched Lodestones", "1 Water Djinn Essence", "1 Guardian Moss", "6 Dwarven Ales", "2 Amphibian Tongues", "2 Alpine Seeds", "2 Tangled Seeds", "3 Stolen Supplies", "1 Pahnai Salad", "3 Vermin Hides", "1 Roaring Ether Heart", "3 Leathery Claws", "1 Azure Crest", "1 Jotun Pelt", "2 Heket Tongues", "5 Mountain Troll Tusks", "3 Vials of Ink", "3 Kournan Pendants", "3 Singed Gargoyle Skulls", "3 Dredge Incisors", "3 Stone Summit Badges", "3 Krait Skins", "2 Inscribed Shards", "3 Feathered Scalps"]
nicklocation=["The Sulfurous Wastes", "The Black Curtain", "The Undercity", "Yatendi Canyons", "Grothmar Wardowns", "Dragon's Gullet", "Boreas Seabed (explorable area)", "Scoundrel's Rise", "Sunward Marches", "Sage Lands", "Cliffs of Dohjok", "Norrhart Domains", "Traveler's Vale", "Flame Temple Corridor", "Regent Valley", "Mineral Springs", "Poisoned Outcrops", "Alcazia Tangle", "Wajjun Bazaar", "Dreadnought's Drift", "Arkjok Ward", "Perdition Rock", "Saoshang Trail", "Fahranur, The First City", "Sacnoth Valley", "Twin Serpent Lakes", "Mount Qinkai", "The Falls", "The Breach", "The Alkali Pan", "Majesty's Rest", "Rhea's Crater", "Varajar Fells", "Dalada Uplands", "Zen Daijun (explorable area)", "Garden of Seborhin", "Bukdek Byway", "Deldrimor Bowl", "Eastern Frontier", "Gyala Hatchery (explorable area)", "The Arid Sea", "Ice Cliff Chasms", "Ice Floe", "Bahdok Caverns", "Tangle Root", "Resplendent Makuun", "Arborstone (explorable area)", "North Kryta Province", "Holdings of Chokhin", "Haiju Lagoon", "Tahnnakai Temple (explorable area)", "Prophet's Path", "Snake Dance", "Mehtani Keys", "Morostav Trail", "Verdant Cascades", "The Scar", "Spearhead Peak", "Nahpui Quarter (explorable area)", "Lornar's Pass", "Issnur Isles", "Ferndale", "Stingray Strand", "Riven Earth", "Wilderness of Bahdza", "Crystal Overlook", "Witman's Folly", "Shadow's Passage", "Barbarous Shore", "Skyward Reach", "Icedome", "Silent Surf", "Nebo Terrace", "Drakkar Lake", "Panjiang Peninsula", "Griffon's Mouth", "Pockmark Flats", "Forum Highlands", "Raisu Palace (explorable area)", "Tears of the Fallen", "Drazach Thicket", "Jaga Moraine", "Mamnoon Lagoon", "Zehlon Reach", "Kessex Peak", "Sunjiang District (explorable area)", "Salt Flats", "Silverwood", "The Eternal Grove (explorable area)", "Lahtenda Bog", "Vehtendi Valley", "Magus Stones", "Diviner's Ascent", "Pongmei Valley", "Anvil Rock", "The Ruptured Heart", "Talmark Wilderness", "The Hidden City of Ahdashim", "Vulture Drifts", "Kinya Province", "Ettin's Back", "Grenth's Footprint", "Jahai Bluffs", "Vehjin Mines", "Reed Bog", "Minister Cho's Estate (explorable area)", "Iron Horse Mine", "The Shattered Ravines", "Archipelagos", "Marga Coast", "Watchtower Coast", "Cursed Lands", "Mourning Veil Falls", "Old Ascalon", "Turai's Procession", "Maishang Hills", "The Floodplain of Mahnkelon", "Sparkfly Swamp", "Frozen Forest", "Dry Top", "Jaya Bluffs", "Plains of Jarin", "Xaquang Skyway", "The Mirror of Lyss", "Ascalon Foothills", "Unwaking Waters (explorable area)", "Bjora Marches", "Dejarin Estate", "Talus Chute", "Shenzun Tunnels", "Gandara, the Moon Fortress", "Diessa Lowlands", "Melandru's Hope", "Tasca's Demise", "Arbor Bay", "Joko's Domain", "Sunqua Vale"]
nickregion=["The Desolation", "Kryta", "Kaineng City", "Vabbi", "Charr Homelands", "Ascalon", "The Jade Sea", "Kryta", "Kourna", "Maguuma Jungle", "Istan", "Far Shiverpeaks", "Northern Shiverpeaks", "Ascalon", "Ascalon", "Southern Shiverpeaks", "The Desolation", "Tarnished Coast", "Kaineng City", "Southern Shiverpeaks", "Kourna", "Ring of Fire Islands", "Shing Jea Island", "Istan", "Charr Homelands", "Kryta", "The Jade Sea", "Maguuma Jungle", "Ascalon", "The Desolation", "Kryta", "The Jade Sea", "Far Shiverpeaks", "Charr Homelands", "Shing Jea Island", "Vabbi", "Kaineng City", "Northern Shiverpeaks", "Ascalon", "The Jade Sea", "Crystal Desert", "Far Shiverpeaks", "Southern Shiverpeaks", "Kourna", "Maguuma Jungle", "Vabbi", "Echovald Forest", "Kryta", "Vabbi", "Shing Jea Island", "Kaineng City", "Crystal Desert", "Southern Shiverpeaks", "Istan", "Echovald Forest", "Tarnished Coast", "Crystal Desert", "Southern Shiverpeaks", "Kaineng City", "Southern Shiverpeaks", "Istan", "Echovald Forest", "Kryta", "Tarnished Coast", "Vabbi", "The Desolation", "Southern Shiverpeaks", "Kaineng City", "Kourna", "Crystal Desert", "Southern Shiverpeaks", "The Jade Sea", "Kryta", "Far Shiverpeaks", "Shing Jea Island", "Northern Shiverpeaks", "Ascalon", "Vabbi", "Kaineng City", "Kryta", "Echovald Forest", "Far Shiverpeaks", "Maguuma Jungle", "Istan", "Kryta", "Kaineng City", "Crystal Desert", "Maguuma Jungle", "Echovald Forest", "Istan", "Vabbi", "Tarnished Coast", "Crystal Desert", "Kaineng City", "Northern Shiverpeaks", "The Desolation", "Kryta", "Vabbi", "Crystal Desert", "Shing Jea Island", "Maguuma Jungle", "Southern Shiverpeaks", "Kourna", "Vabbi", "Maguuma Jungle", "Shing Jea Island", "Northern Shiverpeaks", "The Desolation", "The Jade Sea", "Kourna", "Kryta", "Kryta", "Echovald Forest", "Ascalon", "The Desolation", "The Jade Sea", "Kourna", "Tarnished Coast", "Southern Shiverpeaks", "Maguuma Jungle", "Shing Jea Island", "Istan", "Kaineng City", "Vabbi", "Ascalon", "The Jade Sea", "Far Shiverpeaks", "Kourna", "Southern Shiverpeaks", "Kaineng City", "Kourna", "Ascalon", "Echovald Forest", "Southern Shiverpeaks", "Tarnished Coast", "The Desolation", "Shing Jea Island"]
bonuspve=["Zaishen Mission", "Pantheon", "Faction Support", "Zaishen Vanquishing", "Extra Luck", "Elonian Support", "Zaishen Bounty", "Factions Elite", "Northern Support"]
bonuspveinfo=["Double copper Zaishen Coin rewards for Zaishen missions", "Free passage to the Underworld and the Fissure of Woe", "Double Kurzick and Luxon title track points for exchanging faction", "Double copper Zaishen Coin rewards for Zaishen vanquishes", "Keys and lockpicks drop at four times the usual rate and double Lucky and Unlucky title points", "Double Sunspear and Lightbringer points", "Double copper Zaishen Coin rewards for Zaishen bounties", "The Deep and Urgoz's Warren can be entered from Kaineng Center", "Double Asura, Deldrimor, Ebon Vanguard, or Norn reputation points"]
bonuspvp=["Alliance Battle", "Random Arenas", "Guild Versus Guild", "Competitive Mission", "Heroes' Ascent", "Codex Arena"]
bonuspvpinfo=["Double Balthazar and Imperial faction in Alliance Battles", "Double Balthazar faction and Gladiator title points in Random Arenas", "Double Balthazar faction and Champion title points in GvG", "Double Balthazar and Imperial faction in the Jade Quarry and Fort Aspenwood", "Double Balthazar faction and Hero title points in Heroes' Ascent", "Double Balthazar faction and Codex title points in Codex Arena"]
eventnames=["Canthan New Year", "Lucky Treats Week", "April Fools' Day", "Sweet Treats Week", "Anniversary Celebration", "Dragon Festival", "Wintersday in July", "Wayfarer's Reverie", "Pirate Week", "Halloween", "Special Treats Week", "Wintersday"]
eventdesc=["Different miniature available from that year's Lunar Fortunes. Shing Jea Boardwalk is open. Quests. Special drop: Lunar Token.", "Special drops: Four-Leaf Clover and Shamrock Ale.", "Quests.", "Special drops: Chocolate Bunny and Golden Egg.", "Shing Jea Boardwalk is open. Complete cooperative missions to receive Proofs of Legend. Elite Xunlai Agent Isa Ku and Sadie Salvitas appear. Special drops: Battle Isle Iced Tea, Birthday Cupcake, Bottle Rocket, Champagne Popper, Delicious Cake, Hard Apple Cider, Honeycomb, Hunter's Ale, Krytan Brandy, Party Beacon, Sparkler, Sugary Blue Drink, and Victory Token.", "Shing Jea Boardwalk is open. Mini-missions and quests. Special drop: Victory Token.", "Dwayna Vs Grenth. Special drops: Eggnog, Frosty Tonic, Fruitcake, Mischievous Tonic, and Snowman Summoner.", "Quests. Special drop: Wayfarer's Mark.", "NPCs talk like a pirate (and some will look like one). Special drop: Bottle of Grog.", "Quests. Costume Brawl. Scarred Psyche. Halloween trophy collectors. Special drops: Trick-or-Treat Bags.", "Special drops: Hard Apple Cider and Slice of Pumpkin Pie.", "Quests. Dwayna Vs Grenth. The Great Snowball Fight of the Gods (PvP). Wintersday trophy collectors. Special drops: Candy Cane Shard, Eggnog, Frosty Tonic, Fruitcake, Mischievous Tonic, and Snowman Summoner."]
eventstartdates=[[1,31,20],[3,14,19],[4,1,7],[4,10,19],[4,22,19],[6,27,19],[7,24,19],[8,25,19],[9,13,19],[10,18,19],[11,21,20],[12,19,20]]
eventenddates=[[2,7,20],[3,21,19],[4,2,7],[4,17,19],[5,6,19],[7,4,19],[7,31,19],[9,1,19],[9,20,19],[11,2,8],[11,28,20],[1,2,20]]
sb=['Justiciar Sevaan', 'Insatiable Vakar', 'Amalek the Unmerciful', 'Carnak the Hungry', 'Valis the Rampant', 'Cerris', 'Sarnia the Red-Handed', 'Destor the Truth Seeker', 'Selenas the Blunt', 'Justiciar Amilyn', 'Maximilian the Meticulous', 'Joh the Hostile', 'Barthimus the Provident', 'Calamitous', 'Greves the Overbearing', 'Lev the Condemned', 'Justiciar Marron', 'Justiciar Kasandra', 'Vess the Disputant', 'Justiciar Kimii', 'Zaln the Jaded']
vq=['Countess Nadya', 'Footman Tate', 'Bandits', 'Utini Wupwup', 'Ascalonian Noble', 'Undead', 'Blazefiend Griefblade', 'Farmer Hamnet', 'Charr']
ns=['Unnatural Seeds', 'Worn Belts', 'Grawl Necklaces', 'Baked Husks', 'Skeletal Limbs', 'Red Iris Flowers', 'Charr Carvings', 'Skale Fins', 'Dull Carapaces', 'Enchanted Lodestones', 'Charr Carvings', 'Spider Legs', 'Red Iris Flowers', 'Worn Belts', 'Dull Carapaces', 'Grawl Necklaces', 'Baked Husks', 'Skeletal Limbs', 'Unnatural Seeds', 'Enchanted Lodestones', 'Skale Fins', 'Icy Lodestones', 'Gargoyle Skulls', 'Dull Carapaces', 'Baked Husks', 'Red Iris Flowers', 'Spider Legs', 'Skeletal Limbs', 'Charr Carvings', 'Enchanted Lodestones', 'Grawl Necklaces', 'Icy Lodestones', 'Worn Belts', 'Gargoyle Skulls', 'Unnatural Seeds', 'Skale Fins', 'Red Iris Flowers', 'Enchanted Lodestones', 'Skeletal Limbs', 'Charr Carvings', 'Spider Legs', 'Baked Husks', 'Gargoyle Skulls', 'Unnatural Seeds', 'Icy Lodestones', 'Grawl Necklaces', 'Enchanted Lodestones', 'Worn Belts', 'Dull Carapaces', 'Spider Legs', 'Gargoyle Skulls', 'Icy Lodestones']


def timedelta_to_str(timedelta):
    h, rem = divmod(timedelta.total_seconds(), 3600)
    m, s = divmod(rem, 60)
    h, m, s = int(h), int(m), int(s)
    if h == 0:
        new_string = f"{m} minutes"
    elif m == 0:
        new_string = f"{h} hours"
    else:
        new_string = f"{h} hours and {m} minutes"
    return new_string

def get_sanford(days_modifier=0):
    t_start = datetime.datetime(2017,11,30,7)
    t_now = datetime.datetime.utcnow()
    t_since = t_now - t_start
    days_since = t_since // datetime.timedelta(days=1)
    days_since += days_modifier
    index = days_since % len(ns)
    timeleft_ns = datetime.timedelta(days=1) - ((t_now - t_start) % datetime.timedelta(days=1))
    timeleft_ns = timedelta_to_str(timeleft_ns)
    return ns[index], timeleft_ns

def get_sb_and_vq(days_modifier=0):
    t_start = datetime.datetime(2017,11,30,16)
    t_now = datetime.datetime.utcnow()
    t_since = t_now - t_start
    days_since = t_since // datetime.timedelta(days=1)
    days_since += days_modifier
    index = days_since % len(sb)
    sb_name = sb[index]
    index = days_since % len(vq)
    vq_name = vq[index]
    timeleft_sb_vq = datetime.timedelta(days=1) - ((t_now - t_start) % datetime.timedelta(days=1))
    timeleft_sb_vq = timedelta_to_str(timeleft_sb_vq)
    return sb_name, vq_name, timeleft_sb_vq

def get_prestring(days_modifier=0):
    ns_name, timeleft_ns = get_sanford(days_modifier)
    sb_name, vq_name, timeleft_sb_vq = get_sb_and_vq(days_modifier)
    prestring = (
        f"__Today's Pre-searing Quests: __\n"
        f"Vanguard Quest: **{vq_name}**\n"
        f"Vanguard Quest resets in: **{timeleft_sb_vq}**\n"
        f"Nicholas Sanford: **{ns_name}**\n"
        f"Nicholas Sanford resets in: **{timeleft_ns}**")
    if days_modifier == 1:
        prestring = (
            f"__Tomorrow's Pre-searing Quests: __\n"
            f"Vanguard Quest: **{vq_name}**\n"
            f"Vanguard Quest resets in: **{timeleft_sb_vq}**\n"
            f"Nicholas Sanford: **{ns_name}**\n"
            f"Nicholas Sanford resets in: **{timeleft_ns}**")
    return prestring

def get_sb_and_vq(days_modifier=0):
    t_start = datetime.datetime(2017,11,30,16)
    t_now = datetime.datetime.utcnow()
    t_since = t_now - t_start
    days_since = t_since // datetime.timedelta(days=1)
    days_since += days_modifier
    index = days_since % len(sb)
    sb_name = sb[index]
    index = days_since % len(vq)
    vq_name = vq[index]
    timeleft_sb_vq = datetime.timedelta(days=1) - ((t_now - t_start) % datetime.timedelta(days=1))
    timeleft_sb_vq = timedelta_to_str(timeleft_sb_vq)
    return sb_name, vq_name, timeleft_sb_vq

def get_wikstring(days_modifier=0):
    sb_name, vq_name, timeleft_sb_vq = get_sb_and_vq(days_modifier)
    wikstring = (
        f"__Today's War-In-Kryta Quests: __\n"
        f"Shining Blade Quest: **{sb_name}**\n"
        f"Shining Blade resets in: **{timeleft_sb_vq}**\n")
    if days_modifier == 1:
        wikstring = (
            f"__Tomorrow's War-In-Kryta Quests: __\n"
            f"Shining Blade Quest: **{sb_name}**\n"
            f"Shining Blade resets in: **{timeleft_sb_vq}**\n")
    return wikstring

def timecal(y,m,d,h):
    global dayselapsedinteger
    global weekselapsedinteger
    global daysleft
    global timeleft
    global zqstring
    global zqstringnext
    global nickinfo
    global nicktimer
    global nickstring
    global nickstringnext
    global weeklystring
    global weeklystringnext

    t = datetime.datetime.utcnow().replace(microsecond=0)
    zqtime = datetime.datetime(t.year,t.month,t.day,h)
    timeleft = (zqtime - t) % datetime.timedelta(days=1)

    dailystart = datetime.datetime(y,m,d,h)
    dayselapsed = t + timeleft - dailystart - datetime.timedelta(days=1)
    dayselapsedinteger = int(dayselapsed.total_seconds() / 60 / 60 / 24)
    weekselapsedinteger = int(dayselapsed.total_seconds() / 60 / 60 / 24 / 7)
    daysleft = 6 - (dayselapsedinteger % 7)

    dq1 = "Zaishen Mission: **" +  zm[dayselapsedinteger%len(zm)] + "**. "
    dq2 = "Zaishen Bounty: **" + zb[dayselapsedinteger%len(zb)] + "**. "
    dq3 = "Zaishen Vanquish: **" + zv[dayselapsedinteger%len(zv)] + "**. "
    dq4 = "Zaishen Combat: **" + zc[dayselapsedinteger%len(zc)] + "**. "
    zqtimer = "Zaishen Daily Quests will reset in **" + str(timeleft) + "**!"
    zqstring = dq1 + "\n" + dq2 + "\n" + dq3 + "\n" + dq4 + "\n" + zqtimer
    zqstringnext = "__Tomorrow's Zaishen Quests: __\n" + zqstring
    nickinfo = nickitem[weekselapsedinteger%len(nickitem)] + "** per present at **" + nicklocation[weekselapsedinteger%len(nicklocation)] + "** in " + nickregion[weekselapsedinteger%len(nickregion)] + ".\n"
    nicktimer = "Moving off in **" + str(daysleft) + " days** and **" + str(timeleft) + "**!"
    nickstring = nickinfo + nicktimer
    nickstringnext = "__Next week:__\nNicholas will be collecting **" + nickinfo + nicktimer
    weeklypve = "PvE bonuses: " + bonuspve[weekselapsedinteger%len(bonuspve)] + " -- **" + bonuspveinfo[weekselapsedinteger%len(bonuspveinfo)] + "**.\n"
    weeklypvp = "PvP bonuses: " + bonuspvp[weekselapsedinteger%len(bonuspvp)] + " -- **" + bonuspvpinfo[weekselapsedinteger%len(bonuspvpinfo)] + "**.\n"
    weeklytimer = "Weekly bonuses will expire in **" + str(daysleft) + " days** and **" + str(timeleft) + "**!"
    weeklystring = weeklypve + weeklypvp + weeklytimer
    weeklystringnext = "__Next week: __\n" + weeklystring

def event():
    global eventnames, eventdesc, eventstartdates, eventenddates

    t = datetime.datetime.utcnow().replace(microsecond=0)

    # For testing purposes
    # t = datetime.datetime(2018, 12, 19, 1)

    # Check if event is ongoing or has ended
    year = 2017
    x = 0
    while True:
        eventstart_t = datetime.datetime(year,eventstartdates[x][0],eventstartdates[x][1],eventstartdates[x][2])
        if x == 11:
            year2 = year + 1
            eventend_t = datetime.datetime(year2,eventenddates[x][0],eventenddates[x][1],eventenddates[x][2])
        else:
            eventend_t = datetime.datetime(year,eventenddates[x][0],eventenddates[x][1],eventenddates[x][2])
        if t >= eventstart_t and t < eventend_t:
            event_started = True
            break
        else:
            previous_x = (x + 12 - 1) % 12
            previous_eventend_t = datetime.datetime(year,eventenddates[previous_x][0],eventenddates[previous_x][1],eventenddates[previous_x][2])
            if t < eventstart_t and t > previous_eventend_t:
                event_started = False
                break
        if x == 11:
            x = 0
            year += 1
        else:
            x += 1
        if year == 2999:
            break

    # First sentence.
    if event_started is True:
        timetoeventend = eventend_t - t
        eventenddate = datetime.datetime(year,eventenddates[x][0],eventenddates[x][1],eventenddates[x][2])
        stringeventcurrent = "**{}** has begun! {} \nEvent ends in **{}**! ({} UCT)\n".format(eventnames[x%12], eventdesc[x%12], str(timetoeventend), str(eventenddate))
        x = (x + 1) % 12
        if x == 0:
            year += 1

    elif event_started is False:
        stringeventcurrent =  "Aww... **{}** has ended. \n".format(eventnames[previous_x])
    
    next_eventstartdate = datetime.datetime(year,eventstartdates[x][0],eventstartdates[x][1],eventstartdates[x][2])
    timetonexteventstart = next_eventstartdate - t
    
    # Second sentence
    stringeventnext = "The next event is **" +  eventnames[x%12] + "**. " + eventdesc[x%12] + " \nEvent begins in: **" + str(timetonexteventstart) + "**! (" + str(next_eventstartdate) + " UCT)"

    stringevent = stringeventcurrent + stringeventnext
    return stringevent

class Info:
    """Information on Zaishen Quests, Nicholas the Traveler, weekly bonuses, events and fort aspenwood."""

    def __init__(self, bot):
        self.bot = bot

    def get_channel(self, server, channel_name):
        return discord.utils.get(server.channels, name=channel_name)

    @commands.command()
    async def zq(self, ctx):
        """Displays current Zaishen Quest information with a countdown."""
        timecal(2016,11,30,16)
        await ctx.send("__Today's Zaishen Quests: __\n" + zqstring)

    @commands.command()
    async def zqnext(self, ctx):
        """Displays next Zaishen Quest information with a countdown."""
        timecal(2016,11,29,16)
        await ctx.send(zqstringnext)

    @commands.command()
    async def pre(self, ctx):
        """Displays current Pre-searing dailies information with a countdown."""
        prestring = get_prestring(0)
        await ctx.send(prestring)

    @commands.command()
    async def prenext(self, ctx):
        """Displays next Pre-searing dailies information with a countdown."""
        prestring = get_prestring(1)
        await ctx.send(prestring)

    @commands.command()
    async def wik(self, ctx):
        """Displays War-In-Kryta dailies information with a countdown."""
        wikstring = get_wikstring(0)
        await ctx.send(wikstring)

    @commands.command()
    async def wiknext(self, ctx):
        """Displays next War-In-Kryta dailies information with a countdown."""
        wikstring = get_wikstring(1)
        await ctx.send(wikstring)

    @commands.command()
    async def nick(self, ctx):
        """Displays current Nicholas the Traveler information + countdown."""
        timecal(2016,11,28,15)
        await ctx.send("__This week: __\nNicholas the Traveler is collecting **" + nickstring)

    @commands.command()
    async def nicknext(self, ctx):
        """Displays next Nicholas the Traveler information with a countdown."""
        timecal(2016,11,21,15)
        await ctx.send(nickstringnext)

    @commands.command()
    async def bonus(self, ctx):
        """Displays current weekly bonuses information with a countdown."""
        timecal(2016,11,28,15)
        await ctx.send("__This week: __\n" + weeklystring)

    @commands.command()
    async def bonusnext(self, ctx):
        """Displays next weekly bonuses information with a countdown."""
        timecal(2016,11,21,15)
        await ctx.send(weeklystringnext)

    @commands.command()
    async def fa(self, ctx):
        """Displays Fort Aspenwood information with a countdown."""
        timecal(2016,12,3,21)
        if daysleft == 6:
            daysleftFA = 0
        else:
            daysleftFA = daysleft

        if (timeleft > datetime.timedelta(hours=20)) and (daysleftFA == 0):
            FAstring = "Fort Aspenwood comes alive every weekend at 4pm (EST) or 9pm (UTC/GMT)!\n**The games have begun!** Head over to Fort Aspenwood now and get in line!\nThe next FA games begin in... **" + str(daysleftFA) + " days and " + str(timeleft) + "**"
        elif (timeleft > datetime.timedelta(hours=20)) and (daysleftFA == 5):
            FAstring = "Fort Aspenwood comes alive every weekend at 4pm (EST) or 9pm (UTC/GMT)!\n**The games have begun!** Head over to Fort Aspenwood now and get in line!\nThe next FA games begin in... **" + str(daysleftFA) + " days and " + str(timeleft) + "**"
        else:
            FAstring = "Fort Aspenwood comes alive every weekend at 4pm (EST) or 9pm (UTC/GMT)!\nLet the games begin in... **" + str(daysleftFA) + " days and " + str(timeleft) + "**!"
        await ctx.send(FAstring)

    @commands.command()
    async def event(self, ctx):
        """Displays special events information + countdowns to start and end."""
        stringevent = event()
        await ctx.send(stringevent)

    @commands.command()
    async def all(self, ctx):
        """Displays information on Zaishen, Nick and Weekly Bonuses."""
        await self.all_info(ctx)

    @commands.command()
    async def listall(self, ctx):
        """Displays information on Zaishen, Nick and Weekly Bonuses."""
        await self.all_info(ctx)

    async def all_info(self, ctx):
        timecal(2016,11,30,16)
        info1 = "```Zaishen Quests today```" + zqstring + "\n"
        timecal(2016,11,28,15)
        info2 = "```Nicholas The Traveler```Nicholas the Traveler is collecting **" + nickstring + "\n"
        timecal(2016,11,28,15)
        info3 = "```This week's bonuses```" + weeklystring
        stringevent = event()
        await ctx.send(info1 + info2 + info3 + "```Special event: ```" + stringevent)

    async def links_string(self):
        links_string = "Main Wiki: <https://wiki.guildwars.com/wiki/Main_Page>\nFBGM Wiki: <http://wiki.fbgmguild.com/Main_Page>\nPvX Wiki: <http://gwpvx.gamepedia.com/PvX_wiki>\nGuild Wars Legacy Forums: <https://guildwarslegacy.com/index.php>\nSub-Reddit: <https://www.reddit.com/r/GuildWars/>\nKamadan Trade Log: <https://kamadan.decltype.org/>\nGvG match database: <http://memorial.redeemer.biz/>\nGvG videos: <http://web.ist.utl.pt/ist176479/>"
        return links_string

    @commands.command()
    async def links(self, ctx):
        """Provides you with a list of helpful links."""
        links_string = await self.links_string()
        await ctx.send(links_string)

    @commands.command()
    async def link(self, ctx):
        """Provides you with a list of helpful links."""
        links_string = await self.links_string()
        await ctx.send(links_string)

    @commands.command()
    async def cny(self, ctx):
        """Countdown to CNY finale."""
        t = datetime.datetime.utcnow().replace(microsecond=0)
        cny_end = datetime.datetime(2017,2,7,20)
        cny_NPC_end = datetime.datetime(2017,2,14,20)

        if (t < cny_end):
            await ctx.send("Canthan New Year has begun. CNY will end in **%s**." % (cny_end-t))
        elif (t > cny_end and t < cny_NPC_end):
            await ctx.send("Canthan New Year has ended but NPCs will remain until **%s**." % (cny_NPC_end - t))
        elif (t > cny_end and t > cny_NPC_end):
            await ctx.send("Canthan New Year has ended and NPCs have left.")

        t = datetime.datetime.utcnow().replace(microsecond=0)
        finale_start = datetime.datetime(2017,2,6,8)
        finale_end = datetime.datetime(2017,2,7,8)
        time_to_start = finale_start - t
        time_to_end = finale_end - t

        if (t > finale_start and t < finale_end):
            #Finale has started
            i = 0
            while i <= 24:
                finale_cycle = finale_start + datetime.timedelta(hours=i)
                time_to_finale_cycle = finale_cycle - t
                if time_to_finale_cycle > datetime.timedelta(microseconds=1):
                    break
                i += 3
            output = "Canthan New Year Finale has begun! The next finale cycle will begin in: **%s**. All finales will end in **%s**." % (time_to_finale_cycle, time_to_end)
        elif (t < finale_start):
            #Finale has not started
            output = "Canthan New Year Finale will begin in **%s**!" % (time_to_start)
        elif (t > finale_end):
            #Finale has ended
            output = "Canthan New Year Finale has ended."
        await ctx.send(output)

    @commands.command()
    async def nickfarm(self, ctx):
        url = "<https://gwpvx.gamepedia.com/Guide:Nicholas_the_Traveler_Farming/list#"
        timecal(2016,11,28,15)
        nick_item = nickitem[weekselapsedinteger%len(nickitem)][2:].replace(" ", "_")
        url = url + nick_item + ">"
        await ctx.send(url)


    """INFO 2.0"""
    @checks.is_owner()
    @commands.command()
    async def a1(self, ctx):
        pass
