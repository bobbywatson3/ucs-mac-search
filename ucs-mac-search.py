from UcsSdk import *
from UcsSdk.MoMeta.LsPower import LsPower
import re
import argparse
import getpass


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac-address-wildcard', required=True, help="Wildcard match for any MAC addresses that contain this string")
parser.add_argument('-l', '--login', default='admin', help="Login for UCS Manager. Default is 'admin'.")
parser.add_argument('-p', '--password', help="Password for UCS Manager.")
parser.add_argument('-u', '--ucs', nargs='*', required=True, help="Hostname or IP address of UCS Manager") # TODO make this work with multiple UCS IP's

args = parser.parse_args()

mac_address_wildcard = args.mac_address_wildcard

for ucs in args.ucs:
    try:
        handle = UcsHandle()
        if not args.password:
            args.password = getpass.getpass(prompt='UCS Password: ')
        handle.Login(ucs, args.login, args.password)

        service_profiles = []
        mo_dn_array = {}
        getRsp = handle.GetManagedObject(None, None,{"Dn":"org-root/"})
        moArr = handle.GetManagedObject(getRsp, "macpoolAddr")
        for mo in moArr:
            origDn = str(mo.Dn)
            if mac_address_wildcard.lower() in origDn.lower():
                mac = str(mo.Id)
                service_profile_and_vnic = str(mo.AssignedToDn)
                service_profile_and_vnic = re.search(r'(?<=ls-)(\S*)', service_profile_and_vnic)
                service_profile_and_vnic = service_profile_and_vnic.group().split("/ether-")
                print "MAC address" , mac , "is in use by" , service_profile_and_vnic[0] , "on port" , service_profile_and_vnic[1] + "."

        handle.Logout()
    except Exception, err:
        print "Exception:", str(err)
        import traceback, sys
        print '-' * 60
        traceback.print_exc(file=sys.stdout)
        print '-' * 60

