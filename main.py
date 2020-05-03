#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import server


def main():
    try:
        serv = server.Server('Simple', '0.0.0.0', 10010, server.Connector)
        print('[serv_start] {}'.format(serv.name))
        serv.serve_forever()
    except Exception as e:
        print('[CRUSH] | '+ str(e))


main()
