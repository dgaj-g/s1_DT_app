#!/usr/bin/env python3
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "supabase" / "seed" / "network_questions.json"
OUT_SQL = ROOT / "supabase" / "seed" / "network_questions.sql"

# Guardrail to stop cyberspace/security/data-transfer content leaking into this topic.
BANNED_SCOPE_TERMS = [
    "firewall",
    "encryption",
    "malware",
    "hacking",
    "phishing",
    "ftp",
    "http",
    "https",
    "levels of access",
    "cyber",
    "password",
    "protocol",
]

BASE_CONCEPTS = [
    {
        "tag": "networking_definition",
        "statement": "Networking links computers/devices so they can share data.",
        "keyword": "networking",
        "answer": "linking devices to share data",
        "accepted": [
            "linking computers to share data",
            "devices share data between them",
            "linking computers that share data",
        ],
        "explanation": "A network is a set of connected devices that can exchange data and resources.",
        "distractors": [
            "storing files on one offline computer",
            "using one device with no connections",
            "deleting data from all devices",
        ],
        "source": "U1 DT 2025 Q8(d) + MS",
    },
    {
        "tag": "lan",
        "statement": "A LAN covers a small geographical area, often one building.",
        "keyword": "LAN",
        "answer": "LAN",
        "accepted": ["local area network"],
        "explanation": "A LAN usually serves a local site such as a school, home, or office building.",
        "distractors": ["WAN", "Ring", "Intranet"],
        "source": "U1 DT 2024 Q1(c) + MS",
    },
    {
        "tag": "wan",
        "statement": "A WAN connects computers over large geographical areas.",
        "keyword": "WAN",
        "answer": "WAN",
        "accepted": ["wide area network"],
        "explanation": "A WAN spans large distances, often connecting sites in different towns or countries.",
        "distractors": ["LAN", "Wired applications network", "World area network"],
        "source": "U1 DT 2024 Q1(b) + MS",
    },
    {
        "tag": "internet_definition",
        "statement": "The internet is a large global network of networks.",
        "keyword": "internet",
        "answer": "global network of networks",
        "accepted": [
            "a large global network of networks",
            "large global network of networks",
        ],
        "explanation": "The internet links many networks together worldwide.",
        "distractors": [
            "collection of linked web pages",
            "private organisational network",
            "single network in one building",
        ],
        "source": "U1 DT 2025 Q8(b) + MS",
    },
    {
        "tag": "www_definition",
        "statement": "The World Wide Web is a collection of linked pages on web servers.",
        "keyword": "World Wide Web",
        "answer": "collection of linked web pages on web servers",
        "accepted": [
            "collection of files on web servers connected by hypertext",
            "linked files on web servers",
        ],
        "explanation": "The web is one service that runs on the internet and provides linked pages.",
        "distractors": [
            "global physical cable backbone",
            "private internal staff network",
            "device-to-device short-range link",
        ],
        "source": "U1 DT 2025 Q8(b) + MS",
    },
    {
        "tag": "internet_vs_www",
        "statement": "The internet is the network; the World Wide Web is an application/service running on it.",
        "keyword": "internet vs world wide web",
        "answer": "internet is network; web is application",
        "accepted": [
            "internet is the network; web is the application",
            "internet is the network and world wide web is the application",
            "internet network and web application",
        ],
        "explanation": "The internet is the infrastructure; the web is one service that uses it.",
        "distractors": [
            "both terms mean exactly the same",
            "internet is only email",
            "web is hardware",
        ],
        "source": "U1 DT 2025 Q8(c) + MS",
    },
    {
        "tag": "intranet",
        "statement": "An intranet is a private organisational network for authorised users.",
        "keyword": "intranet",
        "answer": "private organisational network",
        "accepted": [
            "private network owned and managed by an organisation",
            "private network for employees",
        ],
        "explanation": "An intranet is restricted to authorised people inside an organisation.",
        "distractors": [
            "global public network",
            "large geographical network",
            "wireless headset pairing",
        ],
        "source": "U1 DT 2019 Q6(a)(iii) + MS",
    },
    {
        "tag": "iot",
        "statement": "IoT means physical devices connected to the internet.",
        "keyword": "IoT",
        "answer": "physical devices connected to the internet",
        "accepted": [
            "devices connected to the internet",
            "physical smart devices connected to the internet",
        ],
        "explanation": "IoT refers to connected physical devices such as sensors and smart home equipment.",
        "distractors": [
            "only social media accounts",
            "only desktop computers",
            "printed barcodes on paper",
        ],
        "source": "U1 DT 2025 Q8(a) + MS",
    },
    {
        "tag": "wifi",
        "statement": "Wi-Fi is used for wireless network access in places like homes and schools.",
        "keyword": "Wi-Fi",
        "answer": "wireless network access in homes/schools",
        "accepted": [
            "wireless local network access",
            "connect devices wirelessly to a local network",
        ],
        "explanation": "Wi-Fi provides wireless access to a local network and internet.",
        "distractors": [
            "main cable in a bus network",
            "short-range personal pairing only",
            "light-based long-distance cable system",
        ],
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "bluetooth",
        "statement": "Bluetooth is a short-range wireless technology used to link nearby devices.",
        "keyword": "Bluetooth",
        "answer": "short-range wireless technology",
        "accepted": ["short range wireless communication technology"],
        "explanation": "Bluetooth is commonly used for links such as phone-to-headphones or watch-to-phone.",
        "distractors": [
            "global network of networks",
            "main cable in a bus topology",
            "long-distance fixed cable backbone",
        ],
        "source": "U1 DT 2025 Q8(c) + MS",
    },
    {
        "tag": "optical_fibre_signals",
        "statement": "Optical fibre transmits data as light, not electrical signals.",
        "keyword": "optical fibre",
        "answer": "light signals",
        "accepted": ["data transmitted as light"],
        "explanation": "Fibre-optic cables use pulses of light to carry data.",
        "distractors": ["electrical signals", "magnetic tape", "audio waves"],
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "optical_fibre_bandwidth",
        "statement": "Optical fibre supports high bandwidth.",
        "keyword": "optical fibre bandwidth",
        "answer": "high bandwidth",
        "accepted": ["has a high bandwidth"],
        "explanation": "Fibre is designed to carry large amounts of data quickly.",
        "distractors": ["very low bandwidth", "no data capacity", "text only"],
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "optical_fibre_interference",
        "statement": "Fibre-optic cables are less susceptible to interference.",
        "keyword": "optical fibre interference",
        "answer": "less susceptible to interference",
        "accepted": ["low interference", "less affected by interference"],
        "explanation": "Fibre is less affected by electromagnetic interference than copper cables.",
        "distractors": ["more susceptible to interference", "cannot carry data", "wireless only"],
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "optical_fibre_security",
        "statement": "Data on fibre-optic cable is generally harder to intercept than on copper cable.",
        "keyword": "optical fibre security",
        "answer": "harder to intercept than copper",
        "accepted": ["not easier to intercept than copper", "more secure than copper for interception"],
        "explanation": "Fibre is typically harder to tap without detection than copper cabling.",
        "distractors": [
            "easier to intercept than copper",
            "always publicly broadcast",
            "cannot be made secure",
        ],
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "mobile_5g",
        "statement": "5G is suitable for accessing cloud files while travelling.",
        "keyword": "best medium while travelling",
        "answer": "5G",
        "accepted": ["5g"],
        "explanation": "Mobile broadband such as 5G is used when travelling away from fixed networks.",
        "distractors": ["Bluetooth", "Wi-Fi", "Fibre-optic"],
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "nic",
        "statement": "A NIC is required for a computer to connect and communicate on a network.",
        "keyword": "NIC purpose",
        "answer": "connect to and communicate on a network",
        "accepted": [
            "allows device to connect to a network",
            "network connection and communication",
        ],
        "explanation": "A network interface card provides the hardware interface for network access.",
        "distractors": ["stores shared files", "prints paper documents", "creates topology diagrams"],
        "source": "U1 DT 2023 Q7(e) + MS",
    },
    {
        "tag": "switch",
        "statement": "A switch connects devices in a LAN and forwards data to the destination device.",
        "keyword": "switch function",
        "answer": "connects devices in a lan and forwards data",
        "accepted": [
            "connects devices within one network and forwards data",
            "forwards packets within a lan",
        ],
        "explanation": "A switch operates inside a LAN, sending traffic to the correct destination.",
        "distractors": ["connects countries globally", "stores files for all users", "creates wireless signals only"],
        "source": "U1 DT 2021 Q6(1) + MS",
    },
    {
        "tag": "router",
        "statement": "A router connects networks and forwards packets between them.",
        "keyword": "router function",
        "answer": "connects networks and routes packets",
        "accepted": [
            "joins two or more networks",
            "forwards packets from one network to another",
        ],
        "explanation": "Routers direct traffic between networks, including between a LAN and the internet.",
        "distractors": ["joins nodes to one backbone cable", "stores documents centrally", "acts as a workstation"],
        "source": "U1 DT 2021 Q6(2), 2023 Q6(b) + MS",
    },
    {
        "tag": "file_server",
        "statement": "A file server stores and provides shared files on a network.",
        "keyword": "file server purpose",
        "answer": "stores shared files for network users",
        "accepted": [
            "central file storage for users",
            "holds shared files that users can access",
        ],
        "explanation": "A file server gives centralised access to shared resources in a network.",
        "distractors": ["routes internet packets", "ends a bus cable", "pairs bluetooth accessories"],
        "source": "U1 DT 2021 Q6(1) + MS",
    },
    {
        "tag": "ethernet_switch",
        "statement": "On a wired network, each device connects to a switch using Ethernet cables.",
        "keyword": "wired LAN setup",
        "answer": "wired connection to switch",
        "accepted": [
            "devices connect to a switch with ethernet cables",
            "ethernet cable to switch",
        ],
        "explanation": "In wired LANs, Ethernet cabling links network devices to switches.",
        "distractors": ["wireless-only satellite link", "single global internet cable", "social media platform"],
        "source": "U1 DT 2023 Q6(b) + MS",
    },
    {
        "tag": "network_advantages",
        "statement": "Networking allows sharing of files, hardware, software, and communication.",
        "keyword": "network advantages",
        "answer": "share files hardware and communication",
        "accepted": [
            "share files and hardware",
            "share software and communicate",
            "access files from any networked computer",
        ],
        "explanation": "Typical network benefits are resource sharing and easier collaboration.",
        "distractors": ["eliminates all maintenance", "removes all failures", "prevents updates"],
        "source": "U1 DT 2019 Q6(a)(ii), 2025 Q8(d) + MS",
    },
    {
        "tag": "bus_topology",
        "statement": "In a bus network, all nodes connect to one backbone cable.",
        "keyword": "bus topology structure",
        "answer": "all nodes connect to one backbone cable",
        "accepted": ["single backbone cable with connected nodes"],
        "explanation": "Bus topology uses one main cable shared by all connected nodes.",
        "distractors": ["all nodes connect to central switch", "nodes connect in a closed ring", "every node connects to every node"],
        "source": "U1 DT 2023 Q7(b)(i), Q7(c) + MS",
    },
    {
        "tag": "bus_disadvantage",
        "statement": "If the backbone cable fails in a bus topology, network communication fails.",
        "keyword": "bus topology disadvantages",
        "answer": "if backbone cable fails network fails",
        "accepted": [
            "main cable break stops network",
            "if bus cable breaks communication breaks down",
        ],
        "explanation": "A single backbone fault can stop communication for the whole bus network.",
        "distractors": [
            "one cable fault affects only one workstation",
            "no collisions occur",
            "performance always improves with more nodes",
        ],
        "source": "U1 DT 2023 Q7(b)(ii) + MS",
    },
    {
        "tag": "backbone",
        "statement": "The backbone is the main cable in a bus network.",
        "keyword": "backbone",
        "answer": "main cable in bus network",
        "accepted": ["main cable", "bus main cable"],
        "explanation": "All devices in a bus topology connect to the backbone cable.",
        "distractors": ["central server in star", "ring token", "wireless hotspot"],
        "source": "U1 DT 2023 Q7(b)(iii), 2025 Q13 + MS",
    },
    {
        "tag": "terminator",
        "statement": "Terminators prevent signal bounce on a bus backbone.",
        "keyword": "terminator purpose",
        "answer": "stop signal bounce on bus cable",
        "accepted": [
            "stops signal returning down the backbone",
            "absorbs signal to reduce collisions",
        ],
        "explanation": "Terminators absorb signals at cable ends to reduce distortion and data loss.",
        "distractors": ["increases bluetooth range", "stores user files", "converts bus to ring"],
        "source": "U1 DT 2023 Q7(b)(iii) + MS",
    },
    {
        "tag": "ring_topology",
        "statement": "In a ring topology, data passes from one workstation/node to another.",
        "keyword": "ring topology",
        "answer": "data passes from one node/workstation to another",
        "accepted": [
            "data passes workstation to workstation",
            "data travels around the ring through each node",
        ],
        "explanation": "Ring topology sends data around the loop via each connected node.",
        "distractors": ["all devices connect to central switch", "all devices share one backbone only", "no cables are used"],
        "source": "U1 DT 2023 Q7(c), 2022 Q7(a) + MS",
    },
    {
        "tag": "ring_disadvantage",
        "statement": "In a ring network, failure of a cable or node can disrupt the whole network.",
        "keyword": "ring disadvantage",
        "answer": "cable or node failure can disrupt whole ring",
        "accepted": [
            "if cable or node fails whole ring can fail",
            "single cable/node fault can stop network",
        ],
        "explanation": "Because traffic depends on the loop path, one fault can break communication.",
        "distractors": [
            "a fault affects only one workstation",
            "there is always a central controller",
            "new nodes never cause disruption",
        ],
        "source": "U1 DT 2022 Q7(a)(ii) + MS",
    },
    {
        "tag": "star_topology",
        "statement": "In a star topology, all devices connect to a central server/switch/hub.",
        "keyword": "star topology structure",
        "answer": "all devices connect to central server/switch/hub",
        "accepted": [
            "devices connect to central switch",
            "central device with individual links",
        ],
        "explanation": "Star networks use a central point with separate links to each workstation.",
        "distractors": ["devices connect in one circle", "devices share one backbone cable", "no central device is used"],
        "source": "U1 DT 2019 Q6(d)(i), 2024 Q6(a) + MS",
    },
    {
        "tag": "star_advantage",
        "statement": "In a star network, one workstation failure usually does not stop others.",
        "keyword": "star advantage",
        "answer": "if one workstation fails others can continue",
        "accepted": [
            "single workstation failure is isolated",
            "one node failure does not stop whole network",
        ],
        "explanation": "Separate links mean faults are often isolated to one device connection.",
        "distractors": [
            "one workstation failure stops all devices",
            "new workstations cannot be added",
            "star has no performance benefits",
        ],
        "source": "U1 DT 2024 Q6(a), 2019 Q6(d)(ii) + MS",
    },
    {
        "tag": "star_disadvantage",
        "statement": "If the central device in a star network fails, the network can fail.",
        "keyword": "star disadvantage",
        "answer": "if central device fails network fails",
        "accepted": [
            "central server/switch failure stops network",
            "central point is single point of failure",
        ],
        "explanation": "The central switch/server is a dependency in star topology.",
        "distractors": ["no cabling cost", "cannot connect printers", "no setup required"],
        "source": "U1 DT 2019 Q6(d)(iii), 2024 Q6(a) + MS",
    },
    {
        "tag": "bus_diagram_components",
        "statement": "A correct bus diagram shows nodes/workstations, a backbone cable, and two terminators.",
        "keyword": "labels on a bus network diagram",
        "answer": "nodes + backbone cable + two terminators",
        "accepted": [
            "nodes and backbone with terminators at both ends",
            "workstations connected to backbone with two terminators",
        ],
        "explanation": "A correct bus diagram includes nodes/workstations, one backbone cable, and terminators at both ends.",
        "distractors": ["router and cloud only", "single workstation only", "star diagram with central switch"],
        "source": "U1 DT 2023 Q7(c) + MS",
        "mcq_prompts": [
            "Which option lists labels you would find on a bus network diagram?",
            "Choose the option that matches a correctly labelled bus network diagram.",
            "Which option shows the essential labels for a bus network diagram?",
        ],
    },
    {
        "tag": "topology_ring_name",
        "statement": "A topology where computers form a closed loop is called a ring.",
        "keyword": "name of closed-loop topology",
        "answer": "ring",
        "accepted": ["ring topology"],
        "explanation": "In ring topology, each node is connected in a closed path.",
        "distractors": ["bus", "star", "lan"],
        "source": "U1 DT 2022 Q7(a)(i) + MS",
    },
    {
        "tag": "topology_bus_name",
        "statement": "A topology with one backbone cable and terminators is called a bus network.",
        "keyword": "name of backbone topology",
        "answer": "bus",
        "accepted": ["bus topology", "bus network"],
        "explanation": "Bus topology is identified by a shared backbone cable.",
        "distractors": ["ring", "star", "wan"],
        "source": "U1 DT 2023 Q7(b)(i) + MS",
    },
    {
        "tag": "topology_star_name",
        "statement": "A topology with one central switch/server connected to each workstation is called star.",
        "keyword": "name of central-device topology",
        "answer": "star",
        "accepted": ["star topology", "star network"],
        "explanation": "Star topology uses a central node and separate device links.",
        "distractors": ["ring", "bus", "mesh"],
        "source": "U1 DT 2019 Q6(d)(i), 2024 Q6(a) + MS",
    },
    {
        "tag": "media_headphones",
        "statement": "Connecting a mobile phone to wireless headphones uses Bluetooth.",
        "keyword": "connecting a phone to wireless headphones",
        "answer": "Bluetooth",
        "accepted": ["bluetooth"],
        "explanation": "Bluetooth is the expected short-range medium for personal peripherals.",
        "distractors": ["Wi-Fi", "5G", "Fibre-optic"],
        "source": "U1 DT 2023 Q6(a) + MS",
        "mcq_prompts": [
            "Which option is best for connecting a phone to wireless headphones?",
            "Choose the correct option for connecting a phone to wireless headphones.",
            "Which option correctly matches this task: phone to wireless headphones?",
        ],
    },
    {
        "tag": "media_business_lan_internet",
        "statement": "Connecting a business LAN to the internet commonly uses fibre-optic infrastructure.",
        "keyword": "connecting a business LAN to the internet",
        "answer": "Fibre-optic",
        "accepted": ["fibre-optic", "fibre optic"],
        "explanation": "Fibre-optic links are commonly used for high-capacity fixed internet connections.",
        "distractors": ["Bluetooth", "Wi-Fi", "5G"],
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "media_smart_tv_home",
        "statement": "Connecting a smart TV to a home network typically uses Wi-Fi.",
        "keyword": "connecting a smart TV to a home network",
        "answer": "Wi-Fi",
        "accepted": ["wi-fi", "wifi"],
        "explanation": "A home smart TV usually joins the home LAN through Wi-Fi.",
        "distractors": ["Bluetooth", "5G", "Fibre-optic"],
        "source": "U1 DT 2023 Q6(a) + MS",
    },
]

