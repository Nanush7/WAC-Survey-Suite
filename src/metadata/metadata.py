"""
Survey metadata.
"""
# Topic codes.
# Add topics and edit codes as required.
TEAMS = {
    'BOARD': 'WCA Board',
    'WCT': 'WCA Communications Team',
    'WCAT': 'WCA Competition Announcement Team',
    'WDC': 'WCA Disciplinary Committee',
    'WEC': 'WCA Ethics Committee',
    'WFC': 'WCA Financial Committee',
    'WMT': 'WCA Marketing Committee',
    'WQAC': 'WCA Quality Assurance Committee',
    'WRC': 'WCA Regulations Committee',
    'WRT': 'WCA Results Team',
    'WST': 'WCA Software',
    'WSOT': 'WCA Sports Organization Team',
    'WAT': 'WCA Archive Team'
}
TOPIC_CODES = {
    '0': 'All',
    '1': 'Communication and Transparency',
    '2': 'Regulations and Events',
    '7': 'Incidents and Future Regulations',
    '4': 'Disciplinary',
    '3': 'Website',
    '5': 'Software',
    '6': 'Other Comments',
}

# Default relevant topic codes for each team/committee.
# WEAT and WAC excluded.
TEAM_DEFAULT_INTEREST = {
    'BOARD': [],
    'WCT': ['1'],
    'WCAT': [],
    'WDC': ['4'],
    'WEC': [],
    'WFC': [],
    'WMT': [],
    'WQAC': [],
    'WRC': ['2', '7'],
    'WRT': [],
    'WST': ['3', '5'],
    'WSOT': [],
    'WAT': []
}
