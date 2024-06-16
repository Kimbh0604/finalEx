import streamlit as st
import json
import google.generativeai as genai
import requests
import re

API_KEY = 'AIzaSyAiNrpvUeg5vsw5ZjnaDGLr5gWekEe3PAI'
AMADEUS_API_KEY = 'RnSXqTF5s7xLzdl7YqrzhX539la5gfA6'
AMADEUS_API_SECRET = 'VeD4G0kjjwcz0zOC'

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')


def gemini_recommend(user_data):
    response = model.generate_content(
        f"trip style : {user_data['preferences']}\n"
        f"activities : {', '.join(user_data['activities'])}\n"
        "위 정보를 바탕으로 마크다운 방식으로 여행지 5개를 추천해줘. 답변은 먼저 나라, 도시 이름을 적어주고 공항 코드를 알려줘. 또 옆에 부가 설명을 적어주는데, 사용자가 선택한 태그 위주로 설명해줘. 답변 ~~임, ~~함 말투 쓰지 말고 ~~에요 이런식으로 해줘"
    )

    response_text = str(response)

    airport_code_pattern = re.compile(r'\b[A-Z]{3}\b')
    airport_codes = airport_code_pattern.findall(response_text)

    recommendations = []
    try:
        for line in response_text.split('\n'):
            if re.match(r'^\d+\.\s', line):
                recommendations.append(line.strip())
        recommendations = json.loads(response.text).get('recommendations', [])

    except json.JSONDecodeError:
        recommendations = response.text.split('\n')

    with open('airport_codes.json', 'w', encoding='utf-8') as f:
        json.dump({"airport_codes": airport_codes}, f, ensure_ascii=False, indent=4)

    return recommendations



def amadeus_access():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")


def flight_prices(destination, departure_date, return_date):
    access_token = amadeus_access()
    url = f"https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "originLocationCode": "ICN",
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "returnDate": return_date,
        "adults": 1,
        "nonStop": 'false',  # boolean으로 변환합니다
        "max": 5
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching flight prices: {response.status_code}, {response.text}")
        return None


def parse_ai_response(response):
    lines = response.split("\n")
    locations = [line.split(': ')[1].strip() for line in lines if line.startswith('- ')]
    return locations


