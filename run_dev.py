import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
PACKAGE_PATH = SRC_DIR / "openchj-annotator"

sys.path.insert(0, str(PACKAGE_PATH))

os.environ["OPENCHJ_PROJECT_ROOT"] = str(PROJECT_ROOT)

# import after sys.path modification
from utils import path_manager  # noqa: E402

path_manager.initialize_paths(str(PROJECT_ROOT))

# import after path_manager initialization
from main import main  # noqa: E402

main()
