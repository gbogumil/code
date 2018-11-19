import logging as log

class Primes:
    def __init__(self):
        try:
            file = open('primes.bin', 'r')
            self._primes = file.read()
            close(file)
        except:
            self._primes = []
            
    def save(self):
        file = open('primes.bin', 'w')
        file.write(self._primes)
        close(file)
    
    def findPrimes(self, value):


    def isPrime(self, value):
        foundNewPrime=False
        if self._primes[-1]**2 < value:
            for (p in findPrimes(self, value)):
                pass

        for i in range(len(self._primes)):
            if float(value)/self._primes[i] == int(value/self._primes[i]):
                return False
        return true

    def upTo(self, value):
        if (self._primes[-1] <= value):
            for (i in range(len(self._primes))):
                yield self._primes[i]
        else:
            for (p in findPrimes(self, value):
                yield p