# IATA 공항 코드 매핑 함수
def get_iata_code(city_name):
    iata_codes = {
        "Amsterdam": "AMS",
        "Athens": "ATH",
        "Bangkok": "BKK",
        "Barcelona": "BCN",
        "Beijing": "PEK",
        "Berlin": "BER",
        "Bogota": "BOG",
        "Boston": "BOS",
        "Brisbane": "BNE",
        "Brussels": "BRU",
        "Buenos Aires": "EZE",
        "Cairo": "CAI",
        "Cape Town": "CPT",
        "Chicago": "ORD",
        "Copenhagen": "CPH",
        "Dallas": "DFW",
        "Delhi": "DEL",
        "Dubai": "DXB",
        "Dublin": "DUB",
        "Frankfurt": "FRA",
        "Firenze": "FLR",
        "Geneva": "GVA",
        "Guangzhou": "CAN",
        "Hanoi": "HAN",
        "Hong Kong": "HKG",
        "Houston": "IAH",
        "Istanbul": "IST",
        "Jakarta": "CGK",
        "Johannesburg": "JNB",
        "Kuala Lumpur": "KUL",
        "Lagos": "LOS",
        "Lima": "LIM",
        "Lisbon": "LIS",
        "London": "LHR",
        "Los Angeles": "LAX",
        "Madrid": "MAD",
        "Manila": "MNL",
        "Melbourne": "MEL",
        "Mexico City": "MEX",
        "Miami": "MIA",
        "Milan": "MXP",
        "Montreal": "YUL",
        "Moscow": "SVO",
        "Mumbai": "BOM",
        "Munich": "MUC",
        "New York": "JFK",
        "Osaka": "KIX",
        "Paris": "CDG",
        "Prague": "PRG",
        "Rio de Janeiro": "GIG",
        "Rome": "FCO",
        "San Francisco": "SFO",
        "Santiago": "SCL",
        "Sao Paulo": "GRU",
        "Seoul": "ICN",
        "Shanghai": "PVG",
        "Singapore": "SIN",
        "Stockholm": "ARN",
        "Sydney": "SYD",
        "Taipei": "TPE",
        "Tel Aviv": "TLV",
        "Tokyo": "NRT",
        "Toronto": "YYZ",
        "Vancouver": "YVR",
        "Vienna": "VIE",
        "Warsaw": "WAW",
        "Washington D.C.": "IAD",
        "Zurich": "ZRH",
        "Auckland": "AKL",
        "Bangalore": "BLR",
        "Bogotá": "BOG",
        "Brussels": "BRU",
        "Copenhagen": "CPH",
        "Doha": "DOH",
        "Edinburgh": "EDI",
        "Fukuoka": "FUK",
        "Hamburg": "HAM",
        "Helsinki": "HEL",
        "Kolkata": "CCU",
        "Lyon": "LYS",
        "Madrid": "MAD",
        "Manchester": "MAN",
        "Manila": "MNL",
        "Munich": "MUC",
        "Nice": "NCE",
        "Oslo": "OSL",
        "Perth": "PER",
        "Riyadh": "RUH",
        "Sapporo": "CTS",
        "Stuttgart": "STR",
        "Vienna": "VIE",
        "Zurich": "ZRH",
        "Abu Dhabi": "AUH",
        "Anchorage": "ANC",
        "Bahrain": "BAH",
        "Charlotte": "CLT",
        "Denver": "DEN",
        "Detroit": "DTW",
        "Hawaii": "HNL",
        "Las Vegas": "LAS",
        "Newark": "EWR",
        "Orlando": "MCO",
        "Phoenix": "PHX",
        "Salt Lake City": "SLC",
        "San Diego": "SAN",
        "Tampa": "TPA",
        "Addis Ababa": "ADD",
        "Algiers": "ALG",
        "Asuncion": "ASU",
        "Athens": "ATH",
        "Baghdad": "BGW",
        "Baku": "GYD",
        "Bamako": "BKO",
        "Bangui": "BGF",
        "Beirut": "BEY",
        "Belgrade": "BEG",
        "Berlin": "TXL",
        "Bishkek": "FRU",
        "Bridgetown": "BGI",
        "Bucharest": "OTP",
        "Budapest": "BUD",
        "Canberra": "CBR",
        "Caracas": "CCS",
        "Casablanca": "CMN",
        "Chisinau": "KIV",
        "Colombo": "CMB",
        "Conakry": "CKY",
        "Dakar": "DSS",
        "Damascus": "DAM",
        "Dhaka": "DAC",
        "Dili": "DIL",
        "Djibouti": "JIB",
        "Dodoma": "DOD",
        "Douala": "DLA",
        "Dublin": "DUB",
        "Freetown": "FNA",
        "Gaborone": "GBE",
        "Georgetown": "GEO",
        "Gitega": "GID",
        "Harare": "HRE",
        "Havana": "HAV",
        "Islamabad": "ISB",
        "Juba": "JUB",
        "Kabul": "KBL",
        "Kampala": "EBB",
        "Kathmandu": "KTM",
        "Khartoum": "KRT",
        "Kigali": "KGL",
        "Kingston": "KIN",
        "Kinshasa": "FIH",
        "Kuwait City": "KWI",
        "Lima": "LIM",
        "Ljubljana": "LJU",
        "Lomé": "LFW",
        "London": "LHR",
        "Luanda": "LAD",
        "Lusaka": "LUN",
        "Majuro": "MAJ",
        "Malabo": "SSG",
        "Malé": "MLE",
        "Managua": "MGA",
        "Manama": "BAH",
        "Maputo": "MPM",
        "Maseru": "MSU",
        "Mbabane": "SHO",
        "Mexico City": "MEX",
        "Minsk": "MSQ",
        "Mogadishu": "MGQ",
        "Monrovia": "ROB",
        "Montevideo": "MVD",
        "Moroni": "HAH",
        "Moscow": "SVO",
        "Muscat": "MCT",
        "N'Djamena": "NDJ",
        "Nairobi": "NBO",
        "Nassau": "NAS",
        "New Delhi": "DEL",
        "Niamey": "NIM",
        "Nouakchott": "NKC",
        "Nuku'alofa": "TBU",
        "Oslo": "OSL",
        "Ottawa": "YOW",
        "Ouagadougou": "OUA",
        "Panama City": "PTY",
        "Paramaribo": "PBM",
        "Paris": "CDG",
        "Phnom Penh": "PNH",
        "Podgorica": "TGD",
        "Port Louis": "MRU",
        "Port Moresby": "POM",
        "Port-au-Prince": "PAP",
        "Porto-Novo": "COO",
        "Praia": "RAI",
        "Pyongyang": "FNJ",
        "Quito": "UIO",
        "Rabat": "RBA",
        "Reykjavik": "KEF",
        "Riga": "RIX",
        "Roseau": "DOM",
        "San José": "SJO",
        "San Juan": "SJU",
        "Sana'a": "SAH",
        "Santo Domingo": "SDQ",
        "São Tomé": "TMS",
        "Sarajevo": "SJJ",
        "Skopje": "SKP",
        "Sofia": "SOF",
        "St. George's": "GND",
        "St. John's": "ANU",
        "Tirana": "TIA",
        "Tripoli": "TIP",
        "Tunis": "TUN",
        "Ulaanbaatar": "ULN",
        "Valletta": "MLA",
        "Victoria": "SEZ",
        "Vilnius": "VNO",
        "Windhoek": "WDH",
        "Yamoussoukro": "ASK",
        "Yaoundé": "NSI",
        "Zagreb": "ZAG"
        # 필요에 따라 더 많은 도시와 공항 코드를 추가합니다
    }
    with open('airport_codes.json', 'r', encoding='utf-8') as f:
        additional_codes = json.load(f).get('airport_codes', [])
        for code in additional_codes:
            if isinstance(code, str):
                iata_codes[code] = code
    return iata_codes.get(city_name, "")

