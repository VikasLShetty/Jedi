#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import random

graph_extern = {}

def admin1():
    pass
    #need to implement this as a seprate file


def find_shortest_path(graph,start,end,path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


def addFlowRules(net,path,controller):
    Flow_path=[]
    first_port=0
    last_port=0
    l=str(net.links[-2])
    switch_port=l.split('-')[1][3]
    first_port=switch_port
    l=str(net.links[-1])
    last_switch=l.split('-')[0]
    switch_port=l.split('-')[1][3]
    last_port=switch_port
    prev_port=first_port
    info('path:'+str(path)+'\n')

    for i in range(1,len(path)-2):
        for link in net.links:
            if ((path[i] in str(link)) and (path[i+1] in str(link))):
                switches=str(link).split('<->')
                if(switches[0].split('-')[0]==path[i]):
                    switch1=switches[0].split('-')[0]
                    switch2=switches[1].split('-')[0]
                    switch1_port=switches[0][-1]
                    switch2_port=switches[1][-1]
                else:
                    switch2=switches[0].split('-')[0]
                    switch1=switches[1].split('-')[0]
                    switch2_port=switches[0][-1]
                    switch1_port=switches[1][-1]
                info('link:'+str(link)+'\n')
                controller.cmd('ovs-ofctl add-flow '+switch1+' in_port='+prev_port+',actions=output:'+switch1_port)
                info('ovs-ofctl add-flow '+switch1+' in_port='+prev_port+',actions=output:'+switch1_port+'\n')
                controller.cmd('ovs-ofctl add-flow '+switch1+' in_port='+switch1_port+',actions=output:'+prev_port)
                info('ovs-ofctl add-flow '+switch1+' in_port='+switch1_port+',actions=output:'+prev_port+'\n')
                prev_port=switch2_port
                break

    controller.cmd('ovs-ofctl add-flow '+last_switch+' in_port='+prev_port+',actions=output:'+last_port)
    info('ovs-ofctl add-flow '+last_switch+' in_port='+prev_port+',actions=output:'+last_port+'\n')
    controller.cmd('ovs-ofctl add-flow '+last_switch+' in_port='+last_port+',actions=output:'+prev_port)
    info('ovs-ofctl add-flow '+last_switch+' in_port='+last_port+',actions=output:'+prev_port+'\n')

def simulateLinkFailure(path):
    global graph_extern
    k = random.randint(1,len(path)-3)
    graph_extern[path[k]].remove(path[k+1])
    graph_extern[path[k+1]].remove(path[k])



def myNetwork():
    bandwidths = [1,5,10,20,40]
    global graph_extern #mGlobal  view of adjacency list
    #hosts are actually switches here
      #no of switches
    hosts = 4
    mininetswitch = [0 for i in range(hosts+1)]
    host=[0 for i in range(hosts+1)]

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')


    for i in range(1,hosts+1):

        host[i]=i  #Data Structure used for maintaining the Global view of Hosts
        mininetswitch[i]= 's'+str(i)
        net.addSwitch('s'+str(i), cls=OVSKernelSwitch) #mininets view
    for i in range(hosts+1):
        graph_extern[mininetswitch[i]]=[]
    for i in range(1,hosts+1):
        for j in range(1,hosts+1):
            if(i!=j):
                k = random.randint(0,4)
                if(k > 1):
                    if mininetswitch[j] not in graph_extern[mininetswitch[i]]:
                        graph_extern[mininetswitch[i]].append(mininetswitch[j])
                        graph_extern[mininetswitch[j]].append(mininetswitch[i])
                        b = random.choice(bandwidths)
                        net.addLink(mininetswitch[i],mininetswitch[j],cls=TCLink,bw=b)


    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    src=mininetswitch[1]
    dest=mininetswitch[2]
    net.addLink(mininetswitch[1],h1)
    net.addLink(mininetswitch[2], h2)



    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
    for i in range(1, hosts+1):
        net.get('s'+str(i)).start([c0])
    info( '*** Starting switches\n')

    info( '*** Post configure switches and hosts\n')
    path=find_shortest_path(graph_extern,src,dest)
    path.insert(0,'h1')
    path.append('h2')
    #addFlowRules(net,path,c0)
    info('old_graph'+str(graph_extern)+'\n')
    info('old_path:'+str(path)+'\n')
    simulateLinkFailure(path)

    path.remove('h1')
    path.remove('h2')
    new_path=find_shortest_path(graph_extern,src,dest)
    new_path.insert(0,'h1')
    new_path.append('h2')
    info('new_graph'+str(graph_extern)+'\n')
    info('new_path'+str(new_path)+'\n')
    addFlowRules(net,new_path,c0)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
