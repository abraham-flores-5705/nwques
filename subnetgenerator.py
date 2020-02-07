import random
from ipaddress import IPv4Address

# Minimum subnet mask size in bits
# Code will need to be refactored for a MIN_MASK_SIZE < 8 to work, so 8 is minimum
MIN_MASK_SIZE = 8
# Maximum subnet mask size in bits
# MAX_MASK_SIZE maximum is 30, the largest possible meaningful network in IPv4
MAX_MASK_SIZE = 24
# Amount of sub-hosts to generate
HOSTS_TO_GEN = 10

#
# Generates a random classless address NETWORK ONLY outside the reserved first octets
# and a random subnet mask from 8-24 bits
# Returns a single IPv4Address object that fits within the given network and subnet
#
def genclasslesssuper():
  # Do not use these numbers for the first octet
  reserved = [100, 127, 169, 198, 203, 224, 240]
  # Get a random subnet mask
  mask = random.randint(MIN_MASK_SIZE, MAX_MASK_SIZE)
  # Generate an amount of bits equal to the mask (the network portion)
  addrbits = random.getrandbits(mask)
  # If the first octet is in the reserved list, generate a new address
  # ERRORS IF MIN_MASK_SIZE < 8
  while((addrbits >> (mask - 8)) in reserved):
    addrbits = random.getrandbits(mask)
  # Append 0's to the end to pad the address to a full 32 bits
  addrbits = addrbits << (32 - mask)
  # Create an IPv4Address object from the bits
  addr = IPv4Address(addrbits)
  return addr, mask

#
# Generates a random usable host in a given network-only address and subnet mask
# Returns an IPv4Address within
#
def genclasslesssub(addr, mask):
  validaddr = False
  while(not validaddr):
    # Generate an amount of bits equal to the host portion of the address
    addrbits = random.getrandbits(32 - mask)
    # Append the host portion to the network portion and create an IPv4Address object from the result
    fulladdr = IPv4Address(int(addr) | addrbits)
    if(int(fulladdr) != calclast(addr, mask) and int(fulladdr) != calcfirst(addr, mask)):
      validaddr = True
  return fulladdr

#
# Calculates the greatest address from a given subnet and address
# Returns IPv4Address object that is last within the network and subnet mask
#
def calclast(addr, mask):
  # Get the integer value of the network portion of the address
  nw = int(addr) >> (32 - mask)
  # Replace the host bits with 1's to get the last address
  for i in range(32 - mask):
    nw = (nw << 1) + 1
  greatest = IPv4Address(nw)
  return greatest

#
# Calculates the least address from a given subnet and address
# Returns IPv4Address object that is first within the network and subnet mask
#
def calcfirst(addr, mask):
  # Get the integer value of the network portion of the address
  nw = int(addr) >> (32 - mask)
  # Replace the host bits with 0's to get the first address
  for i in range(32 - mask):
    nw = (nw << 1) + 0
  least = IPv4Address(nw)
  return least

#
# Generates a list of 10 random hosts in a given network-only address and subnet mask
# Returns a list of IPv4Adress objects that fit within the given network and subnet
#
def genclasslesssublist(addr, mask):
  outlist = []
  # Initialize list with random hosts
  for i in range(0, HOSTS_TO_GEN):
    outlist.append(genclasslesssub(addr, mask))
  # Generate lists of hosts until all are unique
  unique = False
  while(not unique):
    if(len(set(outlist)) == len(outlist)):
      unique = True
    else:
      for i in range(0, HOSTS_TO_GEN):
        outlist[i] = genclasslesssub(addr, mask)
  # Shuffle the list
  random.shuffle(outlist)
  return outlist

#
# Given a list of IPv4Address objects, determines the best-fit subnetmask for them
# Returns an integer CIDR that best describes the given list
#
def calcsnm(addrlist):
  full = 0xFFFFFFFF
  bestfit = full
  # Perform bitwise AND on all addresses in the list
  for ind in range(len(addrlist)):
    # Compare the current and next addresses
    if(ind == len(addrlist) - 1):
      continue
    addr1i = int(addrlist[ind])
    addr2i = int(addrlist[ind + 1])
    # XNOR the two addresses and store the result
    common = full - (addr1i ^ addr2i)
    # Compare it to previous results
    bestfit = bestfit & common
  # Find the first 0 from left to right in the bestfit
  cutoff = 0
  for ind,val in enumerate(str(bin(bestfit))[2::]):
    if(val == '0'):
      cutoff = ind
      break
  # Remove all trailing 0's
  bestfit = bestfit >> bestfit.bit_length() - cutoff
  # Count the remaining bits
  bestfit = bestfit.bit_length()
  return bestfit


with open("Summary.txt", 'w') as f:
  for i in range(1000):
    gensup = genclasslesssuper()
    subaddrs = genclasslesssublist(gensup[0], gensup[1])
    bestmask = calcsnm(subaddrs)
    f.write(str(i) + "\n" + "Super address: " + str(gensup[0]) + "/" + str(bestmask) + "\n")
    for host in subaddrs:
      f.write("\tSub address: " + str(host) + "\n")
    f.write("\n")
f.close()
