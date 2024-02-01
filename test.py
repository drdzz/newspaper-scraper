import math

"""p = 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151

q = 531137992816767098689588206552468627329593117727031923199444138200403559860852242739162502265229285668889329486246501015346579337652707239409519978766587351943831270835393219031728127
"""
p = 11
q = 7
N = p * q

def keyGen(p,q):
    
    phi = (p - 1) * (q - 1)

    e = [i for i in range(phi-1, 1,-1) if math.gcd(i, phi) == 1] # este es el exponente, cogo el mas pequño entre lso dos numeros
    print("all e's",e)

    a = e[1]
    print("a",a)
    d = pow(a, -1, phi)
    pub_key = a
    priv_key = d

    return pub_key, priv_key

public, private = keyGen(p,q)

print("PUBLIC:",public, "PRIVATE:",private, "MODULUS:",N)
message = 75

encrypt = pow(message, public, N)
print("message:", message)
print("encryted:", encrypt)
decrypt = pow(encrypt,private,N)
print("decrupted",decrypt)