import os
import tempfile


temp_dir = os.path.join(tempfile.gettempdir(), "ripper")
os.rmdir(temp_dir)