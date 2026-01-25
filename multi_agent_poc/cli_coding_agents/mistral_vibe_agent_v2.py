#!/usr/bin/env python3
import sys
if len(sys.argv) == 3 and sys.argv[1] == "refactor":
    print("#!/usr/bin/env python3
# Generated agent code")
else:
    sys.exit(1)