CONCEPT_BY_TAG = {concept["tag"]: concept for concept in BASE_CONCEPTS}

FILL_GAP_ITEMS = [
    {"tag": "lan", "stem": "Fill the gap: A ____ covers a small geographical area such as one building.", "accepted": ["LAN", "local area network"]},
    {"tag": "wan", "stem": "Fill the gap: A ____ connects networks across a large geographical area.", "accepted": ["WAN", "wide area network"]},
    {"tag": "internet_definition", "stem": "Fill the gap: The internet is a global network of ____.", "accepted": ["networks", "networks of networks"]},
    {"tag": "intranet", "stem": "Fill the gap: An intranet is a ____ organisational network.", "accepted": ["private"]},
    {"tag": "iot", "stem": "Fill the gap: IoT refers to ____ devices connected to the internet.", "accepted": ["physical", "smart", "physical smart"]},
    {"tag": "bluetooth", "stem": "Fill the gap: Bluetooth is a ____-range wireless technology.", "accepted": ["short", "short-range", "short range"]},
    {"tag": "wifi", "stem": "Fill the gap: A smart TV usually connects to a home network using ____.", "accepted": ["Wi-Fi", "WiFi", "wifi", "wireless"]},
    {"tag": "optical_fibre_signals", "stem": "Fill the gap: Fibre-optic cables carry data as ____ signals.", "accepted": ["light", "light signals", "pulses of light"]},
    {"tag": "optical_fibre_bandwidth", "stem": "Fill the gap: Fibre-optic cable has ____ bandwidth.", "accepted": ["high"]},
    {"tag": "optical_fibre_interference", "stem": "Fill the gap: Fibre-optic cable is less susceptible to ____.", "accepted": ["interference"]},
    {"tag": "optical_fibre_security", "stem": "Fill the gap: Data on fibre is generally ____ to intercept than copper.", "accepted": ["harder", "more difficult"]},
    {"tag": "mobile_5g", "stem": "Fill the gap: Accessing company files while travelling often uses ____.", "accepted": ["5G", "5g", "5 g"]},
    {"tag": "router", "stem": "Fill the gap: A ____ connects a LAN to the internet.", "accepted": ["router"]},
    {"tag": "ethernet_switch", "stem": "Fill the gap: On a wired LAN, each device connects to a ____ using Ethernet cables.", "accepted": ["switch", "network switch"]},
    {"tag": "nic", "stem": "Fill the gap: A NIC allows a device to ____ and communicate on a network.", "accepted": ["connect", "join"]},
    {"tag": "backbone", "stem": "Fill the gap: In a bus topology, the main cable is called the ____.", "accepted": ["backbone", "backbone cable"]},
    {"tag": "terminator", "stem": "Fill the gap: A ____ is fitted at each end of a bus cable.", "accepted": ["terminator", "terminators"]},
    {"tag": "topology_ring_name", "stem": "Fill the gap: A closed-loop network is a ____ topology.", "accepted": ["ring"]},
    {"tag": "topology_bus_name", "stem": "Fill the gap: A network with one backbone cable is a ____ topology.", "accepted": ["bus"]},
    {"tag": "topology_star_name", "stem": "Fill the gap: A network with one central connection point is a ____ topology.", "accepted": ["star"]},
    {"tag": "network_advantages", "stem": "Fill the gap: One advantage of networking is ____ files and hardware.", "accepted": ["sharing", "share"]},
    {"tag": "ring_topology", "stem": "Fill the gap: In a ring network, data passes from one ____ to another.", "accepted": ["node", "workstation", "device"]},
]

