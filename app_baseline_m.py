import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import os
from dotenv import load_dotenv
from utils.model_utils import  load_ml_model, preprocess_input, make_prediction

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Startup Success Predictor",
    page_icon="🚀",
    layout="wide"
)

load_dotenv()

API_URL = "http://localhost:8000/predict"  # swap in real URL later
HF_TOKEN = os.getenv("HF_TOKEN")

# RENAME keuwords as INDUSTRIES,  countries as COUNTRIES, states as STATES 🚨

keywords = ['Media', 'Application Platforms', 'Apps', 'Curated Web',
        'Software', 'Games', 'Biotechnology', 'Analytics', 'Mobile',
        'E-Commerce', 'Entertainment', 'Networking', 'Health and Wellness',
        'Internet Marketing', 'Education', 'Search', 'Art', 'Beauty',
        'Local Businesses', 'Cosmetics', 'Hospitality', 'Health Care',
        'Advertising', 'Coffee', 'Enterprise Software', 'Batteries', 'iOS',
        'Fashion', 'EdTech', 'Social Travel', 'Sports', 'Real Estate',
        'Audio', 'Health Diagnostics', 'unknown', 'Internet',
        'Local Search', 'Service Providers', 'Publishing',
        'Consumer Goods', 'Manufacturing', 'Augmented Reality', 'Finance',
        'Design', 'Public Transportation', 'Travel', 'Baby Accessories',
        'Designers', 'Cars', 'Clean Technology', 'Content', 'Chat',
        'Cloud Computing', 'Geospatial', 'Music Services', 'Doctors',
        'Social Media', 'Non Profit', 'Fitness', 'Landscaping',
        'Financial Services', 'Consumers', 'Digital Media', 'News',
        'Technology', 'Delivery', 'Big Data', 'Android',
        'Blogging Platforms', 'Customer Service', 'Hardware + Software',
        'Computers', 'Artificial Intelligence', 'Services', 'DIY',
        'Presentations', 'Ad Targeting', 'Credit Cards', 'Discounts',
        'Internet of Things', 'Cloud Infrastructure', 'SaaS', 'Messaging',
        'Collaboration', 'Interior Design', 'Energy', 'Transportation',
        'FinTech', 'Information Technology', 'Consumer Electronics',
        'Communities', 'Data Centers', 'Point of Sale', 'Enterprises',
        'Bitcoin', 'Project Management', 'Business Services', 'Babies',
        '3D', '3D Technology', 'Photography', '3D Printing', 'Alumni',
        'Drones', 'Automotive', 'Printing', 'Creative', 'Automated Kiosk',
        'Business Analytics', 'Music', 'Semiconductors', 'Web Hosting',
        'Cloud Data Services', 'Consulting', 'Game', 'Developer APIs',
        'App Marketing', 'Physical Security', 'Coupons', 'Security',
        'Databases', 'Flash Storage', 'Animal Feed', 'Creative Industries',
        'Machine Learning', 'Crowdfunding', 'Commercial Real Estate',
        'Online Travel', 'Web Design', 'Anything Capital Intensive',
        'Human Resources', 'Office Space', 'Pets', 'Aerospace',
        'Online Shopping', 'Distribution', 'Carbon', 'Career Management',
        'Leisure', 'Consumer Internet', 'Video', 'Food Processing',
        'Healthcare Services', 'Startups', 'Sales and Marketing',
        'Accounting', 'Browser Extensions', 'Information Services',
        'Concentrated Solar Power', 'B2B', 'Nanotechnology',
        'Social Network Media', 'Development Platforms', 'Bicycles',
        'Content Creators', 'Broadcasting', 'Brand Marketing',
        'Finance Technology', 'Home Decor', 'Crowdsourcing',
        'Digital Entertainment', 'Exercise', 'Contact Centers',
        'E-Commerce Platforms', 'SEO', 'Chemicals',
        'Innovation Engineering', 'Travel & Tourism', 'Limousines',
        'Hardware', 'Charity', 'Online Rental', 'Telecommunications',
        'Health Care Information Technology', 'Health and Insurance',
        'Oil & Gas', 'Audiobooks', 'Communications Infrastructure',
        'Distributors', 'Medical', 'Employment', 'M2M', 'Local',
        'Home Automation', 'Contact Management', 'Information Security',
        'Electrical Distribution', 'Content Discovery', 'All Students',
        'Engineering Firms', 'Events', 'Diagnostics',
        'Government Innovation', 'Pharmaceuticals', 'Clean Energy',
        'Logistics', 'Domains', 'Payments', 'Nonprofits',
        'Homeland Security', 'Big Data Analytics', 'Credit', 'Colleges',
        'Medical Devices', 'Construction', 'Internet Radio Market',
        'Legal', 'Public Relations', 'Self Development',
        'Employer Benefits Programs', 'Internet Service Providers',
        'Agriculture', 'Advertising Platforms', 'CRM', 'Data Integration',
        'Politics', 'Collectibles', 'Application Performance Monitoring',
        'Facebook Applications', 'Email', 'Real Time',
        'Comparison Shopping', 'Electronics', 'Mobile Security',
        'Cloud Management', 'Intellectual Property',
        'Marketing Automation', 'Material Science', 'Bio-Pharm',
        'Business Intelligence', 'Assisitive Technology', 'Auctions',
        'Child Care', 'Enterprise Search', 'Classifieds',
        'Content Delivery', 'Business Development', 'DOD/Military',
        'Archiving', 'Advice', 'Digital Signage', 'Industrial',
        'Advertising Exchanges', 'Cause Marketing',
        'Performance Marketing', 'Governments', 'Advanced Materials',
        'Renewable Energies', 'Human Resource Automation',
        'Adventure Travel', 'Insurance', 'Law Enforcement',
        'Advertising Networks', 'Brokers',
        'Embedded Hardware and Software', 'Gps', 'Direct Sales',
        'Robotics', 'Corporate Training', 'Furniture', 'Consumer Lending',
        'Ediscovery', 'Bridging Online and Offline', 'Marketplaces',
        'Brewing', 'Commodities', 'Online Scheduling',
        'Reviews and Recommendations', 'Gift Card',
        'Industrial Automation', 'Lasers', 'Weddings', 'Farming',
        'Tracking', 'Lifestyle', 'Developer Tools', 'Hotels', 'Algorithms',
        'Biomass Power Generation', 'Content Syndication',
        'Location Based Services', 'Loyalty Programs',
        'Business Productivity', 'Personalization', 'Match-Making',
        'Interface Design', 'iPhone', 'Retail', 'Banking',
        'Innovation Management', 'Console Gaming', 'Mining Technologies',
        'Hospitals', 'Risk Management', 'Network Security', 'Data Mining',
        'Craft Beer', 'Cloud Security', 'Charter Schools', 'Architecture',
        'Document Management', 'Consumer Behavior', 'Defense', 'Maps',
        'Specialty Chemicals', 'iPad', 'Journalism',
        'Communications Hardware', 'Fantasy Sports', 'Social Commerce',
        'Investment Management', 'BPO Services', 'Language Learning',
        'Boating Industry', 'Gambling', 'Active Lifestyle', 'Watch',
        'Wine And Spirits', 'Cannabis', 'Dietary Supplements', 'Cooking',
        'Estimation and Quoting', 'Environmental Innovation', 'Graphics',
        'Small and Medium Businesses', 'Electric Vehicles',
        'Specialty Foods', 'Restaurants', 'Kids', 'Energy Management',
        'Waste Management', 'Sensors', 'Fleet Management',
        'Commercial Solar', 'Energy Efficiency', 'Biometrics',
        'Recruiting', 'Incubators', 'Corporate Wellness', 'Angels',
        'Bioinformatics', 'Online Dating', 'Identity',
        'Collaborative Consumption', 'Email Marketing', 'VoIP', 'Biofuels',
        'Gold', 'Reputation', 'Film Production', 'Property Management',
        'Ticketing', 'Wireless', 'Enterprise Security',
        'Alternative Medicine', 'Real Estate Investors',
        'Social Fundraising', 'App Discovery', 'Productivity Software',
        'App Stores', 'Meeting Software', 'Entrepreneur', 'Opinions',
        'Cyber Security', 'Social Television', 'All Markets',
        'Corporate IT', 'Dental', 'Enterprise Application', 'Aquaculture',
        'Water', 'Billing', 'Fraud Detection', 'Gamification', 'CAD',
        'Therapeutics', 'Photo Sharing', 'Data Security',
        'Local Based Services', 'Data Privacy', 'Social Business',
        'Artists Globally', 'Fuels', 'Diabetes', 'Oil and Gas',
        'Intelligent Systems', 'Logistics Company', 'English-Speaking',
        'College Campuses', 'Intellectual Asset Management', 'Simulation',
        'Casual Games', 'Event Management', 'Educational Games',
        'Sporting Goods', 'Guides', 'Licensing', 'Film', 'Charities',
        'Identity Management', 'Home & Garden', 'Lead Generation',
        'Lead Management', 'Auto', 'Sales Automation',
        'Certification Test', 'Heavy Industry', 'Private School',
        'Minerals', 'Infrastructure', 'Entertainment Industry',
        'Public Safety', 'Life Sciences', 'IT Management', 'Open Source',
        'Mobile Software Tools', 'File Sharing', 'Mobile Commerce',
        'Families', 'Social Media Platforms', 'Lifestyle Products', 'ICT',
        'Custom Retail', 'Venture Capital', 'Clinical Trials',
        'Musical Instruments', 'Market Research', 'Wholesale', 'SNS',
        'Navigation', 'Video Games', 'Freelancers',
        'Deep Information Technology', 'Private Social Networking',
        'Career Planning', 'Internet Infrastructure', 'Organic Food',
        'Low Bid Auctions', 'Coworking', 'E-Books', 'Mobile Games',
        'Celebrity', 'Local Advertising', 'Realtors', 'Mobility',
        'FreetoPlay Gaming', 'Building Products', 'Customer Support Tools',
        'Genetic Testing', 'College Recruiting', 'Cyber',
        'Emerging Markets', 'Toys', 'Outsourcing',
        'General Public Worldwide', 'Gadget', 'Professional Services',
        'Service Industries', 'Direct Marketing', 'Groceries',
        'IT and Cybersecurity', 'Generation Y-Z', 'Outdoors', 'Fruit',
        'New Technologies', 'Recreation', 'Mobile Social', 'Shopping',
        'Social Bookmarking', 'EBooks', 'Comics', 'Image Recognition',
        'Non-Tech', 'Product Development Services', 'K-12 Education',
        'Spas', 'Soccer', 'Lifestyle Businesses', 'Mass Customization',
        'Product Design', 'Assisted Living', 'Wearables', 'Social News',
        'Rental Housing', 'Flash Sales', 'Mobile Payments', 'Trading',
        'Digital Rights Management', 'Staffing Firms',
        'Optical Communications', 'EDA Tools', 'Parking', 'Linux',
        'Energy Storage', 'Data Visualization', 'Elder Care',
        'Electronic Health Records', 'Baby Boomers', 'Cable',
        'Enterprise Hardware', 'Social Media Advertising',
        'Personal Finance', 'Video Streaming', 'Darknet',
        'Online Identity', 'Knowledge Management',
        'Business Information Systems', 'New Product Development',
        'Computer Vision', 'Health Services Industry', 'Email Newsletters',
        'Utilities', 'China Internet', 'Medical Professionals', 'Shoes',
        'Jewelry', 'Tea', 'Systems', 'Religion',
        'Online Video Advertising', 'PaaS', 'Parenting', 'Forums',
        'Civil Engineers', 'Air Pollution Control', 'Natural Gas Uses',
        'Predictive Analytics', 'Natural Language Processing',
        'Cloud-Based Music', 'Internet Technology', 'IaaS',
        'University Students', 'Web Development', 'Optimization', 'Fmcg',
        'Online Gaming', 'Pervasive Computing', 'Storage', 'Nightlife',
        'Lighting', 'Incentives', 'Adaptive Equipment',
        'Postal and Courier Services', 'Fertility', 'Enterprise 2.0',
        'Multi-level Marketing', 'Concerts', 'Data Center Automation',
        'Call Center Automation', 'P2P Money Transfer', 'mHealth',
        'Tourism', 'SexTech', 'Contests', 'Financial Exchanges',
        'Natural Resources', 'Data Center Infrastructure', 'Recycling',
        'Retail Technology', 'Humanitarian', 'Online Education',
        'Governance', 'Funeral Industry', 'Gift Exchange', 'Social CRM',
        'Mobile Health', 'Online Reservations', 'Privacy',
        'Mobile Devices', 'Professional Networking', 'Game Mechanics',
        'Field Support Services', 'Home Owners', 'Social + Mobile + Local',
        'Freemium', 'Mechanical Solutions', 'Peer-to-Peer',
        'Personal Branding', 'Mobile Video', 'Group SMS', 'Textiles',
        'Tutoring', 'Plumbers', 'Shipping', 'Supply Chain Management',
        'Photo Editing', 'Solar', 'B2B Express Delivery', 'Translation',
        'In-Flight Entertainment', 'Displays', 'Internet TV',
        'Skill Assessment', 'Gas', 'Semiconductor Manufacturing Equipment',
        'Clean Technology IT', 'Synchronization', 'Farmers Market',
        'Senior Citizens', 'Skill Gaming', 'Neuroscience',
        'Unmanned Air Systems', 'Green', 'Building Owners', 'Eyewear',
        'Human Computer Interaction', 'Fuel Cells', 'Demographies',
        'Social Media Marketing', 'Monetization', 'Racing',
        'Mobile Shopping', 'High Schools', 'Specialty Retail',
        'Home Renovation', 'Business Travelers', 'Mobile Analytics',
        'Speech Recognition', 'Training', 'Swimming', 'Hedge Funds',
        'Interest Graph', 'Social Games', 'Stock Exchanges', 'Oil',
        'Television', 'Registrars', 'Polling', 'Flowers',
        'Vending and Concessions', 'RFID', 'Personal Health',
        'Golf Equipment', 'Mobile Advertising', 'Handmade', 'Smart Grid',
        'Price Comparison', 'Biotechnology and Semiconductor',
        'Mobile Enterprise', 'Disruptive Models', 'Resorts',
        'Vacation Rentals', 'Portals', 'Search Marketing', 'Google Glass',
        'Group Buying', 'Web Browsers', 'High School Students',
        'Shared Services', 'Debt Collecting', 'Indoor Positioning',
        'Local Commerce', 'Video on Demand', 'Video Conferencing',
        'Early-Stage Technology', 'Organic', 'Nutrition',
        'Rapidly Expanding', 'High Tech', 'Theatre', 'Social Recruiting',
        'Web Tools', 'Infrastructure Builders',
        'Enterprise Resource Planning', 'Group Email', 'Edutainment',
        'Music Education', 'Mens Specific', 'Gift Registries',
        'Baby Safety', 'Renewable Tech', 'Social Media Management',
        'Lotteries', 'Green Consumer Goods', 'Cosmetic Surgery',
        'Face Recognition', 'Energy IT', 'Kinect', 'Homeless Shelter',
        'Space Travel', 'Moneymaking', 'Product Search', 'Universities',
        'Pre Seed', 'MicroBlogging', 'Physicians', 'Direct Advertising',
        'Senior Health', 'Procurement', 'QR Codes', 'Subscription Service',
        'Independent Pharmacies', 'Impact Investing', 'Sex Industry',
        'Psychology', 'Music Venues', 'Promotional',
        'Independent Music Labels', 'Women', 'Testing', 'GreenTech',
        'Mobile Infrastructure', 'Retirement', 'Enterprise Purchasing',
        'Subscription Businesses', 'Virtual Workforces', 'Personal Data',
        'Young Adults', 'Lingerie', 'Film Distribution', 'Surveys',
        'Water Purification', 'User Experience Design', 'Taxis', 'Indians',
        'Veterinary', 'Social Buying', 'Ride Sharing', 'Experience Design',
        'Musicians', 'Mobile Emergency&Health', 'Usability',
        'User Interface', 'Sponsorship', 'Productivity', 'Gay & Lesbian',
        'Q&A', 'Micro-Enterprises', 'Task Management']

