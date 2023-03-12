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

import xml.sax.saxutils as xml

def transport_headers():
    """Returns a dictionary, containing transport (http) headers
    to use for the request"""

    return {}

def soap_action():
    """Returns the SOAPAction value to pass to the transport
    or None if no SOAPAction needs to be specified"""

    return "http://www.msn.com/webservices/AddressBook/ABGroupUpdate"

def soap_body(group_id, group_name):
    """Returns the SOAP xml body"""

    return """
        <ABGroupUpdate xmlns="http://www.msn.com/webservices/AddressBook">
            <abId>
                00000000-0000-0000-0000-000000000000
            </abId>
            <groups>
                <Group>
                    <groupId>
                        %(group_id)s
                    </groupId>
                    <groupInfo>
                        <name>
                            %(group_name)s
                        </name>
                    </groupInfo>
                    <propertiesChanged>
                        GroupName
                    </propertiesChanged>
                </Group>
            </groups>
        </ABGroupUpdate>""" % { 'group_id' : group_id,
                                'group_name' : xml.escape(group_name) }

def process_response(soap_response):
    return True
