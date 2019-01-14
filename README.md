# CENG435-TermProject2
CENG435 - Data Communications and Networking Term Project 2

## Authors
Fatih DEVELİ 2330892  
Resul ÇİFTÇİ 1942598  
Group 3

## Getting Started

The source files should be sent to related virtual machines.


### Setting up the virtual machines

Send the source files to related virtual machines.

s.py -------> s  
b.py -------> b  
d.py -------> d  


## Deployment

To run the system, python scripts on source, broker and destination nodes should be executed.

```
$ python b.py
```

s.py must be run only if both other scripts are already running. Running order of other
scripts is not important.

### Running the tests
tc/netem commands are used to apply various conditions to the system. The commands are
applied to the links between broker and destination.

If the command is run for the first time on an interface, "add" version should be used, 
otherwise "add" must be replaced with "change".

#### Experiment 1

To apply loss of packets to network, following commands are used in broker and destination before running the scripts:
```
# tc qdisc add dev eth1 root netem loss 0.5% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc add dev eth2 root netem loss 0.5% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
```

```
# tc qdisc change dev eth1 root netem loss 10% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc change dev eth2 root netem loss 10% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
```

```
# tc qdisc change dev eth1 root netem loss 20% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc change dev eth2 root netem loss 20% corrupt 0% duplicate 0% delay 3ms reorder 0% 0%
```

#### Experiment 2

To apply corruption of packets to the network, following commands are used in broker and destination before running the scripts:

```
# tc qdisc change dev eth1 root netem loss 0% corrupt 0.2% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc change dev eth2 root netem loss 0% corrupt 0.2% duplicate 0% delay 3ms reorder 0% 0%
```

```
# tc qdisc change dev eth1 root netem loss 0% corrupt 10% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc change dev eth2 root netem loss 0% corrupt 10% duplicate 0% delay 3ms reorder 0% 0%
```

```
# tc qdisc change dev eth1 root netem loss 0% corrupt 20% duplicate 0% delay 3ms reorder 0% 0%
# tc qdisc change dev eth2 root netem loss 0% corrupt 20% duplicate 0% delay 3ms reorder 0% 0%
```

#### Experiment 3
To apply reordering of packets to the network, following commands are used in broker and destination before running the scripts:
```
# tc qdisc change dev eth1 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 1% 50%
# tc qdisc change dev eth2 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 1% 50%
```

```
# tc qdisc change dev eth1 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 10% 50%
# tc qdisc change dev eth2 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 10% 50%
```

```
# tc qdisc change dev eth1 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 35% 50%
# tc qdisc change dev eth2 root netem loss 0% corrupt 0% duplicate 0% delay 3ms reorder 35% 50%
```