keywords_sorted = sorted(keywords)

countries = [
    'ALB', 'ARE', 'ARG', 'ARM', 'AUS', 'AUT', 'AZE', 'BAH', 'BEL', 'BGD', 'BGR', 'BHR', 'BLM', 'BLR', 'BLZ', 'BMU', 'BRA',
    'BRB', 'BRN', 'BWA', 'CAN', 'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COL', 'CRI', 'CYM', 'CYP', 'CZE', 'DEU', 'DMA', 'DNK',
    'DOM', 'DZA', 'ECU', 'EGY', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GEO', 'GGY', 'GHA', 'GIB', 'GRC', 'GRD', 'GTM', 'HKG',
    'HND', 'HRV', 'HUN', 'IDN', 'IND', 'IRL', 'IRN', 'ISL', 'ISR', 'ITA', 'JAM', 'JEY', 'JOR', 'JPN', 'KAZ', 'KEN', 'KHM',
    'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LIE', 'LKA', 'LTU', 'LUX', 'LVA', 'MAF', 'MAR', 'MCO', 'MDA', 'MEX', 'MKD', 'MLT',
    'MMR', 'MNE', 'MOZ', 'MUS', 'MYS', 'NGA', 'NIC', 'NLD', 'NOR', 'NPL', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 'POL',
    'PRI', 'PRT', 'PRY', 'PSE', 'QAT', 'ROM', 'RUS', 'RWA', 'SAU', 'SEN', 'SGP', 'SLV', 'SOM', 'SRB', 'SVK', 'SVN', 'SWE',
    'SYC', 'TAN', 'TGO', 'THA', 'TTO', 'TUN', 'TUR', 'TWN', 'UGA', 'UKR', 'URY', 'USA', 'UZB', 'VEN', 'VNM', 'ZAF', 'ZMB',
    'ZWE'
]

