import nfc
from nfc.clf import RemoteTarget
from time import sleep

def Exit():
    print("device shutting down")
    exit()

def Scan():

    try:
        clf = nfc.ContactlessFrontend('usb')
    except:
        print("nfc device not connected")
        Exit()


    scanedUid = ""

    while scanedUid == "" or scanedUid == None:
        target = clf.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))

        
        
        if target is None:
            scanedUid = target
            sleep(0.25)
            continue

        tag = nfc.tag.activate(clf, target)

        print(tag)
        print(tag.ndef)
        
        scanedUid = target.sdd_res.hex()

        sleep(0.25)

    return scanedUid

def main():
    print("scanning...")

    studentID = Scan()

    print("sending: " + studentID)

    sleep(1)
    main()

main()