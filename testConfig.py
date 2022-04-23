from configparser import ConfigParser

config = ConfigParser()
config.read("screens_config.ini")


config.remove_section("screen_3")

# config.set("screen_1", "font_size", "120")
with open('screens_config.ini', 'w') as configfile:
	config.write(configfile)

# print(config["screen_1"]["font_size"])


# try:
# 	config.add_section("screen_3")
# except:
# 	pass

# config.set("screen_3", "font_size", "0")
# with open("screens_config.ini", "w") as configfile:
# 	config.write(configfile)

# print(config.get("screen_3", "font_size"))