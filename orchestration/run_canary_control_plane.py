import os, sys, importlib
os.environ['RICK_MODE'] = 'CANARY'
from orchestration.monkey_patch_gateway import activate
activate()
# choose default engine if none supplied
target = (sys.argv[1] if len(sys.argv)>1 else 'canary_trading_engine').replace('.py','')
try:
    mod = importlib.import_module(target)
    # try common main entry
    if hasattr(mod,'main'): mod.main()
    elif hasattr(mod,'run'): mod.run()
    else: print(f"[INFO] Imported {target}; no main() or run() found.")
except Exception as e:
    print(f"[ERROR] Engine import/run failed: {e}")
    raise