st.set_page_config(page_title="1")

if 'page' not in st.session_state:
    st.session_state.page = 1

if st.session_state.page == 1:
    st.title("반가워요! 😎  \n"
             "여행지를 추천 받아보세요!")
    if st.button('추천 받으러 가기!'):
        st.session_state.page = 2

if st.session_state.page == 2:
    st.title("여행의 목적이 무엇인가요? 🙄")
    options = st.radio("", ["여행은 휴식이지!", "여행왔는데 돌아다녀야지!"])
    if st.button('다음으로 가기'):
        st.session_state.preferences = options
        st.session_state.page = 3

if st.session_state.page == 3:
    st.title("여행 태그를 선택해 보세요!")

    if st.session_state.preferences == "여행은 휴식이지!":
        activities = st.multiselect(
            "마음에 드는 태그를 선택해 보세요!",
            ["음식", "휴식", "문화유산", "자연", "힐링", "온천", "해변", "명상", "역사", "산책", "조용한", "휴양지", "예술", "녹지", "캠핑", "트레킹"]
        )
        if st.button('결과 보기'):
            user_data = {
                "preferences": st.session_state.preferences,
                "activities": activities
            }
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False)
            st.session_state.page = 4

    else:
        activities = st.multiselect(
            "마음에 드는 태그를 선택해 보세요!",
            ["음주", "파티", "클럽", "축제", "라이브쇼", "댄스", "펍", "스키", "서핑", "패러글라이딩", "축구", "모험"]
        )

        if st.button('결과 보기'):
            user_data = {
                "preferences": st.session_state.preferences,
                "activities": activities
            }
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False)
            st.session_state.page = 4

if st.session_state.page == 4:
    st.title("AI의 추천 목록이에요! 😉")

    with open('user_data.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)

    recommendations = gemini_recommend(user_data)
    st.session_state.recommendations = recommendations  # 추천 목록을 세션 상태에 저장

    st.subheader("추천 목록")
    for i, place in enumerate(recommendations):
        st.write(f"{place}")

    if st.button('항공편 알아보기'):
        st.session_state.page = 5

    # 처음 페이지로 다시 돌아가기
    if st.button('돌아가기'):
        st.session_state.page = 1
        st.experimental_rerun()

if st.session_state.page == 5:
    st.title("추천된 여행지로 가는 항공편이에요! ✈️")

    with open('airport_codes.json', 'r', encoding='utf-8') as f:
        airport_codes = json.load(f).get('airport_codes', [])

    departure_date = st.date_input("출국 날짜를 선택하세요")
    return_date = st.date_input("입국 날짜를 선택하세요")

    if st.button('항공편 검색'):
        flight_results = []
        for code in airport_codes:
            result = flight_prices(code, departure_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'))
            if result:
                flight_results.append(result)

        if flight_results:
            st.subheader("항공편 정보")
            for idx, flight in enumerate(flight_results):
                st.write(f"### 항공편 {idx + 1}")
                for offer in flight['data']:
                    st.write(f"- 가격: {offer['price']['total']} {offer['price']['currency']}")
                    st.write(f"- 출발 시간: {offer['itineraries'][0]['segments'][0]['departure']['at']}")
                    st.write(f"- 도착 시간: {offer['itineraries'][0]['segments'][0]['arrival']['at']}")
                    st.write(f"- 항공사: {offer['itineraries'][0]['segments'][0]['carrierCode']}")
                    st.write("")

        else:
            st.error("항공편 정보를 가져오는 데 실패했습니다.")

    # 처음 페이지로 다시 돌아가기
    if st.button('처음으로'):
        st.session_state.page = 1
        st.experimental_rerun()
