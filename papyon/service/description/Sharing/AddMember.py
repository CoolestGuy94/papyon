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

from __future__ import absolute_import
from .common import *

def transport_headers():
    """Returns a dictionary, containing transport (http) headers
    to use for the request"""

    return {}

def soap_action():
    """Returns the SOAPAction value to pass to the transport
    or None if no SOAPAction needs to be specified"""

    return "http://www.msn.com/webservices/AddressBook/AddMember"

def soap_body(member_role, type, state, account):
    """Returns the SOAP xml body"""
    stuff = ""

    if type == 'Passport':
        stuff = "<PassportName>%s</PassportName>" % account
    elif type == 'Email':
        stuff = """<Email>%s</Email>
        <Annotations><Annotation>
            <Name>MSN.IM.BuddyType</Name>
            <Value>32:</Value>
        </Annotation></Annotations>""" % account

    return """
        <AddMember xmlns="http://www.msn.com/webservices/AddressBook">
            <serviceHandle>
                <Id>
                    0
                </Id>
                <Type>
                    Messenger
                </Type>
                <ForeignId>
                </ForeignId>
            </serviceHandle>
            <memberships>
                <Membership>
                    <MemberRole>
                        %s
                    </MemberRole>
                    <Members>
                        <Member xsi:type="%sMember" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                            <Type>
                                %s
                            </Type>
                            <State>
                                %s
                            </State>
                                %s
                        </Member>
                    </Members>
                </Membership>
            </memberships>
        </AddMember>""" % (member_role, type, type, state, stuff)

def process_response(soap_response):
    return True
