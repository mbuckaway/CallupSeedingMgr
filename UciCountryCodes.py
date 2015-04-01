# -*- coding: utf-8 -*-

# from http://users.skynet.be/hermandw/if/ifcyc.html

uci_country_code_str = '''
AFG	Afghanistan	2007
AHO	Netherlands Antilles	x
ALB	Albania	x
ALG	Algeria	x
AND	Andorra	x
ANG	Angola	x
ANT	Antigua and Barbuda	x
ARG	Argentina	x
ARM	Armenia	x
ARU	Aruba	x
AUS	Australia	x
AUT	Austria	x
AZE	Azerbaijan	x
BAH	Bahamas	x
BAN	Bangladesh	x
BAR	Barbados	x
BDI	Burundi	x
BEL	Belgium	x
BEN	Benin	x
BER	Bermuda	x
BIH	Bosnia&Herzegovina	x
BIZ	Belize	x
BLR	Belarus	x
BOL	Bolivia	x
BRA	Brazil	x
BRN	Bahrain	x
BRU	Brunei Darussalam	x
BUL	Bulgaria	x
BUR	Burkina Faso	x
CAF	Central African Rep.	2007
CAM	Cambodia	2010
CAN	Canada	x
CAY	Cayman Islands	x
CGO	Congo, Rep.	2006
COD	Congo, Dem. Rep.	2010
CHI	Chile	x
CHN	China	x
CIV	Côte d'Ivoire	x
CMR	Cameroon	x
COL	Colombia	x
CRC	Costa Rica	x
CRO	Croatia	x
CUB	Cuba	x
CYP	Cyprus	x
CZE	Czech Republic	x
DEN	Denmark	x
DOM	Dominican Republic	x
ECU	Ecuador	x
EGY	Egypt	x
ERI	Eritrea	x
ESA	El Salvador	2
ESP	Spain	x
EST	Estonia	x
ETH	Ethiopia	x
FIJ	Fiji	x
FIN	Finland	x
FRA	France	x
GAB	Gabon	x
GAM	Gambia	2008
GBR	Great Britain	x
GEO	Georgia	x
GER	Germany	x
GHA	Ghana	2008
GRE	Greece	x
GRN	Grenada	2006
GUA	Guatemala	x
GUI	Guinea	2010
GUM	Guam	x
GUY	Guyana	x
HAI	Haiti	x
HKG	Hong Kong	x
HON	Honduras	x
HUN	Hungary	x
INA	Indonesia	x
IND	India	x
IRI	Iran	x
IRL	Ireland	
IRQ	Iraq	2006
ISR	Israel	x
ISV	Virgin Islands (US)	x
ITA	Italy	x
JAM	Jamaica	x
JOR	Jordan	x
JPN	Japan	x
KAZ	Kazakhstan	x
KEN	Kenya	x
KGZ	Kyrgyzstan	x
KOR	Korea, Republic	x
KSA	Saudi Arabia	x
KUW	Kuwait	x
LAO	Laos	x
LAT	Latvia	x
LBA	Libya	x
LCA	Saint Lucia	x
LES	Lesotho	2007
LIB	Lebanon	x
LIE	Liechtenstein	x
LTU	Lithuania	x
LUX	Luxembourg	x
MAC	Macao	x
MAD	Madagascar	x
MAR	Morocco	x
MAS	Malaysia	x
MAW	Malawi	2006
MDA	Moldova	x
MEX	Mexico	x
MGL	Mongolia	x
MKD	FYRO Macedonia	x
MLI	Mali	x
MLT	Malta	x
MNE	Montenegro	x
MON	Monaco	x
MRI	Mauritius	x
MYA	Myanmar	x
NAM	Namibia	x
NCA	Nicaragua	x
NED	Netherlands	x
NEP	Nepal	x
NGR	Nigeria	x
NOR	Norway	x
NZL	New Zealand	x
OMA	Oman	x
PAK	Pakistan	x
PAN	Panama	x
PAR	Paraguay	x
PER	Peru	2004
PHI	Philippines	x
POL	Poland	x
POR	Portugal	x
PRK	Korea, DPR	x
PUR	Puerto Rico	x
QAT	Qatar	2003
ROM	Romania	x
RSA	South Africa	x
RUS	Russia	x
RWA	Rwanda	2006
SEN	Senegal	x
SEY	Seychelles	x
SIN	Singapore	x
SKN	Saint Kitts and Nevis	
SLE	Sierra Leone	2006
SLO	Slovenia	x
SMR	San Marino	x
SOM	Somalia	2008
SRB	Serbia	x
SRI	Sri Lanka	x
STP	São Tomé & Príncipe	2007
SUD	Sudan	2003
SUI	Switzerland	x
SUR	Surinam	2004
SVK	Slovakia	x
SWE	Sweden	x
SYR	Syria	x
TAN	Tanzania	2010
THA	Thailand	x
TKM	Turkmenistan	x
TLS	Timor-Leste	2004
TOG	Togo	x
TPE	Chinese Taipei	x
TRI	Trinidad and Tobago	x
TUN	Tunisia	x
TUR	Turkey	x
UAE	United Arab Emirates	x
UGA	Uganda	x
UKR	Ukraine	x
URU	Uruguay	x
USA	United States America	x
UZB	Uzbekistan	x
VEN	Venezuela	x
VIE	Viet Nam	x
VIN	Saint Vincent	x
YEM	Yemen	x
ZAM	Zambia	x
ZIM	Zimbabwe	x
'''

uci_country_codes = {}
for line in uci_country_code_str.split('\n'):
	line = line.strip()
	if not line:
		continue
	fields = [f.strip() for f in line.split('\t')]
	try:
		uci_country_codes[unicode(fields[1], "utf-8")] = unicode(fields[0], "utf-8")
	except IndexError:
		pass
		
del uci_country_code_str