EASY_MATCH_SETS = [
    {
        "tag": "easy_match_media",
        "left": [
            "Connect phone to wireless headphones",
            "Access cloud files while travelling",
            "Connect a smart TV to home network",
            "Connect business LAN to internet",
        ],
        "right": ["Bluetooth", "5G", "Wi-Fi", "Fibre-optic"],
        "choices": ["Bluetooth", "5G", "Wi-Fi", "Fibre-optic"],
        "explanation": "Phone-headphones uses Bluetooth, travelling cloud access uses 5G, home smart TV uses Wi-Fi, and business LAN internet often uses fibre.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "easy_match_terms",
        "left": ["LAN", "WAN", "Internet", "Intranet"],
        "right": [
            "Small geographical network",
            "Large geographical network",
            "Global network of networks",
            "Private organisational network",
        ],
        "choices": [
            "Small geographical network",
            "Large geographical network",
            "Global network of networks",
            "Private organisational network",
            "Collection of linked pages",
        ],
        "explanation": "LAN and WAN are network sizes, internet is global public infrastructure, and intranet is private organisational access.",
        "source": "U1 DT 2019 Q6(a), 2024 Q1(b)(c), 2025 Q8(b) + MS",
    },
    {
        "tag": "easy_match_device_roles",
        "left": [
            "Connects networks",
            "Connects devices in one LAN",
            "Lets a computer join a network",
            "Stores shared files",
        ],
        "right": ["Router", "Switch", "NIC", "File server"],
        "choices": ["Router", "Switch", "NIC", "File server", "Terminator"],
        "explanation": "Router joins networks, switch manages LAN traffic, NIC enables connection, and file server stores shared files.",
        "source": "U1 DT 2021 Q6, 2023 Q6(b), 2023 Q7(e) + MS",
    },
    {
        "tag": "easy_match_fibre_true_false",
        "left": [
            "Fibre has high bandwidth",
            "Fibre transmits data as electrical signals",
            "Fibre is less susceptible to interference",
            "Fibre data is easier to intercept than copper",
        ],
        "right": ["True", "False", "True", "False"],
        "choices": ["True", "False"],
        "explanation": "CCEA fibre facts: high bandwidth, light transmission, lower interference, and not easier to intercept than copper.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "easy_match_topology",
        "left": [
            "Devices connect to one central point",
            "All nodes share one backbone cable",
            "Devices form a closed loop",
            "Terminators needed at both ends",
        ],
        "right": ["Star", "Bus", "Ring", "Bus"],
        "choices": ["Star", "Bus", "Ring", "LAN"],
        "explanation": "Star means central point; bus means shared backbone and terminators; ring means closed loop.",
        "source": "U1 DT 2019 Q6, 2022 Q7(a), 2023 Q7(b)(c), 2024 Q6(a) + MS",
    },
]

