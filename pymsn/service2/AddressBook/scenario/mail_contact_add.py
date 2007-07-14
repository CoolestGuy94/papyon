# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Johann Prieur <johann.prieur@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
from pymsn.service2.description.AB import ContactType

class MailContactAddScenario(BaseScenario):
    def __init__(self, ab, callback, errback, mail_address="", contact_info={}):
        """Adds a mail contact and updates the address book.

            @param ab: the adress book service
            @param callback: tuple(callable, *args)
            @param errback: tuple(callable, *args)"""
        BaseScenario.__init__(self, 'ContactSave', callback, errback)
        self.__ab = ab

        self.__mail_address = mail_address
        self.__contact_info = contact_info

    def __set_mail_address(self, mail_address):
        self.__mail_address = mail_address
    def __get_mail_address(self):
        return self.__mail_address
    mail_address = property(__get_mail_address, __set_mail_address,
                            doc="The mail address of the contact")
    
    def __set_contact_info(self, contact_info):
        self.__contact_info = contact_info
    def __get_contact_info(self):
        return self.__contact_info
    contact_info = property(__get_contact_info, __set_contact_info,
                            doc="A dict which contains addressbook " \
                                "information about the contact")

    def execute(self):
        contact_info['passport_name'] = self.__mail_address
        contact_info['is_messenger_user'] = False
        self.__ab.ContactAdd(self.__scenario, self.__contact_info, {},
                             self.__contact_add_callback, 
                             self.__contact_add_errback)

    def __contact_add_callback(self, stuff):
        self.__callback(stuff)
        # TODO : get the cached lastchanged date to make a delta findall
        # or directly call a sync scenario
        self.__ab.FindAll(self.__scenario, True, None,
                          self.__find_all_callback, self.__find_all_errback)

    def __contact_add_errback(self, reason):
        # TODO : analyse the reason, and maybe call execute again
        # instead of transmitting it via __errback.
        self.__errback(reason)

    def __find_all_callback(self):
        # TODO : complete the contact list in the client, need to access to
        # the local address book storage, not the service..
        pass

    def __find_all_errback(self, reason):
        self.__errback(reason)