countries_sorted = sorted(countries)

states = [
    '1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2', '20', '21', '22', '23', '24', '25', '26', '27',
    '28', '29', '3', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '4', '40', '41', '42', '43', '44', '45',
    '46', '47', '48', '49', '5', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '6', '60', '61', '62', '65',
    '66', '68', '7', '71', '72', '73', '75', '77', '78', '79', '8', '81', '82', '83', '86', '87', '88', '89', '9', '90',
    '91', '97', '98', '99', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'AB', 'AK', 'AL', 'AR', 'AZ', 'B1', 'B2',
    'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'BC', 'C1', 'C2', 'C3', 'C5', 'C6', 'C7', 'C8', 'C9', 'CA', 'CO', 'CT', 'D2',
    'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'DC', 'DE', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'F1', 'F2',
    'F4', 'F5', 'F7', 'F8', 'F9', 'FL', 'G1', 'G2', 'G3', 'G4', 'G5', 'G7', 'G8', 'GA', 'GU', 'H2', 'H3', 'H4', 'H5', 'H7',
    'H8', 'H9', 'HI', 'I2', 'I4', 'I5', 'I6', 'I7', 'I9', 'IA', 'ID', 'IL', 'IN', 'J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7',
    'J8', 'J9', 'K2', 'K3', 'K4', 'K7', 'K8', 'KS', 'KY', 'L1', 'L3', 'L6', 'L7', 'L8', 'L9', 'LA', 'M2', 'M3', 'M4', 'M5',
    'M8', 'M9', 'MA', 'MB', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'N1', 'N2', 'N3', 'N4', 'N5', 'N7', 'NB', 'NC', 'ND',
    'NE', 'NH', 'NJ', 'NL', 'NM', 'NS', 'NU', 'NV', 'NY', 'O1', 'O2', 'O3', 'OH', 'OK', 'ON', 'OR', 'P1', 'P2', 'P3', 'P4',
    'P5', 'P6', 'P8', 'P9', 'PA', 'PE', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'QC', 'R3', 'R6', 'RI', 'SC', 'SD', 'SK', 'T5',
    'T6', 'T7', 'T8', 'T9', 'TN', 'TX', 'U1', 'U3', 'U6', 'U8', 'UT', 'V1', 'V2', 'V3', 'V5', 'V6', 'V7', 'V8', 'V9', 'VA',
    'VI', 'VT', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W9', 'WA', 'WE', 'WI', 'WV', 'WY', 'X1', 'X2', 'X3', 'X4', 'X5', 'X7',
    'Y1', 'Y2', 'Y4', 'Y5', 'Y6', 'Y7', 'Y9', 'Z1', 'Z3', 'Z7', 'Z8'
]

