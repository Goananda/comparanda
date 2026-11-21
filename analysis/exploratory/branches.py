"""Exploratory: does a given set of traditions form a branch of the consensus tree?
Usage: python3 branches.py <work_dir>
For each set the script finds the branch that matches it best (F1 of membership) and lists what is missing or extra.
"""
import sys, numpy as np, pandas as pd
out = sys.argv[1]
G = pd.read_csv(f'{out}/groups.csv'); kg = np.load(f'{out}/keep_g.npy'); L = np.load(f'{out}/ward.npy')
Gk = G[kg].reset_index(drop=True); N = len(Gk); names = Gk.group.tolist(); pos = {g: i for i, g in enumerate(names)}
mem = {i: frozenset([i]) for i in range(N)}
for j, (a, b, h, n) in enumerate(L): mem[N + j] = mem[int(a)] | mem[int(b)]
def has(*keys): return [g for g in names if any(k in g for k in keys)]
SETS = {
 'ancient written traditions': ['Sumer', 'Akkad,Assyria,Babylon', 'Ancient Egypt', 'Hittite, Hurrit', 'Ugarit, Phoenicia', 'Ancient Greece', 'Old Testament', 'Ancient Italy', 'Avesta; Pekhlevi texts', 'Ancient China', 'India, literary sources', 'Scandinavians: early written sources'],
 'Australia': ['Arnham Land', 'Central Australia', 'Kimberley Plateau', 'Queensland', 'SE Australia', 'Southern Australia', 'Western Australia'],
 'Chaco': ['Mataco', 'Toba', 'Chorote', 'Nivakle', 'Maka', 'Chamacoco', 'Ayoreo', 'Mocovi', 'Lengua,Sanapana,Angaite', 'Caduveo', 'Tereno', 'Chiriguano'],
 'Ge of central Brazil': has('Kayapo', 'Apinaye', 'Canela', 'Craho', 'Krah', 'Sherente', 'Shavante', 'Suya', 'Crenye', 'Timbira'),
 'Central Andes': has('Peru', 'dep.', 'Aimara', 'Kechua', 'Chipaya'),
 'Inuit of Canada and Greenland': has('Greenland', 'Polar Eskimo', 'Baffin', 'Labrador Eskimo', 'Iglulik', 'Netsilik', 'Caribou', 'Copper Eskimo', 'Mackenzie'),
 'Polynesia and Micronesia': ['Samoa', 'Tonga', 'Hawaii', 'Maori,Moriori', 'Tahiti, Society islands', 'Marquesas', 'Tuamotu', 'Mangareva', 'Cook Islands southern', 'Niue', 'Tokelau', 'Tuvalu (Ellice)', 'Rotuma', 'Kapingamarangi', 'Gilbert,Nauru,Banaba', 'Marshal Islands', 'Ponape district', 'Truk district', 'Yap', 'Palau', 'Ulithi, Ngulu', 'Ifaluk, Lamotrek, Satawal', 'Rennel,Tikopia,Bellona,Futuna(Erronan)', 'Ontong Java,Takuu,Nukumanu,Nukuria'],
 'New Guinea': ['Sepik-Ramu Papuans', 'Torricelli Papuans', 'Trans New Guinea East', 'Trans New Guinea West', 'North New Guinea Melanesians', 'SE New Guinea Melanesians', 'Massim district', 'Torres Strait Islands', 'Buka, Bougenville'],
 'Turkic and Mongolic peoples of South Siberia and Mongolia': ['Altai-Kiji, Telengit', 'Khakas', 'Shor', 'Tofa', 'Tuvinians', 'Tuvinians South Altai', 'Kumandin,Chelkan,Tubalar', 'Chulym Turks', 'Buryat', 'Mongols (Khalkha)', 'Mongols (Inner Mongolia)', 'Oirat', 'Darkhad', 'Kalmyk', 'Daghur'],
 'Indo-Aryan and Dravidian South Asia': ['Hindi, Chhattisgarhi', 'Bengali', 'Marathi', 'Tamil', 'Punjabi', 'Sinhalese', 'Gujarati', 'Oriya', 'Assamese', 'Kashmiri', 'Rajasthani', 'Sindhi', 'Telugu, Chenchu', 'Kannada; Kuruba', 'Malayali; Kannikaran', 'Konkani', 'Nepali; Tharu', 'Kumaoni (Central Pahari)', 'Himachali (Western Pahari)'],
 'Horn of Africa': ['Amhara', 'Tigre, Tigrigna', 'Somali', 'Saho, Afar', 'Bilin'],
 'Mesoamerica (Maya)': has('Tzotzil', 'Tseltal', 'Chol', 'Chorti', 'Yucatec', 'Lacandon', 'Quiche', 'Tzutujil', 'Mam, Ixil', 'Kanjobal', 'Kekchi', 'Huastec'),
 'African foragers': ['Bushmen', 'Hadza', 'Mbuti & Efe Pigmies'],
 'Tierra del Fuego and Patagonia': has('Selknam', 'Yamana', 'Alakaluf', 'Tehuelche', 'Mapuche'),
 'Tibet': has('Tibetans'),
 'Japan, Korea, China': ['Japan', 'Korea', 'Chinese folklore', 'Northern Ryukyu; Awami Islands'],
 'Baltic Finns and Balts': has('Estonians', 'Finns', 'Karelians', 'Vepsians', 'Livonians', 'Setu', 'Wotians', 'Latvians', 'Lithuanians'),
}
for label, S in SETS.items():
    S = frozenset(pos[g] for g in S if g in pos)
    if not S: print(f'{label}: no traditions found'); continue
    best = max(mem, key=lambda j: 2 * len(S & mem[j]) / (len(S) + len(mem[j])))
    b = mem[best]; f1 = 2 * len(S & b) / (len(S) + len(b))
    miss = [names[i] for i in S - b]; extra = [names[i] for i in b - S]
    print(f'{label}: set {len(S)}, best branch {len(b)}, F1 {f1:.2f}' + (f' | outside: {"; ".join(miss[:8])}' if miss else '') + (f' | also in the branch: {"; ".join(extra[:12])}' + (' ...' if len(extra) > 12 else '') if extra else ''))