MEDIUM_MATCH_SETS = [
    {
        "tag": "medium_match_topology_effects",
        "left": [
            "Backbone cable fails",
            "Single workstation fails in star",
            "Central device fails in star",
            "Cable/node fails in ring",
        ],
        "right": [
            "Bus communication fails",
            "Other nodes usually continue",
            "Whole star may stop",
            "Ring can be disrupted",
        ],
        "choices": [
            "Bus communication fails",
            "Other nodes usually continue",
            "Whole star may stop",
            "Ring can be disrupted",
            "No effect on any topology",
        ],
        "explanation": "Bus depends on its backbone, star isolates single workstation faults but depends on the central device, and ring can be disrupted by single faults.",
        "source": "U1 DT 2019 Q6(d), 2022 Q7(a), 2023 Q7(b), 2024 Q6(a) + MS",
    },
    {
        "tag": "medium_match_bus_parts",
        "left": [
            "Main cable",
            "End component",
            "Connected device",
            "Typical issue if overloaded",
        ],
        "right": ["Backbone", "Terminator", "Node/Workstation", "Collisions"],
        "choices": ["Backbone", "Terminator", "Node/Workstation", "Collisions", "Switch"],
        "explanation": "A bus network uses a backbone with terminators, connected nodes, and can suffer collisions.",
        "source": "U1 DT 2023 Q7(b)(c) + MS",
    },
    {
        "tag": "medium_match_internet_www",
        "left": [
            "Global network of networks",
            "Collection of linked web pages",
            "Private organisational network",
            "Physical connected devices online",
        ],
        "right": ["Internet", "WWW", "Intranet", "IoT"],
        "choices": ["Internet", "WWW", "Intranet", "IoT", "LAN"],
        "explanation": "Internet is infrastructure, WWW is service/content, intranet is private, and IoT is connected physical devices.",
        "source": "U1 DT 2025 Q8(a)(b)(c) + MS",
    },
    {
        "tag": "medium_match_media_scenarios",
        "left": [
            "Watch to smartphone",
            "Smart TV to home router",
            "Travelling user to cloud",
            "Business LAN to internet",
        ],
        "right": ["Bluetooth", "Wi-Fi", "5G", "Fibre-optic"],
        "choices": ["Bluetooth", "Wi-Fi", "5G", "Fibre-optic", "Backbone"],
        "explanation": "Each scenario maps to the most suitable communication medium from CCEA-style questions.",
        "source": "U1 DT 2023 Q6(a), 2025 Q8(c) + MS",
    },
    {
        "tag": "medium_match_device_jobs",
        "left": [
            "Sends LAN data to destination device",
            "Forwards data between networks",
            "Allows physical/wireless network interface",
            "Provides central file storage",
        ],
        "right": ["Switch", "Router", "NIC", "File server"],
        "choices": ["Switch", "Router", "NIC", "File server", "Terminator"],
        "explanation": "Switch, router, NIC, and file server all play separate roles in network operation.",
        "source": "U1 DT 2021 Q6, 2023 Q6(b), 2023 Q7(e) + MS",
    },
]

EXPERT_MATCH_SETS = [
    {
        "tag": "expert_match_failure_reasoning",
        "left": [
            "One workstation fails, others still run",
            "All communication stops after one main cable break",
            "No central controller, node fault disrupts traffic",
            "Central device failure causes full outage",
        ],
        "right": ["Star advantage", "Bus disadvantage", "Ring disadvantage", "Star disadvantage"],
        "choices": ["Star advantage", "Bus disadvantage", "Ring disadvantage", "Star disadvantage", "WAN advantage"],
        "explanation": "These are standard topology reasoning points from CCEA mark schemes.",
        "source": "U1 DT 2019 Q6, 2022 Q7(a), 2024 Q6(a) + MS",
    },
    {
        "tag": "expert_match_diagram_roles",
        "left": [
            "Main cable in a bus diagram",
            "Label at each bus cable end",
            "Central device in star diagram",
            "Network card in a workstation",
        ],
        "right": ["Backbone", "Terminator", "Switch/Server", "NIC"],
        "choices": ["Backbone", "Terminator", "Switch/Server", "NIC", "WAN"],
        "explanation": "Correct diagram labels depend on topology structure and device function.",
        "source": "U1 DT 2019 Q6(d), 2023 Q7(c), 2025 Q13 + MS",
    },
    {
        "tag": "expert_match_inference",
        "left": [
            "Carries data as light",
            "Supports high bandwidth",
            "Lower interference risk",
            "Harder to intercept than copper",
        ],
        "right": ["Fibre-optic", "Fibre-optic", "Fibre-optic", "Fibre-optic"],
        "choices": ["Fibre-optic", "Bluetooth", "Wi-Fi", "5G"],
        "explanation": "All four statements are fibre-optic properties from the CCEA true/false style content.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "expert_match_task_selection",
        "left": [
            "Staff-only internal website",
            "Global public infrastructure",
            "Linked pages viewed in browser",
            "Physical connected devices",
        ],
        "right": ["Intranet", "Internet", "WWW", "IoT"],
        "choices": ["Intranet", "Internet", "WWW", "IoT", "LAN"],
        "explanation": "These terms are often confused, so expert level requires precise distinction.",
        "source": "U1 DT 2019 Q6(a)(iii), 2025 Q8(a)(b)(c) + MS",
    },
    {
        "tag": "expert_match_network_design",
        "left": [
            "Connect mobile phone to wireless headphones",
            "Connect smart TV to home network",
            "Access company files while travelling",
            "Connect business LAN to internet",
        ],
        "right": ["Bluetooth", "Wi-Fi", "5G", "Fibre-optic"],
        "choices": ["Bluetooth", "Wi-Fi", "5G", "Fibre-optic", "Terminator"],
        "explanation": "Expert level still uses objective mapping, but with realistic mixed scenarios.",
        "source": "U1 DT 2023 Q6(a), 2025 Q8(c) + MS",
    },
]

MEDIUM_DRAG_SETS = [
    {
        "tag": "drag_web_request_path",
        "stem": "Order the typical path from a school workstation to a web server.",
        "order": ["Workstation/NIC", "Switch", "Router", "Internet", "Web server"],
        "explanation": "A typical request leaves the LAN via switch and router before reaching internet services.",
        "source": "Network_Technologies_Notes.docx + U1 DT 2021 Q6 + MS",
    },
    {
        "tag": "drag_bluetooth_pairing",
        "stem": "Order a common Bluetooth pairing sequence.",
        "order": [
            "Enable Bluetooth on both devices",
            "Search for nearby devices",
            "Select the target device",
            "Confirm pairing code",
            "Start audio/data transfer",
        ],
        "explanation": "Bluetooth communication starts only after successful pairing.",
        "source": "U1 DT 2025 Q8(c) + Notes",
    },
    {
        "tag": "drag_bus_setup",
        "stem": "Order the setup steps for a basic bus network.",
        "order": [
            "Lay backbone cable",
            "Connect nodes/workstations",
            "Attach terminators at both ends",
            "Test communication",
        ],
        "explanation": "Terminators must be fitted before final communication testing.",
        "source": "U1 DT 2023 Q7(c), 2025 Q13 + MS",
    },
    {
        "tag": "drag_ring_flow",
        "stem": "Order what happens when data travels on a ring network.",
        "order": [
            "Source workstation sends data",
            "Data moves to the next node",
            "Data continues around the ring",
            "Destination workstation receives data",
        ],
        "explanation": "Ring traffic passes through nodes around the loop to reach the destination.",
        "source": "U1 DT 2022 Q7(a), 2023 Q7(c) + MS",
    },
    {
        "tag": "drag_star_checks",
        "stem": "Order a simple star-network setup and check routine.",
        "order": [
            "Connect each workstation to central switch/server",
            "Verify each cable connection",
            "Test communication from each workstation",
            "Simulate one workstation failure to check isolation",
        ],
        "explanation": "Star networks should keep working if one workstation fails.",
        "source": "U1 DT 2024 Q6(a), 2019 Q6(d) + MS",
    },
    {
        "tag": "drag_wired_lan",
        "stem": "Order the main steps for connecting a new wired workstation to a LAN.",
        "order": [
            "Install/enable NIC",
            "Connect Ethernet cable",
            "Plug into switch",
            "Test network communication",
        ],
        "explanation": "A wired LAN connection needs a NIC and Ethernet link to a switch before communication tests.",
        "source": "U1 DT 2023 Q6(b), Q7(e) + MS",
    },
    {
        "tag": "drag_cloud_travel",
        "stem": "Order the best process for accessing company cloud files while travelling.",
        "order": [
            "Enable mobile data",
            "Connect to 5G service",
            "Open cloud service",
            "Download or edit required files",
        ],
        "explanation": "Travelling access normally depends on mobile data such as 5G before cloud access.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "drag_smart_tv_home",
        "stem": "Order the steps to connect a smart TV to a home network.",
        "order": [
            "Turn on Wi-Fi on the TV",
            "Select home network SSID",
            "Enter network credentials",
            "Confirm connection and test streaming",
        ],
        "explanation": "Home smart TV networking is a Wi-Fi connection process followed by connectivity testing.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "drag_bus_fault",
        "stem": "Order a sensible response after a bus network stops communicating.",
        "order": [
            "Check whether backbone cable is damaged",
            "Inspect terminators at both ends",
            "Repair/replace faulty cable component",
            "Retest communication",
        ],
        "explanation": "Bus faults are often traced to backbone/terminator issues before retesting.",
        "source": "U1 DT 2023 Q7(b)(ii)(iii) + MS",
    },
    {
        "tag": "drag_star_expansion",
        "stem": "Order the process for adding a new workstation to a star network.",
        "order": [
            "Run cable from new workstation",
            "Connect to central switch/server",
            "Configure workstation network settings",
            "Test communication",
        ],
        "explanation": "Star networks allow device addition via the central point without full shutdown.",
        "source": "U1 DT 2024 Q6(a), 2019 Q6(d)(ii) + MS",
    },
    {
        "tag": "drag_internet_www_logic",
        "stem": "Order these statements from infrastructure to service use.",
        "order": [
            "Internet provides global connectivity",
            "Web servers host linked pages",
            "Browsers request pages",
            "Users view web content",
        ],
        "explanation": "Internet infrastructure supports web services that users access through browsers.",
        "source": "U1 DT 2025 Q8(b)(c) + MS",
    },
    {
        "tag": "drag_topology_identification",
        "stem": "Order the clues to identify a bus topology in a diagram question.",
        "order": [
            "Spot one shared main cable",
            "Check nodes connect to that cable",
            "Look for terminators at both ends",
            "Conclude it is a bus topology",
        ],
        "explanation": "CCEA bus diagram marking expects backbone, nodes, and terminators.",
        "source": "U1 DT 2023 Q7(c) + MS",
    },
    {
        "tag": "drag_router_switch_roles",
        "stem": "Order the data path in a typical wired LAN reaching the internet.",
        "order": [
            "Device sends packet via NIC",
            "Switch forwards packet in LAN",
            "Router forwards packet to internet",
            "Remote service responds",
        ],
        "explanation": "NIC->switch->router is the standard progression from local to external network.",
        "source": "U1 DT 2021 Q6 + MS",
    },
    {
        "tag": "drag_fibre_reasoning",
        "stem": "Order this reasoning chain about why fibre is often chosen.",
        "order": [
            "Need high-capacity reliable link",
            "Choose fibre-optic medium",
            "Transmit data as light",
            "Gain high bandwidth and low interference",
        ],
        "explanation": "Fibre is selected for high bandwidth and lower interference risk.",
        "source": "U1 DT 2022 Q8(d), 2023 Q6(a) + MS",
    },
    {
        "tag": "drag_iot_setup_logic",
        "stem": "Order a basic smart-home device connection flow.",
        "order": [
            "Power on IoT device",
            "Connect device to home network",
            "Link device to control app",
            "Send/receive data over internet",
        ],
        "explanation": "IoT devices rely on network connection before they can exchange data online.",
        "source": "U1 DT 2025 Q8(a) + MS",
    },
]