states_sorted = sorted(states)

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

# -------------------------------------------------------
# MODEL
# -------------------------------------------------------

@st.cache_resource
def get_model():
    return load_ml_model()

model = get_model()

def get_prediction(payload: dict) -> dict:
    # 🎨 Fixed: pass payload as single arg (not **kwargs); returns keys the UI expects
    try:
        input_data = preprocess_input(payload)

        # 🎨 Use predict_proba for a probability score when available, else fall back to predict
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)[0]
            success_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            success_probability = float(make_prediction(model, input_data))

        risk_score = 1.0 - success_probability  # 🎨 Risk is the inverse of success probability

        # 🎨 Extract feature importances; unwrap pipeline to reach the final estimator
        feature_names = list(input_data.columns)
        estimator = model[-1] if hasattr(model, "__getitem__") else model
        if hasattr(estimator, "feature_importances_"):
            raw_imp = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            raw_imp = abs(estimator.coef_[0])
        else:
            raw_imp = [1.0 / len(feature_names)] * len(feature_names)
        top_features = dict(zip(feature_names, [float(v) for v in raw_imp]))

        return {
            "success_probability": success_probability,
            "risk_score": risk_score,
            "top_features": top_features
        }
    except Exception as exception:
        st.warning(f"⚠️ Model error - using data. ({exception})")
        return {"success_probability": 0.0, "risk_score": 1.0, "top_features": {}}



