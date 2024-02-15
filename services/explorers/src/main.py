import logging
import os
import sys

import uvicorn

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    uvicorn.run("app.app:app", port=8000, reload=False, access_log=True, host='0.0.0.0',
                workers=int(os.getenv('NUM_WORKERS', '5')))
