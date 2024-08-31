"""
 Namecheap Management library of common functions used by
 all the namecheap execution modules

 Installation Prerequisites
 --------------------------

 - This module uses the following python libraries to communicate to
   the namecheap API:

        * ``requests``
        .. code-block:: bash

            pip install requests

"""

import logging
import xml.dom.minidom

import salt.loader

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Get logging started
log = logging.getLogger(__name__)

__salt__ = None


def __virtual__():
    if not HAS_REQUESTS:
        return (
            False,
            "Missing dependency: 'requests'. The namecheap utils module "
            "cannot be loaded. ",
        )
    global __salt__
    if not __salt__:
        __salt__ = salt.loader.minion_mods(__opts__)
    return True


def post_request(opts):
    namecheap_url = __salt__["config.option"]("namecheap.url")
    return _handle_request(requests.post(namecheap_url, data=opts, timeout=45))


def get_request(opts):
    namecheap_url = __salt__["config.option"]("namecheap.url")
    return _handle_request(requests.get(namecheap_url, params=opts, timeout=45))


def _handle_request(r):
    r.close()

    if r.status_code > 299:
        log.error(str(r))
        raise Exception(str(r))

    response_xml = xml.dom.minidom.parseString(r.text)
    apiresponse = response_xml.getElementsByTagName("ApiResponse")[0]

    if apiresponse.getAttribute("Status") == "ERROR":
        data = []
        errors = apiresponse.getElementsByTagName("Errors")[0]
        for e in errors.getElementsByTagName("Error"):
            data.append(e.firstChild.data)
        error = "".join(data)
        log.info(apiresponse)
        log.error(error)
        raise Exception(error)

    return response_xml



def get_opts(command):
    opts = {}
    opts["ApiUser"] = __salt__["config.option"]("namecheap.name")
    opts["UserName"] = __salt__["config.option"]("namecheap.user")
    opts["ApiKey"] = __salt__["config.option"]("namecheap.key")
    opts["ClientIp"] = __salt__["config.option"]("namecheap.client_ip")
    opts["Command"] = command
    return opts
