#!/usr/bin/python
# 2021 - Matthieu Walter

import pan.xapi
from xml.etree import ElementTree


HOST    = "10.1.1.1"
API_KEY = "APIKEY"

# users you do not want to kick
SKIP = ["my_user"]


def dump_xml(xml):
    print ElementTree.tostring(xml, encoding='utf8', method='xml')

def _exec_cmd(cmd):
    ''' execute a PA command
    '''

    xapi = pan.xapi.PanXapi(hostname=HOST, api_key=API_KEY)
    xapi.op(cmd=cmd)
    data = xapi.xml_root()


    response = ElementTree.fromstring(data)
    if response.attrib['status'] != 'success':
        raise Exception

    results = [e for e in response.getchildren() if e.tag == 'result']
    if not len(results):
        raise Exception

    return results[0]



def get_all_gp_users(gateway):
    users = []
    
    xml = _exec_cmd("""<show>
                        <global-protect-gateway>
                            <current-user>
                                <gateway>%s</gateway>
                            </current-user>
                        </global-protect-gateway>
                       </show>"""%gateway)

    for e in xml.findall("entry"):
        username = e.find("username").text
        domain   = e.find("domain").text
        computer = e.find("computer").text

        users.append({
                        "username": username,
                        "domain":   domain,
                        "computer": computer
                        })
    return users



def get_gp_gateways():
    # gateway[name] = portal // gateway-N
    gateways = {}
    xml = _exec_cmd("""<show>
                        <global-protect-gateway>
                            <gateway>
                                <type>remote-user</type>
                            </gateway>
                        </global-protect-gateway>
                    </show>""")
    #dump_xml(xml)
    #for gw in xml.findall("entry/gateway-name"):
    for gw in xml.findall("entry"):
        gw_name = gw.find("gateway-name").text
        portal  = gw.find("portal").text
        gateways[gw_name] = portal

    return gateways



def kick_user(gateway, user, domain, computer):
    xml = _exec_cmd("""<request>
                        <global-protect-gateway>
                            <client-logout>
                                <computer>%s</computer>
                                <domain>%s</domain>
                                <user>%s</user>
                                <gateway>%s</gateway>
                            </client-logout>
                        </global-protect-gateway>
                       </request>"""%(computer, domain, user, gateway))

    r = xml.find("response")
    status = r.attrib["status"]

    return status.lower() == "success"




if __name__ == "__main__":
    """ doesnt work for always on users...
    """
    for gw_name, portal in get_gp_gateways().items():
        print "processing gateway: %s"%gw_name
        for user in get_all_gp_users(gw_name):
            print "     kicking user %8s\%-8s :"%(user["domain"], user["username"]),


            # skip me :p
            if user["username"].lower() in SKIP:
                print "SKIP"
                continue

            st = kick_user(portal, user["username"], user["domain"], user["computer"])
            if st:
                print "OK"
            else:
                print "FAILED"
    
    
    
