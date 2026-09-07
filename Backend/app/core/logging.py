"""
هدف اینه که:

کاربر خطای داخلی و traceback نبینه.
خودمون در لاگ بفهمیم دقیقاً چه اتفاقی افتاده.
خطاهای 500 قابل پیگیری باشن.
بعداً در Docker هم لاگ‌ها رو راحت ببینیم.
"""

import logging
import sys


logger = logging.getLogger("kenko")

logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False