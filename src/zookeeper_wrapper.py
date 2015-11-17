"""
Use this file to maintain and develop ZooKeeper specific functionality
"""

import sys
import logging
from kazoo.client import KazooClient

from singleton import *

class ZooKeeperWraper(object):
    def startLogging(self):
        # If the application is not making using of logging then Kazoo
        # throws an error message - No handlers could be found for logger "kazoo.client"
        # In order to avoid this we use this basic recipe
        logging.basicConfig()

    def createZooKeeperClient(self):
        zk = KazooClient(HOST_PORT_COMBO)
        return zk

    def startOperation(self, zk):
        zk.start()

    def stopOperation(self, zk):
        zk.stop()

    def callEnsurePath(self, zk, path):
        zk.ensure_path(path)

    def callCreatePath(self, zk, path, value="", ephemeral=False, makepath=False):
        zk.create(path, value=value, ephemeral=ephemeral, makepath=makepath)

    def checkIfNodeExists(self, zk, node):
        if zk.exists(node):
            return True
        else:
            return False

    def getNodeData(self, zk, node):
        data, stat = zk.get(node)
        return (data, stat)

    def setNodeData(self, zk, node, data):
        zk.set(node, data)

    def deleteNodes(self, zk, node, recursive=True):
        zk.delete(node, recursive=recursive)

def implementHostLocking(host_name="h1"):
    # - Create the helper object first and then call the startLogging method
    helper = ZooKeeperWraper()
    helper.startLogging()

    # - Create the Kazoo instance. Used for the next set of steps
    zk = helper.createZooKeeperClient()

    # - Start the Kazoo instance
    helper.startOperation(zk)

    # - Get the path from the Singleton on which the Locking needs to be done
    if not helper.checkIfNodeExists(zk, LOCK_PATH):
        helper.callCreatePath(zk, LOCK_PATH, makepath=True)

    # - Acquire the Lock
    lock = zk.Lock(LOCK_PATH, host_name)
    with lock:
        print("%s acquired the lock" % host_name)
        print("Temporarily importing time module and sleeping for 600 seconds")
        print("Instead of the sleep we will need to add the switch intelligence layer code here")
        import time
        time.sleep(600)
        zk.release()
        print("Releasing the lock")

    # - Stop the Kazoo instance at the very end
    helper.stopOperation(zk)

if __name__ == '__main__':
    host_name = sys.argv[1]
    implementHostLocking(host_name)