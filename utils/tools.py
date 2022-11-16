import os
import zipfile


def get_base_name(local_file):
    """Get file basename."""
    if os.path.isfile(local_file):
        basename = os.path.basename(local_file)
        return basename


def no_ext(basename):
    return os.path.splitext(basename)[0]


# EXTRACT COVER
def extract_cover(arc_name, index=0):
    """Extract 1st jpg found in archive (zip or cbz)."""
    with zipfile.ZipFile(arc_name, 'r') as zf:
        img_list = zf.namelist()
        jpg_list = [i for i in img_list if (
            i.endswith(".jpg") or i.endswith(".jpeg"))]
        jpg_list.sort()
        cover = jpg_list[index]  # extracts 1st jpeg for cover (1 for variant)
        file_data = zf.read(cover)
    with open(os.path.basename(cover), "wb") as fout:
        fout.write(file_data)

    return os.path.basename(cover)
