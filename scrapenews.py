import lavanguardiascraper as ls
import theguardianscraper as gs

diarios = ['https://www.theguardian.com/', 'https://www.lavanguardia.com/','https://www.elperiodico.com/']
for diario in diarios:
    if "theguardian" in diario:
        print(diario)
        gs.run()
    elif "lavanguardia" in diario:
        print(diario)
        ls.run()
    elif "elperiodico" in diario:
        print(diario)
        