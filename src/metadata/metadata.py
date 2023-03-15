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
    '0': 'General Questions',
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
    'WCT': ['1', '3'],
    'WCAT': [],
    'WDC': ['4'],
    'WEC': [],
    'WFC': [],
    'WMT': [],
    'WQAC': [],
    'WRC': ['2', '7'],
    'WRT': [],
    'WST': ['5'],
    'WSOT': [],
    'WAT': []
}

# Columns that must be deleted for privacy and other reasons.
MUST_DELETE_COLUMNS = [
    'Respondent ID',
    'Collector ID',
    'Start Date',
    'End Date',
    'IP Address',
    'Email Address',
    'First Name',
    'Last Name',
    'Custom Data 1',
    'wca_token'
]

# String added by Pandas in blank column labels.
PANDAS_UNNAMED = 'Unnamed:'

# Questions to separate topics.
SEPARATOR_QUESTION = 'Would you like to leave your feedback on this topic?'
