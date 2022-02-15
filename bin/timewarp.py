import click
from datetime import datetime, timedelta
from lxml import etree
import sys
import os


def warp_file(fh, days):
    """Given open file handle, move all date values w/i forward by `days`"""
    if days < 0:
        print(f"warping {fh.name} {-1 * days} days back...")
    else:
        print(f"warping {fh.name} {days} days forward...")

    tree = etree.parse(fh)

    def bump_date(dt):
        moment = datetime.strptime(dt, "%Y-%m-%d")
        moment += timedelta(days=days)
        return moment.strftime("%Y-%m-%d")

    meds = "//Message/Body/RxHistoryResponse/MedicationDispensed"
    for med in tree.xpath(meds):
        for elem in med.xpath("WrittenDate/Date"):
            elem.text = bump_date(elem.text)
        for elem in med.xpath("LastFillDate/Date"):
            elem.text = bump_date(elem.text)

    # Return tree root for writing
    return etree.ElementTree(tree.getroot())


@click.command()
@click.option('--days', default=0, help="number of days to warp into the future (use negative value to move back)")
@click.option('--source', default=None, help="option to name single source file to time-warp")
@click.option('--dir', default="20170701", help="option to name source directory, defaults to '20170701'")
def timewarp(days, source, dir):
    """Time warp all files in dir by given number of days, write inplace"""
    if source:
        def single_file_gen():
            yield source
        file_gen = single_file_gen
    else:
        def multi_file_gen():
            for item in os.scandir(dir):
                fp = os.path.join(dir, item.name)
                if not os.path.isfile(fp):
                    continue
                yield fp
        file_gen = multi_file_gen

    for source_file in file_gen():
        try:
            with open(file=source_file, mode='r') as src:
                bumped_contents = warp_file(src, days)
            bumped_contents.write(source_file, pretty_print=True)
        except etree.XMLSyntaxError as err:
            print(f"ERROR can't parse XML in {source_file}", file=sys.stderr)






if __name__ == '__main__':
    timewarp()