# -------------------------------------------------------
# WHISPER / VOICE
# -------------------------------------------------------
def transcribe(audio_bytes: bytes, content_type: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": content_type or "audio/wav",
        }
        response = requests.post(
            "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3-turbo",
            headers=headers,
            data=audio_bytes,
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return ""

# -------------------------------------------------------
# CHART HELPERS
# -------------------------------------------------------
def gauge_chart(probability: float):
    if probability >= 0.65:
        bar_color = "#2ecc71"
    elif probability >= 0.45:
        bar_color = "#f39c12"
    else:
        bar_color = "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(probability * 100, 1),
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": "Success Probability", "font": {"size": 18}}, #Check font size
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": bar_color, "thickness": 0.3},
            "steps": [
                {"range": [0,  45], "color": "#fde8e8"},
                {"range": [45, 65], "color": "#fef9e7"},
                {"range": [65, 100], "color": "#eafaf1"},
            ],
            "threshold": {
                "line":      {"color": "black", "width": 3},
                "thickness": 0.8,
                "value":     65,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=60, b=20))
    return fig


def feature_chart(features: dict):
    df = (
        pd.DataFrame(list(features.items()), columns=["Feature", "Importance"])
        .sort_values("Importance", ascending=True)
    )
    colors = ["#3498db" if v >= df["Importance"].median() else "#85c1e9"
              for v in df["Importance"]]

    fig = go.Figure(go.Bar(
        x=df["Importance"],
        y=df["Feature"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1%}" for v in df["Importance"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top Feature Importances",
        xaxis_title="Importance",
        xaxis={"range": [0, df["Importance"].max() * 1.3]},
        height=280,
        margin=dict(l=20, r=60, t=50, b=20),
    )
    return fig

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("## 🚀")
with col_title:
    st.title("Startup Success Predictor")
    st.caption("AI-powered prediction of startup success - built with Le Wagon Bootcamp Montréal 2026")


st.divider()

# -------------------------------------------------------
# VOICE INPUT
# -------------------------------------------------------
st.subheader("🎙️ Voice Input")
st.caption("Describe your startup out loud - we'll transcribe it for you.")

audio = st.audio_input("Record your startup description")

if audio:
    audio_bytes = audio.read()
    audio_hash = hash(audio_bytes)
    if audio_hash != st.session_state.last_audio_hash:
        with st.spinner("Transcribing via Whisper large-v3-turbo..."):
            transcript = transcribe(audio_bytes, audio.type)
        if transcript:
            st.session_state.transcript = transcript
            st.session_state.last_audio_hash = audio_hash

if st.session_state.transcript:
    st.success(f"**Transcript:** {st.session_state.transcript}")
    if st.button("Clear transcript"):
        st.session_state.transcript = ""
        st.rerun()

st.divider()

# -------------------------------------------------------
# INPUT FORM
# -------------------------------------------------------
st.subheader("Company Profile")


# compare to app.py version for same name. must use CAPITALS 🚨🚨🚨
with st.form("prediction_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**General**")
        company_name  = st.text_input("Company Name", placeholder="e.g. Le Wagon")
        founded_year  = st.number_input("Founded Year", min_value=1990, max_value=2025, value=2018, step=1)
        country_code = st.selectbox("Country", options = countries_sorted, index = 0) #TODO: Check feasibility for our project as we only have US start-ups
        state_code =  st.selectbox('State', options = states_sorted, index = 0)
        first_funding_year =  st.number_input('First Funding Year', min_value=1990, max_value=2025, value=2018, step=1)
        last_funding_year =  st.number_input('Last Funding Year', min_value=1990, max_value=2025, value=2018, step=1)
        category_list =  st.selectbox('Category', options=keywords_sorted, index=0)

    with col2:
        st.markdown("**Company Details**")
        industry = st.selectbox("Industry", [
            "Software", "Mobile", "E-Commerce", "Enterprise Software",
            "FinTech", "Biotech", "HealthTech", "EdTech", "CleanTech",
            "Hardware", "SaaS", "AI / ML", "Other"
        ])
        employees = st.selectbox("Team Size", [
            "1-10", "11-50", "51-200", "201-500", "500+"
        ])
        relationships = st.slider("Key Relationships (People)", 0, 50, 5,
                                help="Number of notable people linked to the company")

    with col3:
        st.markdown("**Funding**")
        funding_total_usd = st.number_input("Total Funding Raised ($M)", min_value=0.0,
                                        max_value=2000.0, value=5.0, step=0.5)
        funding_rounds = st.slider("Funding Rounds", 0, 15, 2)
        milestones     = st.slider("Milestones Achieved", 0, 30, 3,
                                help="Product launches, key hires, partnerships, etc.")

    st.markdown("**Funding Types**")
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
    has_angel  = fc1.checkbox("Angel")
    has_vc     = fc2.checkbox("VC")
    has_roundA = fc3.checkbox("Series A")
    has_roundB = fc4.checkbox("Series B")
    has_roundC = fc5.checkbox("Series C")
    has_roundD = fc6.checkbox("Series D")

    st.markdown("")
    submitted = st.form_submit_button(label="**Predict Success**", use_container_width=True, type="primary", icon="🔮")

# -------------------------------------------------------
# RESULTS
#  concicliate with app.py 🚨
# -------------------------------------------------------
if submitted:
    # 🎨 Added company_name so the results header can display it (filtered out before model input)
    payload = {
        "company_name": str(company_name),
        "category_list": str(category_list),
        "funding_total_usd":float(funding_total_usd) * 1_000_000,
        "country_code":  str(country_code),
        "state_code": str(state_code),
        "funding_rounds": int(funding_rounds),
        "founded_year":  int(founded_year),
        "first_funding_year": int(first_funding_year),
        "last_funding_year": int(last_funding_year),
    }


    with st.spinner("Analysing startup..."):
        result = get_prediction(payload)

    prob     = result["success_probability"]
    risk     = result["risk_score"]
    features = result["top_features"]

    if prob >= 0.65:
        verdict     = "✅ Likely to Succeed"
        risk_label  = "🟢 Low Risk"
        delta_color = "normal"
    elif prob >= 0.45:
        verdict     = "⚠️ Uncertain Outcome"
        risk_label  = "🟡 Medium Risk"
        delta_color = "off"
    else:
        verdict     = "❌ High Failure Risk"
        risk_label  = "🔴 High Risk"
        delta_color = "inverse"

    st.divider()
    display_name = payload["company_name"]
    st.subheader(f"Results: {display_name}")

    # --- Key Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Verdict",              verdict)
    m2.metric("Success Probability",  f"{prob:.1%}")
    m3.metric("Risk Score",           f"{risk:.1%}")
    m4.metric("Risk Classification",  risk_label)

    st.markdown("")

    # --- Charts ---
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(gauge_chart(prob), use_container_width=True)
    with ch2:
        st.plotly_chart(feature_chart(features), use_container_width=True)

    # --- Debug Expanders ---
    with st.expander("🛠 Debug: API Payload"):
        st.json(payload)

    with st.expander("🛠 Debug: API Response"):
        st.json(result)