EXPERT_DRAG_SETS = [
    {
        "tag": "expert_drag_bus_outage",
        "stem": "Order the best troubleshooting sequence for a complete bus network outage.",
        "order": [
            "Confirm all nodes lost communication",
            "Inspect backbone cable continuity",
            "Check both terminators are fitted",
            "Replace faulty segment/component",
            "Retest end-to-end communication",
        ],
        "explanation": "A bus-wide outage usually points first to backbone or terminator faults.",
        "source": "U1 DT 2023 Q7(b)(ii)(iii) + MS",
    },
    {
        "tag": "expert_drag_school_extension",
        "stem": "Order the decision process for connecting a new school building to the existing network.",
        "order": [
            "Recognise distance exceeds one-building LAN scope",
            "Select WAN-style inter-site connection",
            "Use router links between sites",
            "Test inter-building communication",
            "Verify shared resources across sites",
        ],
        "explanation": "Inter-building expansion needs network-type and routing decisions before validation.",
        "source": "U1 DT 2024 Q1(b)(c), 2021 Q6 + MS",
    },
    {
        "tag": "expert_drag_media_selection",
        "stem": "Order the matching logic for choosing communication media in mixed scenarios.",
        "order": [
            "Identify short-range personal device task",
            "Map to Bluetooth",
            "Identify travelling cloud-access task",
            "Map to 5G",
            "Map home LAN device access to Wi-Fi",
        ],
        "explanation": "Expert tasks require selecting media by scenario constraints rather than memorising terms.",
        "source": "U1 DT 2023 Q6(a), 2025 Q8(c) + MS",
    },
    {
        "tag": "expert_drag_topology_choice",
        "stem": "Order this reasoning process for selecting a robust topology for a school lab.",
        "order": [
            "Need fault isolation for single workstation failures",
            "Choose star topology structure",
            "Connect all devices to central switch",
            "Test that one workstation fault does not stop others",
            "Document central-device failure risk",
        ],
        "explanation": "Star gives isolation benefits but still has a central point dependency.",
        "source": "U1 DT 2019 Q6(d), 2024 Q6(a) + MS",
    },
    {
        "tag": "expert_drag_ring_fault",
        "stem": "Order the analysis of a ring network failure where traffic stops.",
        "order": [
            "Identify loss of node-to-node circulation",
            "Check each ring cable segment and node",
            "Locate break/fault point in loop",
            "Restore loop continuity",
            "Retest full ring data flow",
        ],
        "explanation": "Ring communication depends on a complete loop path through nodes.",
        "source": "U1 DT 2022 Q7(a)(ii), 2023 Q7(c) + MS",
    },
]

