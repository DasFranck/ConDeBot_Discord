#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random

from collections import OrderedDict

import hjson

from classes.Plugin import Plugin

NAME = "Lists"
DESCRIPTION = ""
USAGE = {}


# Load the lists file into an array of dict
def load_lists(lists_path):
    if (os.path.isfile(lists_path)):
        with open(lists_path, encoding="utf8") as lists_file:
            try:
                return hjson.load(lists_file)
            except:
                return None
    else:
        return []


# Get the reply dict assign to the trigger
def get_list(lists, name):
    if (lists is None):
        return None
    for lst in lists:
        if (lst["name"] == name):
            return lst
    return None


# Write the lists to the hjson file
def write_to_file(lists_path, lists):
    with open(lists_path, 'w', encoding="utf8") as lists_file:
        hjson.dump(lists, lists_file, indent=' ' * 2)


class ListsPlugin(Plugin):
    def __init__(self, cdb):
        super().__init__(cdb)
        self.LISTS_DIR_PATH = self.cdb.DATA_PATH + "lists/"
        os.makedirs(self.LISTS_DIR_PATH, exist_ok=True)
        cdb.reserve_keywords(["list"], "Lists")

    async def add_to_list(self, lists, list_name, content, message, author):
        old_dict = get_list(lists, list_name)
        if (old_dict is None):
            new_dict = OrderedDict(name=list_name, list=[content], count=0, locked=False)
            lists.append(new_dict)
            self.cdb.log_info("The new list %s has been created by %s" % (list_name, author), message)
        else:
            # Check if the reply dict is locked
            if (not self.cdb.isop_user(message.author) and "locked" in old_dict and old_dict["locked"] is True):
                await message.channel.send("Sorry, the %s list has been locked by an operator." % list_name)
                self.cdb.log_warn("The locked list %s modification has been requested by NON-OP %s, FAILED" % (list_name, author), message)
                return lists
            else:
                old_dict["list"].append(content)
                self.cdb.log_info("A new element has been added in the list %s by %s" % (list_name, author), message)
        await message.channel.send("Roger that, a new element has been added in %s (index: %d)." % (list_name, len(get_list(lists, list_name)["list"]) - 1))
        return lists

    async def write_random_from_list(self, lists, list_name, message, author):
        lst = get_list(lists, list_name)
        index = random.randrange(len(lst["list"]))
        await message.channel.send(lst["list"][index])
        await message.channel.send(str(index))
        self.cdb.log_info("A random content from the list %s has been requested by %s" % (list_name, author), message)
        lst["count"] += 1
        return lists

    async def on_message(self, message, cmd):
        if not cmd \
           or not cmd.triggered \
           or cmd.action not in ["list"]:
            return

        # Set file path
        if message.guild is not None:
            lists_path = f"{self.LISTS_DIR_PATH}{message.guild.id}.json"
        else:
            lists_path = f"{self.LISTS_DIR_PATH}.dump.json"

        # Load JSON lists file
        lists = load_lists(lists_path)
        if not lists:
            self.cdb.logger.error("JSON lists file loading failed.")
            await message.channel.send("The JSON lists file seems corrupted. Please fix it before using the replier module.")
            return

        if len(cmd.args) > 1:
            if cmd.args[1] == "add":
                if len(cmd.args) == 2:
                    await message.channel.send("Try with a content to put in the list next time.")
                else:
                    new_lists = await self.add_to_list(lists, cmd.args[0], " ".join(cmd.args[2:]), message, str(cmd.author))
                    write_to_file(lists_path, new_lists)
            if cmd.args[1] == "get":
                pass
            if cmd.args[1] == "del":
                pass
            if cmd.args[1] == "count":
                pass
            if cmd.args[1] == "size":
                pass
            if cmd.args[1] == "lock":
                pass

        elif len(cmd.args) == 1:
            new_lists = await self.write_random_from_list(lists, cmd.args[0], message, str(cmd.author))
            write_to_file(lists_path, new_lists)

        else:
            await message.channel.send("Try with an argument for this command next time.")
            return
        return
