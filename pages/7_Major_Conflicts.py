import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import numpy as np
import time
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Military Conflicts", layout="wide") 
st.title("🛡️ Global Military Conflicts Dashboard (1960–2020)")

# ─── INJECT GLOBAL CSS ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Full-screen war-scene background */
    .stApp {
      background: url('https://t4.ftcdn.net/jpg/03/49/86/71/240_F_349867133_a2Upqgg99LIDvsGbR4Of3a0bXCwqzrAQ.jpg')
                  no-repeat center center fixed;
      background-size: cover;
    }
    /* Translucent sidebar */
    [data-testid="stSidebar"] {
      background-color: rgba(0, 0, 0, 0.6);
    }
    /* Centered hero text */
    .css-1lcbmhc {
      text-align: center !important;
      padding: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    This dashboard provides an overview of major military conflicts from 1960 to 2020, including their locations, troop movements, and outcomes.
    Use the sidebar to navigate through different conflicts and explore their details.
    """
)


import time
from geopy.exc import GeocoderUnavailable

@st.cache_data(show_spinner=False)
def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="conflict_dashboard")
    try:
        time.sleep(1.1)   # ensure ≥1 second between calls
        loc = geolocator.reverse((lat, lon), language="en")
        return loc.address if loc else f"{lat:.2f}, {lon:.2f}"
    except GeocoderUnavailable:
        return f"{lat:.2f}, {lon:.2f}"


# --- Load Data ---
@st.cache_data
def load_data():
    budget = pd.read_csv("data/Cleaned_Defence_Budget.csv")
    military_exp = pd.read_excel("data/Military_Expenditure_final_rounded.xlsx")
    return budget, military_exp

budget_df, exp_df = load_data()

# --- Conflict Metadata (with outcomes) ---
conflicts = {
    'Indo-China War (1962)': {
        'year': 1962,
        'countries': ['India', 'China'],
        'region': 'Asia',
        'description': 'Border conflict between India and China in the Himalayas.',
        'impact': 'Significant impact on Indian military modernization and border defense strategies.',
        'outcome': 'China withdrew to pre-war lines; Tashkent Declaration signed; India overhauled defenses.',
        'events': [
            {"date":"1960","event":"Initial border clashes begin."},
            {"date":"1961","event":"Roads built by China in Aksai Chin."},
            {"date":"Oct 20, 1962","event":"China launches simultaneous attacks."},
            {"date":"Nov 5, 1962","event":"Indian reinforcements airlifted."},
            {"date":"Nov 20, 1962","event":"China declares ceasefire."}
        ],
        'troop_movements': [
            {"from":{"lat":27.59,"lon":91.87},"to":{"lat":27.32,"lon":92.46}} #Tawang to Bomdi La
        ]
    },
    'Indo-Pakistan War (1965)': {
        'year': 1965,
        'countries': ['India','Pakistan'],
        'region': 'Asia',
        'description': 'Second Indo-Pakistan war over Kashmir.',
        'impact': 'Led to military reforms and increased defense spending.',
        'outcome': 'Status quo ante restored; Tashkent Declaration signed.',
        'events': [
            {"date":"1963","event":"Rann of Kutch skirmishes."},
            {"date":"Aug 1965","event":"Operation Gibraltar begins."},
            {"date":"Sep 6, 1965","event":"India crosses international border."},
            {"date":"Sep 22, 1965","event":"UN calls for ceasefire."},
            {"date":"1967","event":"Border tensions flare again."}
        ],
        'troop_movements': [
            {"from":{"lat":31.63398,"lon":74.87226},"to":{"lat": 31.54972,"lon":74.34361}} # Amritsar to Lahore
        ]
    },
    'Six-Day War (1967)': {
        'year': 1967,
        'countries': ['Israel','Egypt','Syria','Jordan'],
        'region': 'Middle East',
        'description': 'Major Arab-Israeli conflict.',
        'impact': 'Reshaped Middle Eastern alliances.',
        'outcome': 'Israel captured Sinai, Golan Heights, West Bank, Gaza; UN 242 passed.',
        'events': [
            {"date":"1965","event":"Yemen conflict draws in Egypt."},
            {"date":"Jun 5, 1967","event":"Israel launches preemptive strikes."},
            {"date":"Jun 7, 1967","event":"Sinai offensive begins."},
            {"date":"Jun 9, 1967","event":"Golan Heights seized."},
            {"date":"Jun 10, 1967","event":"Ceasefire across all fronts."}
        ],
        'troop_movements': [
            {"from":{"lat":31.5,"lon":34.8},"to":{"lat":30.0,"lon":33.0}} 
        ]
    },
    'Indo-Pakistan War (1971)': {
        'year': 1971,
        'countries': ['India','Pakistan'],
        'region': 'Asia',
        'description': 'War leading to the creation of Bangladesh.',
        'impact': 'South Asian power dynamics shifted; Pakistan split.',
        'outcome': 'Bangladesh liberated; Dhaka surrender; Shimla Agreement signed.',
        'events': [
            {"date":"1969","event":"East Pakistan protests ignite."},
            {"date":"Mar 26, 1971","event":"Bangladesh declares independence."},
            {"date":"Dec 3, 1971","event":"India launches operations."},
            {"date":"Dec 16, 1971","event":"Pakistan surrenders in Dhaka."},
            {"date":"1973","event":"Post-war exercises expand."}
        ],
        'troop_movements': [
            {"from":{"lat":23.829321,"lon":91.277847},"to":{"lat":23.777176,"lon":90.399452}} # Agartala to Dhaka
        ]
    },
    'Soviet-Afghan War (1979-1989)': {
        'year': 1979,
        'countries': ['Soviet Union','Afghanistan'],
        'region': 'Asia',
        'description': 'Soviet military intervention in Afghanistan.',
        'impact': 'Cold War dynamics and regional stability affected.',
        'outcome': 'Soviet withdrawal in 1989; ensuing civil war.',
        'events': [
            {"date":"1978","event":"Saur Revolution."},
            {"date":"Dec 24, 1979","event":"Soviet invasion begins."},
            {"date":"1985","event":"Gorbachev announces withdrawal plans."},
            {"date":"Feb 15, 1989","event":"Soviet troops leave."},
            {"date":"1992","event":"PDPA government falls."}
        ],
        'troop_movements': [
            {"from":{"lat":41.0,"lon":61.0},"to":{"lat":34.5,"lon":69.2}}
        ]
    },
    'Gulf War (1990-1991)': {
        'year': 1990,
        'countries': ['United States','Iraq','Kuwait'],
        'region': 'Middle East',
        'description': 'Coalition vs. Iraq over Kuwait invasion.',
        'impact': 'Modern warfare technology revolutionized.',
        'outcome': 'Kuwait liberated; Iraq under sanctions.',
        'events': [
            {"date":"Aug 2, 1990","event":"Iraq invades Kuwait."},
            {"date":"Jan 17, 1991","event":"Operation Desert Storm begins."},
            {"date":"Feb 24, 1991","event":"Ground offensive."},
            {"date":"Feb 28, 1991","event":"Ceasefire; liberation."},
            {"date":"1993","event":"No-fly zones enforced."}
        ],
        'troop_movements': [
            {"from":{"lat":25.0,"lon":45.0},"to":{"lat":29.0,"lon":48.0}}
        ]
    },
    'Kargil War (1999)': {
        'year': 1999,
        'countries': ['India','Pakistan'],
        'region': 'Asia',
        'description': 'Infiltration along the LoC in Kargil.',
        'impact': 'Heightened tensions; border security strengthened.',
        'outcome': 'India regained posts; conflict ended by July 1999.',
        'events': [
            {"date":"May 1999","event":"Intrusion detected."},
            {"date":"Jun 1999","event":"Battles at Tololing."},
            {"date":"Jul 4, 1999","event":"Tiger Hill recaptured."},
            {"date":"Jul 26, 1999","event":"Operation Vijay ends."},
            {"date":"2001","event":"LoC fence reinforced."}
        ],
        'troop_movements': [
            {"from":{"lat":34.6,"lon":76.2},"to":{"lat":34.556335,"lon":76.132507}} # To Kargil
        ]
    },
    'Afghanistan War (2001-2021)': {
        'year': 2001,
        'countries': ['United States','Afghanistan'],
        'region': 'Asia',
        'description': 'US-led intervention after 9/11.',
        'impact': 'Longest US war; changed counter-terrorism.',
        'outcome': 'US withdrawal; Taliban regained control.',
        'events': [
            {"date":"Oct 7, 2001","event":"Operation Enduring Freedom."},
            {"date":"Nov 2001","event":"Taliban regime collapses."},
            {"date":"2011","event":"Osama bin Laden killed."},
            {"date":"Aug 30, 2021","event":"US completes withdrawal."},
            {"date":"2022","event":"Taliban consolidates control."}
        ],
        'troop_movements': [
            {"from":{"lat":38.0,"lon":68.0},"to":{"lat":34.5,"lon":69.2}}
        ]
    },
    'Iraq War (2003-2011)': {
        'year': 2003,
        'countries': ['United States','Iraq'],
        'region': 'Middle East',
        'description': 'US-led invasion and occupation of Iraq.',
        'impact': 'Major impact on regional geopolitics.',
        'outcome': 'US withdrawal in 2011; ongoing insurgency.',
        'events': [
            {"date":"Mar 20, 2003","event":"Invasion begins."},
            {"date":"Apr 9, 2003","event":"Fall of Baghdad."},
            {"date":"2006","event":"Surge strategy deployed."},
            {"date":"Dec 15, 2011","event":"War formally ends."},
            {"date":"2012","event":"Last troops leave."}
        ],
        'troop_movements': [
            {"from":{"lat":28.0,"lon":48.0},"to":{"lat":33.3,"lon":44.4}}
        ]
    }
}




# --- Additional Sector Markers ---
additional_movements = {
    'Indo-China War (1962)': [
        {"lat":33.9,"lon":78.2,"label":"Rezang La Sector"},
        {"lat":32.9,"lon":78.8,"label":"Tawang Sector"}
    ],
    'Indo-Pakistan War (1965)': [
        {"lat":31.5,"lon":74.3,"label":"Amritsar Sector"},
        {"lat":32.0,"lon":75.1,"label":"Jammu Front"}
    ],
    'Indo-Pakistan War (1971)': [
        {"lat":24.5,"lon":88.3,"label":"Jessore Advance"},
        {"lat":23.9,"lon":91.3,"label":"Agartala Front"}
    ],
    'Gulf War (1990-1991)': [
        {"lat":29.5,"lon":47.7,"label":"Desert Storm Entry"},
        {"lat":30.5,"lon":47.8,"label":"Basra Advance"}
    ],
    'Iraq War (2003-2011)': [
        {"lat":33.4,"lon":44.2,"label":"Baghdad Advance"},
        {"lat":31.9,"lon":44.5,"label":"Basra Front"}
    ]
}

# --- Military Strength Data ---
strength_db = {
    "1962": {"India":{"Personnel":350000,"Tanks":200,"Fighter Aircraft":100},
             "China":{"Personnel":800000,"Tanks":700,"Fighter Aircraft":400}},
    "1965": {"India":{"Personnel":825000,"Tanks":720,"Fighter Aircraft":460},
             "Pakistan":{"Personnel":365000,"Tanks":600,"Fighter Aircraft":300}},
    "1967": {"Israel":{"Personnel":275000,"Tanks":800,"Fighter Aircraft":300},
             "Egypt":{"Personnel":240000,"Tanks":900,"Fighter Aircraft":350}},
    "1971": {"India":{"Personnel":1000000,"Tanks":2200,"Fighter Aircraft":450},
             "Pakistan":{"Personnel":365000,"Tanks":1700,"Fighter Aircraft":300}},
    "1979": {"Soviet Union":{"Personnel":900000,"Tanks":2000,"Fighter Aircraft":700},
             "Afghanistan":{"Personnel":170000,"Tanks":500,"Fighter Aircraft":100}},
    "1990": {"United States":{"Personnel":540000,"Tanks":2000,"Fighter Aircraft":1400},
             "Iraq":{"Personnel":650000,"Tanks":5000,"Fighter Aircraft":700}},
    "1999": {"India":{"Personnel":1100000,"Tanks":3100,"Fighter Aircraft":620},
             "Pakistan":{"Personnel":560000,"Tanks":2400,"Fighter Aircraft":410}},
    "2001": {"United States":{"Personnel":98000,"Tanks":1000,"Fighter Aircraft":1200},
             "Afghanistan":{"Personnel":40000,"Tanks":100,"Fighter Aircraft":40}},
    "2003": {"United States":{"Personnel":150000,"Tanks":1300,"Fighter Aircraft":1100},
             "Iraq":{"Personnel":375000,"Tanks":2000,"Fighter Aircraft":300}}
}

# --- Conflict Locations ---
conflict_locations = {
    'Indo-China War (1962)': {"lat":33.7,"lon":78.0,"label":"Aksai Chin"},
    'Indo-Pakistan War (1965)':{"lat":32.5,"lon":74.0,"label":"Lahore Front"},
    'Six-Day War (1967)':     {"lat":31.5,"lon":34.8,"label":"Gaza-Sinai"},
    'Indo-Pakistan War (1971)':{"lat":23.7,"lon":90.4,"label":"Dhaka"},
    'Soviet-Afghan War (1979-1989)':{"lat":34.5,"lon":69.2,"label":"Kabul"},
    'Gulf War (1990-1991)':    {"lat":29.3,"lon":47.9,"label":"Kuwait City"},
    'Kargil War (1999)':       {"lat":34.5,"lon":76.1,"label":"Kargil"},
    'Afghanistan War (2001-2021)':{"lat":34.5,"lon":69.2,"label":"Kabul"},
    'Iraq War (2003-2011)':    {"lat":33.3,"lon":44.4,"label":"Baghdad"}
}

# --- Conflict Images ---
conflict_images = {
    "Indo-China War (1962)": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Indian_soldiers_on_patrol_during_the_1962_Sino-Indian_border_war.jpg",
    "Indo-Pakistan War (1965)": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Pakistani_AMX-13_%281965_War%29.jpg/500px-Pakistani_AMX-13_%281965_War%29.jpg",
    "Six-Day War (1967)" : "data:image/jpeg;base64,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",
    "Indo-Pakistan War (1971)": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/1971_Instrument_of_Surrender.jpg/500px-1971_Instrument_of_Surrender.jpg",
    "Soviet-Afghan War (1979-1989)": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ5kFt15sfNaSopAutFQqE4HHDzM_3NeVRAPA&s",
    "Kargil War (1999)": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Kargil_war.jpg",
    "Gulf War (1990-1991)": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQuzpZqrTStm4E5UwZm4uvzRDoZfBHUSIbiuL7w1ylMumVCtmXM7yW9-6XrhePcPQ1aUiU&usqp=CAU",
    "Afghanistan War (2001-2021)": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQFMVoiTM6DIDnTJMyuq2RNddAjIefJhiv4NkroUyHfBU4BE_X_omt6YwMy7NGIDxEIp0c&usqp=CAU",
    "Iraq War (2003-2011)": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUSEhIVFRUVGBUVFxcYFxcVFxcXFRYWFhgXFRYYHSggGBolHRUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGxAQGi0lHyUvLS0tLS0tLS0tLS0tLS0rLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIALgBEwMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAACAAEDBAUGBwj/xABCEAABAwIDBAcFBQYFBQEAAAABAAIRAyEEEjEFQVFhBhMicYGRoRQyUrHBB0LR4fAjM2JykvEVJEOColNjc7LCFv/EABkBAAMBAQEAAAAAAAAAAAAAAAABAgMEBf/EACMRAAICAgICAwADAAAAAAAAAAABAhESIQMxIkETMlEEYXH/2gAMAwEAAhEDEQA/ANUBSBINRAL0TjEU4CIBEAgQwaiATgIgEDGARgJAIwExAhqIBGAnDUACGosqINRBqBAZUQajARAIAjDU4apA1PlQBGGp8qkyp8qAI8qfKpA1PlQMiypZVZp027zHggLEWBFlSDVJCWVADGidYQFimN0xCQyHKmLVNlTEJARZU2VS5UoQMiypZVMApKDspmJUsCFlAnQFbGydlNe0l40MeSjwmKvBsNVfwmMa2w0KxnKRrFIst2VRH3B4ykj9tCZY2zTR5sAnhEAjyruOUEBEAnARgIAEBGAnARAJgMAiATgI2tQIYBGAnARAJgMGpwEQCINSAEBEAiARAJgBlTwjhRYyu2lTfVeYaxrnuPANBJ+SVgSAJ8q8cxP2oYkVs7Q3q5nqyBdvDNrMb+O5eubJx9PEUWV6RllRocOPMHmDIPcohyKXRUoOPZYDUoQVMVTa4MdUY1zrNaXNDieABMlTwrskCEoR5U+VAyOE0KWE2VAEeVKFLlSypARZU2VTZU2VIZFlSyqXKnyJDIcqOnTk6wpQ1Gxp1AsPLxSbHQLaRBurDnCyaqXOAJiNAoqjC2yyeyui9TrAAWSVHrUlGJVnMgIwFTpbQZMOlh4OEeJ4DvhXWEESCCOIuF1WY0OAiDU4CkATAEBEAiDU4CAGARAJwEYCBDAIgE4CIBACARQnARAIAZoUzGjeqlXHUWPFN9Wmx5GYNc9rSRMSATcSqWx+kdGvUfRzBlZkzTLgZA+9TeDlqNuNLibgJOS6GkzYe0blBisM2ox1N7czHtLXNOha4QR5FTZ2/EPMLF290swmEtUqBz/+mztO/wB25o745ShtJbBK2eKdNuiFfZ7ybvoOJyPAJAE2bUMdl9xyO7eBl7F6QYmgHNo1qlMO1DXEDfoN2puI1W7016aVcY4szFlA5QaTbh2VxcC4nfJ3RoLWXJtblXDJq/E6op1ssYjGPJzOJLpkkmTPGV6F0N+051PLSxkvZoKou9v84++OevevMaj0OU6jyRGTjtCcUz6swtdlRjalNwexwBa5pkEHeCpoXgn2b9N3YKp1VUk4Z57Q16sn77B8xv11198oVGvaHscHNcAWuBkEHQg7wuuE1JGEo4sbKllUsJZVdkkeVC1wJI3jXxupoShKx0R5U2VTBqYtSsaRHCQapMqvYXBSDNjuUuSRSVgYDCA3dB5XlXqdDLZuh1soWbPM3d3c0TQWyJnxWEnfs0iqD6sZSIEngqLqGoMQrJqKF1WdVCbHRX9lCSm61JGTDFHAnFtPZqM9J/4vAcfAFJmEpOPYcWO1gEtd4tN1o5dyhfgaZEZY5Cw/p09F2GBEGV26OZUHMZXdwIt5o27RDf3tN9PnGZvcHNSGDe33Kh7jf8QB3BG2vWb71MO5tn0FyT3wgVFqhWY8SxzXDkQfkpg1ZL/ZnntsyO4xkcO9zNPEqxSwz4mliCRweBVb/UId6p2FF8BGAqHtFdvv0Q8caTgT/Q+PQlSU9q0ZhzurPCoDTPhmgHwlFhRdARgJNG9GAmIYBGAkqTtrU7CmHVnEAgUxIIMw7OYYG2Nyd1pKVgVukPRfDY1sV2HMBDajTle3uMEEciCFwe1/s0pgOp0MZVqVhdtLq2OA/wDK4EBgPxOI8dF6OMJWq/vn5G/9OkSP66tnH/bl8VeoUGU2hrGtY2bACBJPzJUSgpdopSaPn2v0A2qCR7IXQSJD6RB5jtTCah9n21nw0YQtH8T6bWjn73yX0UAnDVPwxK+Rni2y/sYruviMTTp/w02moY/mdlAPgVj9L/s/xFCsaeHZUrMawPDoGZwg5gAPecC02F/E3+hadKeSwOnOw318PNIkVqRFWnBHaykEsncTAg7nNaVM+ONa7KjN3s+XzrwTtfwXs/T/AKBNxWFZjcI1xr5A+oCAH12uGYktAA6wcgJFuC8UWTjRadljW+hXo32RdL6lOuzBVHTRqkhgIJLKh0DTuaTMjSTNrrzIFafRva/smKo4kND+qcHZTodQRO6xN+MIi6djkrR9WBqfKszo10mwmOZmw9TMQ1rnsIh7M8wHTqZaRadFsABdOVmFEOVSMoEqxTo/EY5cVM0cGqXMpRIKeFMSbIhhmgSTJUrqx3pCiDcuWWTKxRXw7GzJMcoVqnTJvPdKgrNAIhD1pHFEnY0qLVSoRqVXfXCrVapKhcVGI7J6lYKB1VA4oIlFDC6xOmyjmkkBggIwEwRgLsswEAjASARAJ2IZ1MGxAI5iVXfsymTIBaeLSQVbARAIApDC1W+5VkcHifNwuidVrAQ+gHjfkcD5MfqrwRtCAOT2/iKNGhUqUmVKFRsEQ2pSAlwBccvYdAJO/RcPh9tV31GNZinmqXNLAHZ3G+mUTLTzGkr2cBR4fB02TkpsbOuVobPfAWHJwubTujSHJiqo43aXRfF1msFQ0nPcQalVjn0zpBY4TFRmkQBpoF2eztn06DBTpNytAAGpMNECSbmysAI2rSMFF2iXJsQC4/pt0lq4d7adJo7IZUcSCZ7Vm20FrrtGgLzT7QcW2pXimZDW5HWPvNcbA2463WfPPGPdF8UE5Hf7ExwxFCnXAjrGh0axxE98q+AszofiqdXC0shnIxrHWIhzWiRB/V1vOpjhHPWVanpEOOyuGpyFaDOJOiTKCMwxMZn7F+U/uqjuydzKjrlh4Ncbj+KRvaF5r9on2V1cRifaMCKY62TVY52QB/xtt97eOInevZK+zw8Froc1wgg7wqDCaDslZxLPuVjpybVP3XcHGzu+xhyTVFJNHyVtnZFfCVnUK9M06jdQd43OadC07iFBgMHUqvFOk0vedGj3ncmjeeQX1h016G4baVLq6whzR+zqtAzsJ4He02luh74K+aulnRTF7LrBtYEDNNKs2Q1+WDmY7VrhItqCsjQj6M7er7PxTarQQWEsqUzbM2YfTdwNvAgL6m6P4uli6FPE0HhzHiRxad7XcHA2I5L4/c5xdmdLi4ySbkk7yTqV6H9lvTt2zaha8OfhqpGdo95jhbrGDeYsRvAHC5k0GKPpJzQNdfNQueSYCmZiWPY14ILXAOaeIIkHyUEAXDrppiYNQkGCFEQTp6KwL6me/wCiIODdE8qCiq7MNxUYkmFarPJ3qDrCEsgoTsPaSVAQNyNxJULlNjoB5Q5gge5QuegZLmSVUvSQBSCNqjCMLps5yQIgEARhOwDCIBCCjCLAcBGEIRBOwDCIIQUQKLAIIwgCMFKwJGwvI+m2ywzE1ocYcQ8cs8OI8yV600ry77QgfaqkExlp+ob+Hquf+R9TXi7O6+zrZ3s+CpicxqftXGPjiBB4NDQumLh3FYfRZ59jw0n/AEaf/oFrNKtLSJb2WKTJNypjwGnFRUXHQFV8VjW0mlz3Bo4n6DeVLZSRoNfH5J3YgRBE7oWDsrbVKvZrxmv2TYxNoB1twWvh2A6qRlCpgsv7mo6kPgs+n/Q73RyYWryz7aaVWp7LSqFjo610taWRORtwXO1v5L2SpRIEgyvG/tQYfbSSf9Nn1t6KZtY6Kj9ji8TsalWqveBlY4y1oAbAgaxYbzbir/8A+fw7GyGmQQJL3kxHfCbDESN/9ltOaOqcQNC0mba25rklN2dKiqIsP0hxVKm2nTxDw1hGUSDAAgCSJy8tF2PRPptUxFZtCsxsvBh7JFwCYc0k8DcLzio/lvV7oliMmNoO/wC40eDuz9VtCbRlKKPdGuOinp07XVcVYT+0QtmzNIldTjW6q1XDcmqV5UD6qkYnPQPqKN9RQueiwDeVCSmdUUTnJ2IPOnVcuSQBACjBWe3EKZuJC3yMaLoKIPVUVQU5EoyCi41ykDllEkI2YohGQ8TUBRtKoNxKlFdGQqLoKIKk2spG1UZDxLQKMFVhXS9r5JZjxLS8V22a1OrVpvklriCcpM3kGTxBB8V7I3GBea9Mqodiqp/k/wDRq5+d2jXiWzq/swoVG4MPqzFR7nMFxDBDd+gJaTbiuxkDULnOjOJjCUL/AOmz5LT9sHFaLpEPsW2NtU8MzMZLz7rBv5ngOa8+2hj6ld+eoZ1tPZG+GjcEG3NpOrV3ONxmLRya2QI8p8VTY65kiLR37/p6rmnyNvRrGAQtwBkEHQjS1uHFdb0d6YOaRTrmQbB+pB4PO8c1xeaM2Zw1kXi0f3sqrqhAMkE3jmJt6R6ojJipHuzMVAXlH2qs/wA0w/FSb6OeF1HQza2fDgOMmmSzvEAt9DHguY+05+atSP8AAR/z/NaN6BdnHUd11oCocpGaBAtx3/QKk1mW3EfVXKXu6fdK5pHREzqu/wAe9NgK+Sox/wAL2O/pcCpsQY8R+SpOK0RDPoJ1UblE+qsnBY7NTpu+JjD5tCm9pW5iW3VVG6oqxroXVeaAJnVFGXqs+qg65AFkvQF6gNZQ+0DiEDLiSp+0JIAz2uUrFC0KUFa2ZE7FYplUc6RrFKwo0HOCqYzEtY0udoBJ4xxhRNqlcd02240E0cgkD3nC4newyCO9JypDSNWl00o5wwtcNTMiBEwO82811VKsCJnVeCsxHbaSb2g8IXr+x646vOetbA7XWk7hqN0d0KYyb7KaOhZUT9YuYf0tw7a3U9omwkRF76zpF1q4TaTKnuSbNdJa4CHTEEi+mm6ydio1cxUbnFRMrJOqoGGXFeedKqp9pq3+AeYZ+Hqu9NRcBtiKtV72mcxtusIj5LPlaoqCbejs+j1U+y0f/Gz5LRFVc7sHa1EYem01AC1uUjeMtrhXv8Yo/ET3NcfonnFewwf4cbXwlYve1zoguEC9hz0HHxVeaYZnd1hAdl96LzBMcLT5LXxr3OqPc0EtLiRYjXksbGYZzWEOb2ZzSSAZO4DguWXKrpM2jxurZFXxdHNl7UWMhxNrfmVI3CMe0PY51zA7R3cisYUGmoGyTaeUncTwsVu4Om4nKWFsd5bPhoj5MfYlBs6v7P2FtGo4umXwOIyga+fooOn+tE/zj1Z+Kh2TjH4ZhY0NOZxdJm0gCI8Fl7e2rUrwHhnZJjKCLmx1J4BaR5oyVIHxSjtlFhJPmrNFx0nj+P0VCnxJ3LSwdSLkb53aEQs5FIz6xuLqrU5K3iHzIH6uqdQq4ikel7BrThqP8gHlb6K71sLE6JVJwzBwLh/yJ+qg2gWiq8FrnXBgyRcDSbRqtJTxjZnGNujpRVVHaW1Oqy9hzi6QI0sJudyo7EdDHANLYe7XfMH6pttuJYDIGVwJkTY9njbVGTcLQVTokpbZe57WmkQHEicwtYnTfotA1VymaHMPWn326Zd57l0Rcp4ZOSdlTST0YWPazragfUc64IBdpIFgBoE+yXU2VoAILmkDXcZRbccWPa8NkEZSeYJInzKr4Oq91ZlgAA4nuj8ws5JrkRSfgdH1iSr50l1GIQqIxUWdTe6LkHwj5KVtaysgul6HMuT6U7eNNuRhhzhqPUcu9cxgek2IZPbzTpmv9dPzUuVDSPUzVABJMAXMryPbuM66s5+aASec7rDhAWnjOl9YtyiASLmLgnWATC50XuJ4fKVDlY8QWiZibCeOm9dqza1ahg6eYhwfoHAFuX4eJMz2QN3BUeheBpkVHOv9zKdMpAMx5rq69bDnIX5OxOQmMokQY3aJr9Eed1aTm1G52xLQ+CY7J0GsjQrvMBt808NndJJ9zQNiLX/GdFhY3ZXWvl1QQ0U2OdOrQMxjneU7sMzI3qagyMMw7UuJEWI0Ez+CBmnsLpZVdVIquhhjcAAd8nWPy5rtaWJDgCDINwV5lhtnOd1jrOOYuJO/tEWP3dNy67Yr/wBkzXTl9Eoy3Q2n2dBVq9k9x+S4Fla8frRbu2NsmjDQwOzDXNEbuBWDRY003OJIIJ0E6N32WHO0zbitEey8S1odmP3neTRJ9FtNrAeIXPYXAvBGcQJee/MIV/qM7R2XHT70f/K5ZRTZtnSNFmPbcmQBNzxB5KptB9NzmzJjLl+GakgOjeRHySeAyiW+7qYidd5PenZRtemJtrJNuN1Px09A+RVs591PJWaw2FwbxYggX7iF0LXmkQ0xlMSZJi263JVHYcl7oayQGjQxNzx4EKWvQLi0FrQCDu0sQtJK1smEleg6m0hnyCIzME8nB0+oCq7RMHxP0WVWbSpG0PcDMxaWnjKTNqdaYcINyPRVDjqSaFLlTTTNBtm5iRGvn/ZPTc07zu3R+rpgJbygx3iNyGq2L+g5QVsZ2FiOOpOuiqVf1/ZXacuZOXcTp+v0FUqb/wAERGzreh1f9i4cHn1DVPj8RnqTTeDbK4WkESR4XK5DC417aT2tFjE8Uuj2LnENFhIcPT5qpu40QlTs6zBYxtNpD33c53nYRbfaUGL2iC403Nluh5g7+S5fpFiDTrwOAd3mIuN8QqA2q8kOzSdL3hOEvFBJbOtosAyOiYI+cSto1Fg4GtnoSLntX5i/zRf4y0AZmvEjeInuU8TSbQ5JtJmljzmpuHKfK/0VCi+HMN7yPMW+SnbiGuGuonwKqud2Afhg+RhPl7TCHtGl1idZH+K0+J/pd+CS1yRnTDZtIFxZlcIEzYDdwM70xxU+Z+a5nD4xrGvq7py7t3cpqO1GlmcmI15GxjmnF62JrZLtPZjDmqkkujSbcTHOFgtwEVWNcQW5mttwDgDbWT9Ue2tqPccogHSYFhz525rPwTy+pTHF9MHn2gFjCMkts0k03ot9IaFJjwGCNd/DxVKnWhsD9SpukLx1zraW5cfqs+bHerivFEt+TNPAYxwJcHEaWBIDiNJjVbWMxR9kbzL7RaS4k85XMYEPdIbeLmL91luY9jvZKQiCS4xpq4mb+ama2v8ARx9ma2udRMm3C36+Suh5gTOWx5TAWa0WBnWbfL6q1BMwCYDRpOoACbFFG7sauXNeyNG5r/rmtDB9JKVKk1pYS8C25p4z/ZY+wJzVgQRlpxf+ZqyK9STOkiLfgs8bkzRypG1itqPxBlwAiQI4G6v7P7TKgJMBzdDxF58lytGr1e7v5+G5dNsKpmZVP8VP5FLkXbCErpGrh3sqFwBMg39BZZO3tsuoMaGAFzpAmYEa6d4VrY5/av8A5KfqXrI6WMuz+Z3yaufjrOma8m42aezNqOrYZ73AZmGCBpYTaZWTsfb9Z9YNqQWumALZYBPiLd/yV3o23/L4kfx//JWTgBkr0zpB/EfVbUrejN9Ifa+2KwrOFNwa0OnQGbAXndbcupp189CjVNi6mfAkHjzXJY+jBk7w1x/3ZSfmugxDv8lSI3T6OKUknFBG0zmK4GskAe8J1nh6qTZ7CKoANrwD70EGI4hVzU7UTB14o8K5wrU7zrbwK3RlXs6qjOXWNR9E4b2Znj56IKWIOWCBAvpffZOKscJ7hCg0JsNSLWG8WMzYiZWc9quVa5IgmxA4Ko4c/VCArlhggTfgY/uqOw65Zi6cm+eD4yPqFps1WXjWZcQxw3FjvI/kqvdCa1ZtdN2xVpmNWkeR/NYFSoDoMvjw79V1HTk/s2uAk6A7xMGR5Lkab5bli48zffzSh9RT7Oy6I1JouB+64+oWbXewFwJlwJAkAxyEzyU3Q55BqNM6Aj1Cy9vUSK7yBYkeo/JTj5FX4gddBnMSfK3BdPsqtnoyOY8lxZD9wXTdFnuyOa7UGfA2+ic46FF7MXE1Q1zgdxPBJWdp7Omq48/oEkJqhuLswtnVycxPB0d9oHqVZNZrWN7EQ0O0iXhsCbyqAbFP3iIAcBfV06+ijwzn1DlJJFvAfqF0fpiDVc7U773QPqC0cB/dWKpBnhmjwVR7ZkjQf2TQF11Au3zYb5JsEqeFMOHED5o8A82kWAE+XPu9VpUm0+scHZurLTcRYjSOSl2PRS2dV9ne2sWlwEixiZERK18VinV6LHgHtlxI1jK4gd2gWVjWFwDGsLWtuTu7296s4Co5tJrQ2YLhfS7gQQlLoaqyKrQqOAblAdP3RESTIgaC4VnC4ttLNLrmIN4kAC1vHxQUzVYyAMzifejdIkF2o8FBiqFWrmJYJsREAHcbaJNJ6YrNfo/WD+vIP+m3v97U8+SxjhrSXtEcTC6TCMosYIysOVvWEGM0AAgk63+qx8ThyMwpvblMkOvMQezm4XKlJWx/0TU8FTa1vbzZwDmizNMzTz7QVynjqFCi7JUzl7hbeMoNyOEwPFVauNqVJEgAWMW0Drj+q5WPjqBflyti+U3k6CTrpqjBPTZWVdG7s3aEPzGQC1s2jTh5lS7ZxdJ7SZBcNAZ+9luLawOW9ZlaocoE3ywdLWsJhU6WJcDOUF4JILhnbuFmib+G5SuJXY1P0zsNkUqYoVnU3lzXEG9osRpuXK1MXTzG7iWkQdLb5HktLZZquoYoBj87shHYIzS4zlEWsfVU39H8W4gig4SADdovxglOMUm7HJ60XMS6k5zXBxIIAgNkdjKzjf3gVtV2mnhWZQ4wSBIyuMujTzWOdkmW9a9rSx4cRBN27jyW3iscHtawkGLyBlHg29tN6mcYqkthBvtnOf4W5zpyRecznNB37gZVxmxwCH525hG8mbGdyvEt3u9CqorZnEMdlAMSRJJjhNtRxTysKJjRO9wHgqDcRVdIDWtIMS4yPCBdS1GPcf3kDSANfNSYWk1sgkuJMzGmttUWA1JtWIeWTyzJ2sqbwzzI+isOe2bSP13oesbpcpWMelh5MlwneBdQ4rA03Sczw6IHZESJhS9e0bj5hMK7eB8x+CVhRobYAfQYXTYsJy66QYXJ0Xtkio5wJBygD70mA7fErb9tI0nukfOFWxeSoQ54LiIvIFp5NEqotITVknR4ltW5sQR9VJt+kTUEAQRxi7QT4mxVzD4RjSHCbXEE92k6occaNSMznCOTh5qWndoar2cxVrz7mhaCJWt0drkvM726d1/qrTMDhhEOAjS34o8Ng6TKmcVRPw2C0dP0QizWpy4lJWZb8QSXPizXJHnr6VQ9kwM1zv5DTSFJQw7aYcM7STH47p/QSSXWtmD0NSw0tNtQYkRBOhvA4qRmEblaw2G/iTrcjdZJJFkkuCa2TJECw3+nBHVDCZBtvnTgkkkMRq2i0c5OilLmiDmzSOHu6eaSSVBYz61Q9lkHdAH0hTUtn4moNLcSWgepSSSYy4OiddwGaowebz9FoUOiQ+9Wd/tAHzlJJMC1R6MYduuY97o+UKwdnYVkuNNttSZPzSSQBUftTDM/d0Wnnla0fKVE/pG7Roa3lcpJKmkiU7Ihtys7eQP9oH1KOltB7iBndJMbzr3O+iSSybNK1ZPW2fmBnUmZiHd0yoDsgzOc90C3okknikTkylUw7WuIL6nZ/kj5IaTaQJgPk3u4fgkkkzRBOqs+E8dUuuZ8O7WUkkgGp1Gz7s95T9dT+A/1aJkkDB6xnwn+r8kJqt3N/wCRSSRQCbUYfu+pTde34B5lJJMVk1PaUWDG+ZSxGMDxdrdNbgpkkxFHK9A4PHFJJFixRAXu5JJJKxUf/9k="
}


# --- User Interaction ---
regions = sorted({c['region'] for c in conflicts.values()})
region = st.selectbox("🌍 Select Region:", regions)
wars = [w for w,d in conflicts.items() if d['region']==region]
war = st.selectbox("🎯 Select Conflict/War:", wars)

if war:
    info = conflicts[war]
    year = info['year']


    # ── Visual & Summary ──
    st.markdown("### 📷 Visual & Summary")
    img_col, sum_col = st.columns([1.5, 2])
    with img_col:
        if war in conflict_images:
            st.image(conflict_images[war], use_container_width=True)
    with sum_col:
        real_loc = get_location_name(
            conflict_locations[war]["lat"],
            conflict_locations[war]["lon"]
        )
        st.markdown(f"""
            **Conflict:** {war}  
            **Year:** {year}  
            **Region:** {info['region']}  
            **Countries:** {', '.join(info['countries'])}  
            **Description:** {info['description']}  
            **Impact:** {info['impact']}  
        """)
        st.markdown("#### 🕒 Key Events")
        for ev in info['events']:
            st.write(f"- **{ev['date']}**: {ev['event']}")

    st.markdown("---")

    # ── Tabs ──
    tab = st.radio("Conflict Insights:", ["📊 Budget Trends","🪖 Military Strength","🗺️ Conflict Map"], horizontal=True)

    # --- Tab 1: Budget Trends (% of GDP for all parties + checkpoint) ---
    if tab == "📊 Budget Trends":
        st.subheader(f"📈 Defence Budget (% of GDP) Around {war}")

        # years ±2 around conflict
        years = [str(y) for y in range(year-2, year+3)]
        fig = go.Figure()
        all_gdp = []

        # plot each country
        for country in info['countries']:
            df_c = budget_df[budget_df["Country Name"] == country]
            if df_c.empty: continue
            tmp = df_c[years].T.reset_index()
            tmp.columns = ["Year","% of GDP"]
            tmp["Year"] = tmp["Year"].astype(int)
            all_gdp += tmp["% of GDP"].dropna().tolist()
            fig.add_trace(go.Scatter(
                x=tmp["Year"], y=tmp["% of GDP"],
                mode="lines+markers",
                name=country
            ))

        if all_gdp:
            max_gdp = max(all_gdp)
            # vertical line at conflict year
            fig.add_vline(
                x=year,
                line=dict(color="white", dash="dash")
            )
            # annotation / pin for conflict
            fig.add_annotation(
                x=year,
                y=max_gdp,
                text=f"{war}",
                showarrow=True,
                arrowhead=2,
                ay=-40
            )

        # force integer ticks on x, restore y-axis label
        fig.update_xaxes(
            tickmode="linear",
            dtick=1,
            tickformat="d",
            title_text="Year"
        )
        fig.update_yaxes(title_text="% of GDP")

        fig.update_layout(
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    # --- Tab 2: Military Strength ---
    elif tab == "🪖 Military Strength":
        st.subheader("🪖 Military Strength Comparison")

        sel_year = str(year)
        if sel_year in strength_db:
            data = strength_db[sel_year]

            # 1) Personnel — horizontal bar chart (one trace per country, with legend)
            fig_pers = go.Figure()
            
            # pick as many colors as you need — here blue for the first country, red for the second
            colors = ['blue', 'red']
            
            for i, country in enumerate(data.keys()):
                fig_pers.add_trace(go.Bar(
                    y=[country],
                    x=[data[country]['Personnel']],
                    orientation='h',
                    name=country,                   # gives you a legend entry
                    marker_color=colors[i % len(colors)],
                    width=0.25
                ))
            
            fig_pers.update_layout(
                title="Personnel Strength",
                xaxis_title="Number of Personnel",
                yaxis_title="Country",
                barmode='stack',                   # or 'group' if you want them side‐by‐side
                template="plotly_white",
                margin=dict(l=80, r=20, t=40, b=40),
                legend=dict(title="Country")
            )

            st.plotly_chart(fig_pers, use_container_width=True)

            # 2) Tanks vs Fighter Aircraft — grouped horizontal bars
            cats = ["Tanks", "Fighter Aircraft"]
            fig_eq = go.Figure()
            for country in data:
                fig_eq.add_trace(go.Bar(
                    y=cats,
                    x=[data[country][cat] for cat in cats],
                    orientation='h',
                    name=country,
                    width=0.25
                ))
            fig_eq.update_layout(
                barmode='group',
                title="Armored & Air Strength",
                xaxis_title="Count",
                yaxis_title="Equipment Type",
                template="plotly_white",
                margin=dict(l=100, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_eq, use_container_width=True)

        else:
            st.info("🪖 Data not available for this conflict.")

    # --- Tab 3: Conflict Map Animation ---
    else:
        st.subheader("🗺️ Conflict Map & 5-Step Troop Movements")

        evs = info['events']
        if len(evs) >= 5:
            idxs = np.linspace(0, len(evs)-1, 5, dtype=int)
            sel_evs = [evs[i] for i in idxs]
        else:
            sel_evs = evs + [{"date":"","event":""}]*(5-len(evs))

        f = info['troop_movements'][0]['from']
        t = info['troop_movements'][0]['to']
        lats = np.linspace(f['lat'], t['lat'], 5)
        lons = np.linspace(f['lon'], t['lon'], 5)
        positions = [{"lat":la, "lon":lo} for la,lo in zip(lats,lons)]

        map_ph = st.empty()
        txt_ph = st.empty()
        play  = st.checkbox("▶️ Play Animation")

        def render(i):
            o = positions[0]
            e = positions[-1]
            layers = []

            # START
            df_s = pd.DataFrame([{
                "lat": o["lat"], "lon": o["lon"],
                "label": f"🟢 Start — {get_location_name(o['lat'], o['lon'])}"
            }])
            layers.append(pdk.Layer("ScatterplotLayer", data=df_s,
                get_position='[lon, lat]', get_color=[0,255,0], get_radius=30000, pickable=True
            ))

            # END
            df_e = pd.DataFrame([{
                "lat": e["lat"], "lon": e["lon"],
                "label": f"🔴 End — {get_location_name(e['lat'], e['lon'])}"
            }])
            layers.append(pdk.Layer("ScatterplotLayer", data=df_e,
                get_position='[lon, lat]', get_color=[255,0,0], get_radius=30000, pickable=True
            ))

            # intermediate route segment
            if i>0:
                segment = pd.DataFrame([{
                    "start_lon": positions[i-1]['lon'], "start_lat": positions[i-1]['lat'],
                    "end_lon": positions[i]['lon'],     "end_lat": positions[i]['lat']
                }])
                layers.append(pdk.Layer("LineLayer", data=segment,
                    get_source_position="[start_lon, start_lat]",
                    get_target_position="[end_lon, end_lat]",
                    get_width=4, get_color=[0,0,0]
                ))

            # moving marker
            cur = positions[i]
            df_m = pd.DataFrame([{
                "lat": cur['lat'], "lon": cur['lon'],
                "label": f"🔵 {sel_evs[i]['date']}"
            }])
            layers.append(pdk.Layer("ScatterplotLayer", data=df_m,
                get_position='[lon, lat]', get_color=[0,0,255], get_radius=20000, pickable=True
            ))

            # fixed checkpoints
            if war in additional_movements:
                layers.append(pdk.Layer("ScatterplotLayer",
                    data=pd.DataFrame(additional_movements[war]),
                    get_position='[lon, lat]',
                    get_color=[0,200,200], get_radius=15000, pickable=True
                ))

            center = np.mean([[p['lat'],p['lon']] for p in positions], axis=0)
            deck = pdk.Deck(
                map_style="mapbox://styles/mapbox/satellite-streets-v11",
                initial_view_state=pdk.ViewState(
                    latitude=center[0], longitude=center[1], zoom=5, pitch=45
                ),
                layers=layers,
                tooltip={"text":"{label}"}
            )
            map_ph.pydeck_chart(deck)
            txt_ph.markdown(f"**{sel_evs[i]['date']}** — {sel_evs[i]['event']}")

        st.markdown("""
        <div style="background:#fff;padding:8px;border-radius:4px;display:inline-block;">
          <span style="color:green;">🟢 Start</span>  
          <span style="color:red;">🔴 End</span>  
          <span style="color:blue;">🔵 Current</span>  
          <span style="color:black;">— Route</span>
        </div>""", unsafe_allow_html=True)

        if play:
            for i in range(5):
                render(i)
                time.sleep(1)
        else:
            step = st.slider("Step", 0, 4, 0)
            render(step)
        
        st.markdown("### 🏁 Outcome")
        for line in info['outcome'].split(';'):
            st.markdown(f"- {line.strip()}")
        
st.markdown("---")
st.caption("📊 Data Sources: SIPRI, MoD India, Wikipedia, GlobalSecurity.org")