EXPERT_SCENARIOS = [
    {
        "tag": "scenario_lan",
        "stem": "A school network only covers one building. Which option best describes this network type?",
        "answer": "LAN",
        "distractors": ["WAN", "Intranet", "Ring"],
        "explanation": "A LAN covers a small geographical area such as one building.",
        "source": "U1 DT 2024 Q1(c) + MS",
    },
    {
        "tag": "scenario_wan",
        "stem": "A company links offices in Belfast and Derry. Which option best describes the network type?",
        "answer": "WAN",
        "distractors": ["LAN", "Bus", "Intranet"],
        "explanation": "A WAN connects networks over large geographical areas.",
        "source": "U1 DT 2024 Q1(b) + MS",
    },
    {
        "tag": "scenario_intranet",
        "stem": "Staff can access an internal site, but the public cannot. Which option is correct?",
        "answer": "Intranet",
        "distractors": ["Internet", "WWW", "IoT"],
        "explanation": "An intranet is a private organisational network for authorised users.",
        "source": "U1 DT 2019 Q6(a)(iii) + MS",
    },
    {
        "tag": "scenario_www",
        "stem": "A student opens linked pages in a browser. Which option names this service running on the internet?",
        "answer": "World Wide Web",
        "distractors": ["LAN", "Backbone", "Router"],
        "explanation": "The World Wide Web is a collection of linked pages on web servers.",
        "source": "U1 DT 2025 Q8(b)(c) + MS",
    },
    {
        "tag": "scenario_iot",
        "stem": "A smart thermostat sends data online so it can be monitored remotely. Which option describes this?",
        "answer": "IoT",
        "distractors": ["Intranet", "WAN", "Bus topology"],
        "explanation": "IoT refers to physical devices connected to the internet.",
        "source": "U1 DT 2025 Q8(a) + MS",
    },
    {
        "tag": "scenario_bluetooth",
        "stem": "A student links wireless headphones to a phone. Which option is the most suitable communication technology?",
        "answer": "Bluetooth",
        "distractors": ["Wi-Fi", "5G", "Fibre-optic"],
        "explanation": "Bluetooth is designed for short-range personal device links.",
        "source": "U1 DT 2023 Q6(a), 2025 Q8(c) + MS",
    },
    {
        "tag": "scenario_wifi",
        "stem": "A smart TV is being connected to the home network in the living room. Which option is best?",
        "answer": "Wi-Fi",
        "distractors": ["Bluetooth", "5G", "Backbone cable"],
        "explanation": "Wi-Fi is the typical medium for local wireless network access.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "scenario_5g",
        "stem": "An employee needs cloud files while travelling between sites. Which option is most suitable?",
        "answer": "5G",
        "distractors": ["Bluetooth", "Wi-Fi", "Terminator"],
        "explanation": "5G is used for mobile data access away from fixed networks.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "scenario_fibre",
        "stem": "A business needs a high-capacity fixed link from LAN to internet. Which option is most suitable?",
        "answer": "Fibre-optic",
        "distractors": ["Bluetooth", "5G", "Wi-Fi"],
        "explanation": "Fibre-optic is commonly used for high-capacity fixed connectivity.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "scenario_router",
        "stem": "A school must connect its internal network to the internet. Which device option is required?",
        "answer": "Router",
        "distractors": ["Switch", "NIC", "Terminator"],
        "explanation": "A router connects networks and forwards packets between them.",
        "source": "U1 DT 2021 Q6(2), 2023 Q6(b) + MS",
    },
    {
        "tag": "scenario_switch",
        "stem": "In a wired LAN, each workstation needs to connect to a central LAN device. Which option is correct?",
        "answer": "Switch",
        "distractors": ["Router", "File server", "Backbone"],
        "explanation": "On a wired network, each device connects to a switch using Ethernet cables.",
        "source": "U1 DT 2023 Q6(b) + MS",
    },
    {
        "tag": "scenario_nic",
        "stem": "A computer cannot join the network until one hardware component is present. Which option is it?",
        "answer": "NIC",
        "distractors": ["Router", "Terminator", "WAN"],
        "explanation": "A NIC is needed for a device to connect and communicate on a network.",
        "source": "U1 DT 2023 Q7(e) + MS",
    },
    {
        "tag": "scenario_file_server",
        "stem": "A school wants central storage so all staff can access shared files. Which option is best?",
        "answer": "File server",
        "distractors": ["Switch", "NIC", "Router"],
        "explanation": "A file server stores shared files for network users.",
        "source": "U1 DT 2021 Q6(1) + MS",
    },
    {
        "tag": "scenario_bus_failure",
        "stem": "In a bus topology, the main cable breaks. Which option best describes what happens next?",
        "answer": "Communication across the bus network fails",
        "distractors": [
            "Only one workstation is affected",
            "Performance improves",
            "Network becomes a ring automatically",
        ],
        "explanation": "If the backbone cable fails, communication on a bus network can fail.",
        "source": "U1 DT 2023 Q7(b)(ii) + MS",
    },
    {
        "tag": "scenario_terminator",
        "stem": "A teacher labels both ends of a bus cable. Which option explains the role of these end components?",
        "answer": "They stop signal bounce/return on the cable",
        "distractors": [
            "They increase wireless range",
            "They store shared files",
            "They route internet traffic",
        ],
        "explanation": "Terminators absorb the signal and reduce bounce/collision issues.",
        "source": "U1 DT 2023 Q7(b)(iii) + MS",
    },
    {
        "tag": "scenario_star_advantage",
        "stem": "One workstation in a star network fails. Which option is most accurate?",
        "answer": "Other workstations can usually continue",
        "distractors": [
            "Whole network always stops",
            "Backbone cable fails",
            "Network turns into bus topology",
        ],
        "explanation": "In star topology, single workstation failures are often isolated.",
        "source": "U1 DT 2024 Q6(a), 2019 Q6(d)(ii) + MS",
    },
    {
        "tag": "scenario_star_disadvantage",
        "stem": "The central switch/server in a star topology fails. Which option is most accurate?",
        "answer": "The network can fail because the central point is critical",
        "distractors": [
            "Only one workstation fails",
            "No effect on communication",
            "It improves security",
        ],
        "explanation": "A star network depends on the central device.",
        "source": "U1 DT 2019 Q6(d)(iii), 2024 Q6(a) + MS",
    },
    {
        "tag": "scenario_ring_disadvantage",
        "stem": "A node or cable fails in a ring network. Which option best matches this risk?",
        "answer": "The ring can be disrupted",
        "distractors": [
            "Only one device is affected for sure",
            "No disruption because there is a central controller",
            "Terminators absorb the issue",
        ],
        "explanation": "Ring communication can be disrupted by a single node/cable failure.",
        "source": "U1 DT 2022 Q7(a)(ii) + MS",
    },
    {
        "tag": "scenario_internet_www_compare",
        "stem": "Which option correctly distinguishes internet and World Wide Web?",
        "answer": "Internet is the network; WWW is an application/service running on it",
        "distractors": [
            "Both terms mean the same thing",
            "WWW is the physical cable network",
            "Internet is only email",
        ],
        "explanation": "CCEA expects internet infrastructure and WWW service to be distinguished.",
        "source": "U1 DT 2025 Q8(c) + MS",
    },
    {
        "tag": "scenario_bus_labels",
        "stem": "A student is labelling a bus topology diagram. Which option lists essential labels?",
        "answer": "Nodes/workstations, backbone cable, terminators at both ends",
        "distractors": [
            "Router and cloud only",
            "Switch and ring token",
            "One workstation only",
        ],
        "explanation": "Bus diagram marking points include nodes, backbone, and two terminators.",
        "source": "U1 DT 2023 Q7(c) + MS",
    },
    {
        "tag": "scenario_fibre_signals",
        "stem": "Which option about fibre-optic transmission is correct?",
        "answer": "It transmits data using light",
        "distractors": [
            "It transmits data as electrical signals only",
            "It cannot carry network data",
            "It is a wireless medium",
        ],
        "explanation": "Fibre-optic data is carried as pulses of light.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "scenario_fibre_bandwidth",
        "stem": "A company needs a high-bandwidth medium. Which option is most suitable from this topic?",
        "answer": "Fibre-optic",
        "distractors": ["Bluetooth", "Bus topology", "Intranet"],
        "explanation": "Fibre-optic cable has high bandwidth.",
        "source": "U1 DT 2022 Q8(d), 2023 Q6(a) + MS",
    },
    {
        "tag": "scenario_fibre_intercept",
        "stem": "Which option best describes interception risk on fibre compared with copper?",
        "answer": "Fibre is generally harder to intercept",
        "distractors": [
            "Fibre is easier to intercept",
            "Both are always equally easy to intercept",
            "Interception depends only on topology name",
        ],
        "explanation": "CCEA mark schemes accept that fibre is generally harder to intercept than copper.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "scenario_network_advantage",
        "stem": "A school asks why computers should be networked. Which option gives a valid advantage?",
        "answer": "Share files/hardware and communicate",
        "distractors": [
            "Eliminate all maintenance",
            "Guarantee no failures",
            "Remove need for updates",
        ],
        "explanation": "Networking advantages include sharing resources and communication.",
        "source": "U1 DT 2019 Q6(a)(ii), 2025 Q8(d) + MS",
    },
    {
        "tag": "scenario_topology_name",
        "stem": "A diagram shows all nodes connected to one backbone cable with terminators at both ends. Which option is correct?",
        "answer": "Bus topology",
        "distractors": ["Ring topology", "Star topology", "WAN"],
        "explanation": "This is the defining structure of a bus topology.",
        "source": "U1 DT 2023 Q7(b)(i)(c) + MS",
    },
]

