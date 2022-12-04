# Auctus
A resource and warchest automation, production calculation, and auditing script for the MMO Politics &amp; War

Usage Instructions
1. Install Python https://www.python.org/downloads/
2. Open cmd.exe and use pip to install the dependences
      Example: pip install bs4
      Module dependences as of typing: requests, json, urllib.request, pickle, time, sys, os.path, math, copy, datetime, lxml, operator, bs4
3. Right click on auctus.py and click, "Edit with IDLE"
4. Configure settings and set variables as desired and needed
    a. banking_alliance_id, run_audit, brick_the_send, brick_resources_low, dump_to_offshore_global, offshore_name, API_key, alliance_mode, allianceid_apikey_pair_dict_list, allianceid_apikey_dict, taxid_list, allianceid_list, user_email, user_password, accept_applicants_as_programmees, headers, send_wc, WAR_maint_wc, PEACE_maint_WC, wc_money_mult, send_resource_multipler, send_food_and_uranium_buffer, food_and_uranium_multipler, top_off_mode, and trader_id_list
5. At the top of the IDLE window, click Run -> Run Module to start. Alternatively press the F5 key
6. If the script has set brick_resources_low to True, then it will be normal for it to crash if it doesn't have enough to send
7. I recommend not engaging this script wrecklessly and not starting it too close to a turn change as it will fail if it runs into a turn change
9. Give praise
