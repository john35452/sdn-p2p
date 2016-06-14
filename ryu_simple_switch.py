import sys
import os
os.system('ryu-manager ryu.app.simple_switch_13 --ofp-tcp-listen-port '+sys.argv[1])
