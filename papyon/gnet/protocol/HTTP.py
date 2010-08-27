# -*- coding: utf-8 -*-
#
# Copyright (C) 2006  Ali Sabil <ali.sabil@gmail.com>
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

from papyon.gnet.constants import *
from papyon.gnet.proxy import ProxyInfos
from papyon.gnet.message.HTTP import HTTPRequest
from papyon.gnet.io import TCPClient
from papyon.gnet.parser import HTTPParser
from papyon.gnet.proxy.factory import ProxyFactory

import gobject
import base64
import platform

__all__ = ['HTTP']


class HTTP(gobject.GObject):
    """HTTP protocol client class."""
    
    __gsignals__ = {
            "error" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (gobject.TYPE_ULONG,)),

            "response-received": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)), # HTTPResponse

            "request-sent": (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,)), # HTTPRequest
            }

    def __init__(self, host, port=80, proxies={}):
        """Connection initialization
        
            @param host: the host to connect to.
            @type host: string

            @param port: the port number to connect to
            @type port: integer

            @param proxies: proxies that we can use to connect
            @type proxies: L{gnet.proxy.ProxyInfos}"""
        gobject.GObject.__init__(self)
        self._host = host
        self._port = port
        self._proxies = proxies
        self.__http_proxy = None
        self._transport = None
        self._http_parser = None
        self._outgoing_queue = []
        self._waiting_response = False

        self._errored = False
        self.connect("error", self._on_self_error)

    def _on_self_error(self, *args):
        self._errored = True

    def _setup_transport(self):
        if self._transport is None:
            if self._proxies and self._proxies.get('http', None):
                if self._proxies['http'].type == 'http':
                    self.__http_proxy = self._proxies['http']

            if self.__http_proxy:
                self._transport = TCPClient(self.__http_proxy.host,
                        self.__http_proxy.port)
            else:
                self._transport = TCPClient(self._host, self._port)
                if self._proxies:
                    self._transport = ProxyFactory(self._transport,
                            self._proxies, 'http')
            self._setup_parser()
        
        if self._transport.get_property("status") != IoStatus.OPEN:
            self._transport.open()

    def _setup_parser(self):
        self._http_parser = HTTPParser(self._transport)
        self._http_parser.connect("received", self._on_response_received)
        self._transport.connect("notify::status", self._on_status_change)
        self._transport.connect("error", self._on_error)
        self._transport.connect("sent", self._on_request_sent)

    def _on_status_change(self, transport, param):
        if transport.get_property("status") == IoStatus.OPEN:
            self._process_queue()
        elif transport.get_property("status") == IoStatus.CLOSED and\
                (self._waiting_response or len(self._outgoing_queue) > 0) and\
                not self._errored:
            self._waiting_response = False
            self._setup_transport()

    def _on_request_sent(self, transport, request, length):
        assert(str(self._outgoing_queue[0]) == request)
        self._waiting_response = True
        self.emit("request-sent", self._outgoing_queue[0])

    def _on_response_received(self, parser, response):
        if response.status >= 100 and response.status < 200:
            return
        #if response.status in (301, 302): # UNTESTED: please test
        #    location = response.headers['Location']

        #    location = location.rsplit("://", 1)
        #    if len(location) == 2:
        #        scheme = location[0]
        #        location = location[1]
        #    if scheme == "http":
        #        location = location.rsplit(":", 1)
        #        self._host = location[0]
        #        if len(location) == 2:
        #            self._port = int(location[1])
        #        self._outgoing_queue[0].headers['Host'] = response.headers['Location']
        #        self._setup_transport()
        #        return
        self._outgoing_queue.pop(0) # pop the request from the queue
        self.emit("response-received", response)
        self._waiting_response = False
        self._process_queue() # next request ?

    def _on_error(self, transport, error):
        self.emit("error", error)

    def _process_queue(self):
        if len(self._outgoing_queue) == 0 or \
                self._waiting_response: # no pipelining
            return
        if self._transport is None or \
                self._transport.get_property("status") != IoStatus.OPEN:
            self._setup_transport()
            return
        self._transport.send(str(self._outgoing_queue[0]))

    def request(self, resource='/', headers=None, data='', method='GET'):
        if headers is None:
            headers = {}
        headers['Host'] = self._host + ':' + str(self._port)
        headers['Content-Length'] = str(len(data))
        if 'User-Agent' not in headers:
            user_agent = GNet.NAME, GNet.VERSION, platform.system(), platform.machine()
            headers['User-Agent'] = "%s/%s (%s %s)" % user_agent

        if self.__http_proxy is not None:
            url = 'http://%s:%d%s' % (self._host, self._port, resource)
            if self.__http_proxy.user:
                auth = self.__http_proxy.user + ':' + self.__http_proxy.password
                credentials = base64.encodestring(auth).strip()
                headers['Proxy-Authorization'] = 'Basic ' + credentials
        else:
            url = resource
        request  = HTTPRequest(headers, data, method, url)
        self._outgoing_queue.append(request)
        self._process_queue()

    def close(self):
        if self._transport:
            self._transport.close()
