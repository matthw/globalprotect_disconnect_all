# globalprotect_disconnect_all
disconnect all Palo Alto Globalprotect users
2021 - Matthieu Walter

quick and dirty but it works.
just edit the file to fill in the firewall mgt ip, the api key and a list of users you do not want to disconnect (like yourself if you are running this script remotely).

it will go over the gateways and disconnect people.
i think it fails with pre-logon users.