DIAGRAM_LABEL_ITEMS = [
    {
        "tag": "diagram_star_ws",
        "diagram_key": "star_topology",
        "marker": "1",
        "stem": "In this star-network diagram, which option best identifies number 1?",
        "answer": "Workstation",
        "distractors": ["Router", "Terminator", "Backbone cable"],
        "explanation": "Marker 1 marks an end-user workstation in the star diagram.",
        "source": "U1 DT 2019 Q6(d)(i) + MS",
    },
    {
        "tag": "diagram_star_central",
        "diagram_key": "star_topology",
        "marker": "2",
        "stem": "In this star-network diagram, which option best identifies number 2?",
        "answer": "Switch/Server",
        "distractors": ["Router", "Terminator", "Intranet"],
        "explanation": "Marker 2 is the central switch/server in a star topology.",
        "source": "U1 DT 2019 Q6(d)(i), 2024 Q6(a) + MS",
    },
    {
        "tag": "diagram_star_printer",
        "diagram_key": "star_topology",
        "marker": "3",
        "stem": "In this star-network diagram, which option best identifies number 3?",
        "answer": "Printer",
        "distractors": ["NIC", "Router", "Backbone cable"],
        "explanation": "Marker 3 points to a shared network printer.",
        "source": "U1 DT 2019 Q6(d)(i) + MS",
    },
    {
        "tag": "diagram_star_cable",
        "diagram_key": "star_topology",
        "marker": "4",
        "stem": "In this star-network diagram, which option best identifies number 4?",
        "answer": "Cable",
        "distractors": ["Terminator", "WAN", "WWW"],
        "explanation": "Marker 4 indicates the physical cable link in the star.",
        "source": "U1 DT 2019 Q6(d)(i) + MS",
    },
    {
        "tag": "diagram_bus_terminator",
        "diagram_key": "bus_topology",
        "marker": "1",
        "stem": "In this bus-network diagram, which option best identifies number 1?",
        "answer": "Terminator",
        "distractors": ["Router", "NIC", "Switch"],
        "explanation": "Marker 1 labels the end component that absorbs signals on a bus cable.",
        "source": "U1 DT 2023 Q7(b)(iii) + MS",
    },
    {
        "tag": "diagram_bus_backbone",
        "diagram_key": "bus_topology",
        "marker": "2",
        "stem": "In this bus-network diagram, which option best identifies number 2?",
        "answer": "Backbone cable",
        "distractors": ["Ring cable", "Switch", "5G link"],
        "explanation": "Marker 2 is the main shared cable in bus topology.",
        "source": "U1 DT 2023 Q7(b)(c) + MS",
    },
    {
        "tag": "diagram_bus_node",
        "diagram_key": "bus_topology",
        "marker": "3",
        "stem": "In this bus-network diagram, which option best identifies number 3?",
        "answer": "Node/Workstation",
        "distractors": ["Router", "Backbone cable", "Terminator"],
        "explanation": "Marker 3 points to a connected node/workstation.",
        "source": "U1 DT 2023 Q7(c) + MS",
    },
    {
        "tag": "diagram_ring_node",
        "diagram_key": "ring_topology",
        "marker": "1",
        "stem": "In this ring-network diagram, which option best identifies number 1?",
        "answer": "Node/Workstation",
        "distractors": ["Terminator", "File server", "Backbone cable"],
        "explanation": "Marker 1 identifies a workstation/node in the ring.",
        "source": "U1 DT 2022 Q7(a) + MS",
    },
    {
        "tag": "diagram_ring_path",
        "diagram_key": "ring_topology",
        "marker": "2",
        "stem": "In this ring-network diagram, which option best identifies number 2?",
        "answer": "Ring data path/cable",
        "distractors": ["Switch", "Router", "NIC"],
        "explanation": "Marker 2 marks the loop path used for ring communication.",
        "source": "U1 DT 2022 Q7(a), 2023 Q7(c) + MS",
    },
    {
        "tag": "diagram_ring_flow",
        "diagram_key": "ring_topology",
        "marker": "3",
        "stem": "In this ring-network diagram, which option best identifies number 3?",
        "answer": "Data passes node to node",
        "distractors": ["Central switch control", "Backbone terminator", "Wireless broadcast only"],
        "explanation": "Ring communication passes data between nodes around the loop.",
        "source": "U1 DT 2022 Q7(a), 2023 Q7(c) + MS",
    },
    {
        "tag": "diagram_path_nic",
        "diagram_key": "lan_internet_path",
        "marker": "1",
        "stem": "In this LAN-to-internet path diagram, which option best identifies number 1?",
        "answer": "Workstation/NIC",
        "distractors": ["Router", "Internet", "Terminator"],
        "explanation": "Marker 1 marks the source device and network interface.",
        "source": "U1 DT 2021 Q6, 2023 Q7(e) + MS",
    },
    {
        "tag": "diagram_path_switch",
        "diagram_key": "lan_internet_path",
        "marker": "2",
        "stem": "In this LAN-to-internet path diagram, which option best identifies number 2?",
        "answer": "Switch",
        "distractors": ["Router", "Backbone cable", "Intranet"],
        "explanation": "Marker 2 labels the switch handling LAN traffic.",
        "source": "U1 DT 2021 Q6(1), 2023 Q6(b) + MS",
    },
    {
        "tag": "diagram_path_router",
        "diagram_key": "lan_internet_path",
        "marker": "3",
        "stem": "In this LAN-to-internet path diagram, which option best identifies number 3?",
        "answer": "Router",
        "distractors": ["NIC", "Switch", "Terminator"],
        "explanation": "Marker 3 labels the router connecting LAN to internet.",
        "source": "U1 DT 2021 Q6(2), 2023 Q6(b) + MS",
    },
    {
        "tag": "diagram_path_internet",
        "diagram_key": "lan_internet_path",
        "marker": "4",
        "stem": "In this LAN-to-internet path diagram, which option best identifies number 4?",
        "answer": "Internet/Web server",
        "distractors": ["Intranet", "Bus backbone", "Bluetooth"],
        "explanation": "Marker 4 is the external internet service destination.",
        "source": "U1 DT 2025 Q8(b)(c), 2021 Q6 + MS",
    },
    {
        "tag": "diagram_media_bluetooth",
        "diagram_key": "media_links",
        "marker": "1",
        "stem": "In this communication-media diagram, which option best identifies number 1?",
        "answer": "Bluetooth link",
        "distractors": ["Wi-Fi link", "5G link", "Fibre-optic link"],
        "explanation": "Marker 1 is the phone-to-headphones short-range connection.",
        "source": "U1 DT 2023 Q6(a), 2025 Q8(c) + MS",
    },
    {
        "tag": "diagram_media_wifi",
        "diagram_key": "media_links",
        "marker": "2",
        "stem": "In this communication-media diagram, which option best identifies number 2?",
        "answer": "Wi-Fi link",
        "distractors": ["Bluetooth link", "5G link", "Backbone cable"],
        "explanation": "Marker 2 shows home smart-TV local wireless access.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "diagram_media_5g",
        "diagram_key": "media_links",
        "marker": "3",
        "stem": "In this communication-media diagram, which option best identifies number 3?",
        "answer": "5G link",
        "distractors": ["Wi-Fi link", "Bluetooth link", "Terminator"],
        "explanation": "Marker 3 indicates travelling mobile cloud access.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "diagram_media_fibre",
        "diagram_key": "media_links",
        "marker": "4",
        "stem": "In this communication-media diagram, which option best identifies number 4?",
        "answer": "Fibre-optic link",
        "distractors": ["5G link", "Wi-Fi link", "Bluetooth link"],
        "explanation": "Marker 4 marks business LAN fixed high-capacity internet link.",
        "source": "U1 DT 2023 Q6(a) + MS",
    },
    {
        "tag": "diagram_fibre_light",
        "diagram_key": "fibre_properties",
        "marker": "1",
        "stem": "In this fibre-properties diagram, which option best identifies number 1?",
        "answer": "Data carried as light",
        "distractors": ["Data carried as electricity", "No signal transmission", "Wireless radio broadcast"],
        "explanation": "Fibre-optic transmits data using pulses of light.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
    {
        "tag": "diagram_fibre_bandwidth",
        "diagram_key": "fibre_properties",
        "marker": "2",
        "stem": "In this fibre-properties diagram, which option best identifies number 2?",
        "answer": "High bandwidth",
        "distractors": ["Low bandwidth", "No network capacity", "Topology name"],
        "explanation": "A key fibre property is high bandwidth.",
        "source": "U1 DT 2022 Q8(d) + MS",
    },
]

EASY_MCQ_TAGS = [
    "networking_definition",
    "lan",
    "wan",
    "internet_definition",
    "www_definition",
    "internet_vs_www",
    "intranet",
    "iot",
    "wifi",
    "bluetooth",
    "optical_fibre_signals",
    "optical_fibre_bandwidth",
    "optical_fibre_interference",
    "optical_fibre_security",
    "mobile_5g",
    "nic",
    "switch",
    "router",
    "file_server",
    "ethernet_switch",
    "network_advantages",
    "bus_topology",
    "bus_disadvantage",
    "backbone",
    "terminator",
    "ring_topology",
    "star_topology",
    "star_advantage",
    "topology_bus_name",
    "media_headphones",
]

MEDIUM_MCQ_TAGS = [
    "lan",
    "wan",
    "internet_definition",
    "www_definition",
    "internet_vs_www",
    "iot",
    "wifi",
    "bluetooth",
    "optical_fibre_signals",
    "optical_fibre_security",
    "mobile_5g",
    "nic",
    "switch",
    "router",
    "file_server",
    "bus_topology",
    "bus_disadvantage",
    "ring_topology",
    "star_topology",
    "star_disadvantage",
]

ALLOWED_FORMATS = {
    "easy": {"mcq", "fill_gap", "match_table"},
    "medium": {"mcq", "fill_gap", "match_table", "drag_drop"},
    "expert": {"mcq", "diagram_label", "match_table", "drag_drop"},
}


def stable_shuffle(values, seed):
    rnd = random.Random(seed)
    out = list(values)
    rnd.shuffle(out)
    return out


def dedupe_strings(values):
    seen = set()
    out = []
    for value in values:
        cleaned = str(value).strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            out.append(cleaned)
    return out


def accepted_terms(concept):
    return dedupe_strings([concept["answer"], *concept.get("accepted", [])])


def concept_by_tag(tag):
    concept = CONCEPT_BY_TAG.get(tag)
    if concept is None:
        raise AssertionError(f"Unknown concept tag: {tag}")
    return concept


def mcq_from_concept(concept, difficulty, index, seed_offset=500):
    choices = stable_shuffle([concept["answer"], *concept["distractors"]], seed_offset + index)
    default_prompts = [
        f"Choose the best description of {concept['keyword']}.",
        f"Which option is correct for {concept['keyword']}?",
        f"Select the accurate option for {concept['keyword']}.",
    ]
    prompts = concept.get("mcq_prompts", default_prompts)
    return {
        "difficulty": difficulty,
        "format": "mcq",
        "stem": prompts[index % len(prompts)],
        "options_json": {"choices": choices},
        "correct_answer_json": {"choice": concept["answer"]},
        "markscheme_points_json": [concept["answer"]],
        "explanation": concept["explanation"],
        "source_ref": concept["source"],
        "tags_json": [concept["tag"]],
    }


def scenario_mcq(item, index):
    choices = stable_shuffle([item["answer"], *item["distractors"]], 2100 + index)
    return {
        "difficulty": "expert",
        "format": "mcq",
        "stem": item["stem"],
        "options_json": {"choices": choices},
        "correct_answer_json": {"choice": item["answer"]},
        "markscheme_points_json": [item["answer"]],
        "explanation": item["explanation"],
        "source_ref": item["source"],
        "tags_json": [item["tag"], "expert_scenario"],
    }


def fill_gap(item, difficulty):
    concept = concept_by_tag(item["tag"])
    accepted = dedupe_strings([*item["accepted"], concept["answer"], *concept.get("accepted", [])])
    return {
        "difficulty": difficulty,
        "format": "fill_gap",
        "stem": item["stem"],
        "options_json": None,
        "correct_answer_json": {"accepted": accepted},
        "markscheme_points_json": [concept["answer"]],
        "explanation": concept["explanation"],
        "source_ref": concept["source"],
        "tags_json": [concept["tag"]],
    }


def match_set(set_data, difficulty, index):
    pairs = [{"left": left, "right": right} for left, right in zip(set_data["left"], set_data["right"])]
    choices = set_data["choices"] if index % 2 == 0 else list(reversed(set_data["choices"]))
    return {
        "difficulty": difficulty,
        "format": "match_table",
        "stem": "Match each item to the correct term or definition.",
        "options_json": {"pairs": pairs, "choices": choices},
        "correct_answer_json": {"pairs": {pair["left"]: pair["right"] for pair in pairs}},
        "markscheme_points_json": ["All pairings correct"],
        "explanation": set_data["explanation"],
        "source_ref": set_data["source"],
        "tags_json": [set_data["tag"]],
    }


def drag_set(set_data, difficulty, index):
    return {
        "difficulty": difficulty,
        "format": "drag_drop",
        "stem": set_data["stem"],
        "options_json": {"items": stable_shuffle(set_data["order"], 3200 + index)},
        "correct_answer_json": {"order": set_data["order"]},
        "markscheme_points_json": ["Sequence correct"],
        "explanation": set_data["explanation"],
        "source_ref": set_data["source"],
        "tags_json": [set_data["tag"]],
    }


def diagram_label(item, index):
    choices = stable_shuffle([item["answer"], *item["distractors"]], 4200 + index)
    return {
        "difficulty": "expert",
        "format": "diagram_label",
        "stem": item["stem"],
        "options_json": {
            "diagram_key": item["diagram_key"],
            "marker": item["marker"],
            "choices": choices,
        },
        "correct_answer_json": {
            "choice": item["answer"],
            "accepted": [item["answer"], item["answer"].lower()],
        },
        "markscheme_points_json": [item["answer"]],
        "explanation": item["explanation"],
        "source_ref": item["source"],
        "tags_json": [item["tag"], f"diagram_{item['diagram_key']}", "diagram_label"],
    }


def build_questions():
    easy = []
    for i in range(30):
        easy.append(mcq_from_concept(concept_by_tag(EASY_MCQ_TAGS[i % len(EASY_MCQ_TAGS)]), "easy", i))
    for i in range(20):
        easy.append(fill_gap(FILL_GAP_ITEMS[i % len(FILL_GAP_ITEMS)], "easy"))
    for i in range(10):
        easy.append(match_set(EASY_MATCH_SETS[i % len(EASY_MATCH_SETS)], "easy", i))

    medium = []
    for i in range(20):
        medium.append(mcq_from_concept(concept_by_tag(MEDIUM_MCQ_TAGS[i % len(MEDIUM_MCQ_TAGS)]), "medium", i, seed_offset=700))
    for i in range(15):
        medium.append(fill_gap(FILL_GAP_ITEMS[(i + 7) % len(FILL_GAP_ITEMS)], "medium"))
    for i in range(10):
        medium.append(match_set(MEDIUM_MATCH_SETS[i % len(MEDIUM_MATCH_SETS)], "medium", i))
    for i in range(15):
        medium.append(drag_set(MEDIUM_DRAG_SETS[i], "medium", i))

    expert = []
    for i in range(25):
        expert.append(scenario_mcq(EXPERT_SCENARIOS[i], i))
    for i in range(20):
        expert.append(diagram_label(DIAGRAM_LABEL_ITEMS[i], i))
    for i in range(10):
        expert.append(match_set(EXPERT_MATCH_SETS[i % len(EXPERT_MATCH_SETS)], "expert", i))
    for i in range(5):
        expert.append(drag_set(EXPERT_DRAG_SETS[i], "expert", i))

    for question in easy:
        if question["format"] not in ALLOWED_FORMATS["easy"]:
            raise AssertionError(f"Easy question has disallowed format: {question['format']}")
    for question in medium:
        if question["format"] not in ALLOWED_FORMATS["medium"]:
            raise AssertionError(f"Medium question has disallowed format: {question['format']}")
    for question in expert:
        if question["format"] not in ALLOWED_FORMATS["expert"]:
            raise AssertionError(f"Expert question has disallowed format: {question['format']}")

    questions = easy + medium + expert
    assert len(easy) == 60
    assert len(medium) == 60
    assert len(expert) == 60
    assert len(questions) == 180

    for idx, question in enumerate(questions):
        source_type = "adapted_exam" if idx < 72 else "new_original"
        question["source_type"] = source_type
        if source_type == "new_original":
            question["source_ref"] = f"{question['source_ref']}; Network_Technologies_Notes.docx"
        question["qa_status"] = "published"
        question["is_active"] = True

    return questions


def sql_escape(value: str) -> str:
    return value.replace("'", "''")


def json_sql(value) -> str:
    return f"'{sql_escape(json.dumps(value, ensure_ascii=True))}'::jsonb"


def to_sql(questions):
    rows = []
    for question in questions:
        options_sql = "null" if question["options_json"] is None else json_sql(question["options_json"])
        rows.append(
            "(\n  "
            + ",\n  ".join(
                [
                    "(select id from target_topic)",
                    f"'{question['difficulty']}'::public.difficulty_level",
                    f"'{question['format']}'::public.question_format",
                    f"'{sql_escape(question['stem'])}'",
                    options_sql,
                    json_sql(question["correct_answer_json"]),
                    json_sql(question["markscheme_points_json"]),
                    f"'{sql_escape(question['explanation'])}'",
                    f"'{question['source_type']}'::public.question_source",
                    f"'{sql_escape(question['source_ref'])}'",
                    json_sql(question["tags_json"]),
                    f"'{question['qa_status']}'",
                    "true" if question["is_active"] else "false",
                ]
            )
            + "\n)"
        )

    values_sql = ",\n".join(rows)
    return f"""-- Seed 180 network technology questions

with target_topic as (
  select id from public.topics where slug = 'network-technologies'
)
insert into public.questions (
  topic_id,
  difficulty,
  format,
  stem,
  options_json,
  correct_answer_json,
  markscheme_points_json,
  explanation,
  source_type,
  source_ref,
  tags_json,
  qa_status,
  is_active
)
values
{values_sql}
on conflict do nothing;
"""


def assert_scope_guard(questions):
    payload = json.dumps(questions, ensure_ascii=True).lower()
    for banned in BANNED_SCOPE_TERMS:
        if banned in payload:
            raise AssertionError(f"Out-of-scope term found in generated content: {banned}")


def main():
    questions = build_questions()
    counts = {"easy": 0, "medium": 0, "expert": 0}
    for question in questions:
        counts[question["difficulty"]] += 1

    assert counts == {"easy": 60, "medium": 60, "expert": 60}
    assert_scope_guard(questions)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(questions, indent=2), encoding="utf-8")
    OUT_SQL.write_text(to_sql(questions), encoding="utf-8")

    print(f"Generated {len(questions)} questions")
    print(f"Distribution: {counts}")
    print(f"JSON: {OUT_JSON}")
    print(f"SQL: {OUT_SQL}")


if __name__ == "__main__":
    main()
