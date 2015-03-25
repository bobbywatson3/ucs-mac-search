from UcsSdk import *
from UcsSdk.MoMeta.LsPower import LsPower
import re
import argparse
import getpass
from prettytable import PrettyTable

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac-address-wildcard', required=True, help="Wildcard match for any MAC addresses that contain this string")
parser.add_argument('-l', '--login', default='admin', help="Login for UCS Manager. Default is 'admin'.")
parser.add_argument('-p', '--password', help="Password for UCS Manager.")
parser.add_argument('-u', '--ucs', nargs='*', required=True, help="Hostname or IP address of UCS Manager") # TODO make this work with multiple UCS IP's

args = parser.parse_args()

mac_address_wildcard = args.mac_address_wildcard

def create_mac_sp_dict(ucs, login, password, mac):
        for attempt in range(3):
            try:
                handle = UcsHandle()
                print "Connecting to UCS at %s as %s." % (ucs, login)
                if not password:
                    password = getpass.getpass(prompt='UCS Password: ')
                handle.Login(ucs, login, password)
                output = []
                mo_dn_array = {}
                getRsp = handle.GetManagedObject(None, None,{"Dn":"org-root/"})
                moArr = handle.GetManagedObject(getRsp, "macpoolAddr")
                for mo in moArr:
                    origDn = str(mo.Dn)
                    if mac_address_wildcard.lower() in origDn.lower() and str(mo.Assigned) == "yes":
                        matches = {}
                        mac = str(mo.Id)
                        service_profile_and_vnic = str(mo.AssignedToDn)
                        service_profile_and_vnic = re.search(r'(?<=ls-)(\S*)', service_profile_and_vnic)
                        service_profile_and_vnic = service_profile_and_vnic.group().split("/ether-")
                        matches = {"UCS" : ucs, "service profile" : service_profile_and_vnic[0], "MAC address" : mac, "vNIC" : service_profile_and_vnic[1]}
                        output.append(matches)
                return output
                handle.Logout()
                break
            except Exception, err:
                if "Authentication failed" in str(err):
                    print 'Authentication failed.'
                    password = getpass.getpass(prompt='Please re-enter password for %s at UCS %s: ' % (login, ucs))
                else:
                    print "Exception:", str(err)
                    import traceback, sys
                    print '-' * 60
                    traceback.print_exc(file=sys.stdout)
                    print '-' * 60
matches = []
for ucs in args.ucs:
    matches.extend(create_mac_sp_dict(ucs, args.login, args.password, args.mac_address_wildcard))
mac_table = PrettyTable(["MAC Address", "vNIC", "Service Profile", "UCS IP"])
for match in matches:
    mac_table.add_row([match["MAC address"], match["vNIC"], match["service profile"], match["UCS"]])
mac_table.sortby = "MAC Address"
print mac_table
