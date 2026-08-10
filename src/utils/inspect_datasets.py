import os
from collections import Counter

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ROOTS = {
    'PESTAI': os.path.join(BASE, 'dataset', 'raw', 'pest'),
    'GRAPE': os.path.join(BASE, 'dataset', 'raw', 'disease'),
}

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff', '.webp'}

for name, root in ROOTS.items():
    print(f'=== {name} ===')
    print('root:', root)
    if not os.path.exists(root):
        print('MISSING ROOT')
        print()
        continue
    total_files = 0
    total_dirs = 0
    ext_counts = Counter()
    nonimg = []
    class_dirs = []
    has_annotation = False
    structure = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        structure.append((rel, sorted(dirnames), sorted(filenames)))
        if rel == '.':
            class_dirs.extend(sorted(dirnames))
        total_dirs += 1
        for fname in filenames:
            total_files += 1
            ext = os.path.splitext(fname)[1].lower()
            ext_counts[ext] += 1
            if ext not in IMG_EXTS:
                nonimg.append(os.path.join(rel, fname))
            if 'xml' in ext or 'csv' in ext or 'json' in ext or 'txt' in ext:
                has_annotation = True

    print('dirs:', total_dirs)
    print('files:', total_files)
    print('top-level class dirs:', class_dirs)
    print('ext counts:', dict(ext_counts))
    print('non-image files:', nonimg[:50])
    print('structure sample:')
    for rel, dirs, files in structure[:20]:
        print(' ', rel, 'dirs=', dirs, 'files=', len(files))
    print()
