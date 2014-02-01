from os import system
import sys


def wait():
    print 'Press enter when ready to continue.'
    print '(or abort with Ctrl+c)'
    raw_input()


def get_mounts():
    system('df -h > mounts.txt')
    with open('mounts.txt') as mounts_file:
        mounts = mounts_file.readlines()

    return [line.split()[0] for line in mounts]


def find_prefix(elements):
    min_len = min(len(x) for x in elements)
    for i in range(min_len):
        letters = set(x[i] for x in elements)
        if len(letters) > 1:
            return elements[0][:i]

    return elements[0][0:min_len]


def create_sd(image_path):
    print 'Step 1 of 4'
    print '-----------'

    print 'Please make sure the SD card is *not* inserted on your machine.'
    print 'If it is, please *remove* it.'
    wait()
    mounts_before = get_mounts()

    print 'Step 2 of 4'
    print '-----------'

    print 'Now insert the SD card, and continue when linux has detected it.'
    wait()
    mounts_after = get_mounts()

    new_mounts = set(mounts_after) - set(mounts_before)

    if not new_mounts:
        print "Couldn't detect the SD card partitions."
        sys.exit()

    print 'Step 3 of 4'
    print '-----------'

    print 'Will umount the SD card partitions:'
    print '\n'.join(new_mounts)
    wait()

    for device in new_mounts:
        system('sudo umount ' + device)

    sd_device = find_prefix(list(new_mounts))
    if sd_device.endswith('p'):
        sd_device = sd_device[:-1]

    print 'Step 4 of 4'
    print '-----------'

    write_command = 'sudo dd bs=4M if=%s of=%s' % (image_path, sd_device)

    print 'Will write the image to the SD card in this device:'
    print sd_device
    print 'Using this command:'
    print write_command
    print 'WARNING: this is dangerous, continue only if you are sure about this.'
    wait()
    print "Writting... please don't remove the SD card."
    system(write_command)
    system('sudo sync')

    print 'Done! Your SD card is ready.'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python picarder.py IMAGE_FILE'
        sys.exit()

    image_path = sys.argv[1]
    create_sd(image_path)
