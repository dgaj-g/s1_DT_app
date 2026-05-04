from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ObjectiveDefinition:
    code: str
    title: str
    description: str
    keywords: tuple[str, ...]


OBJECTIVE_CATALOG: dict[str, tuple[ObjectiveDefinition, ...]] = {
    "digital-data": (
        ObjectiveDefinition("digital-data.data-and-information", "Data and information", "Distinguish raw data from processed information and recognise the purpose of digital representation.", ("raw data", "processed data", "processed and given meaning", "unprocessed", "facts and figures", "meaningless raw", "becomes information", "term data", "term information", "term \"information\"", "example of information", "with context or meaning", "describes the term data", "describes the term information", "true about data", "best describes the term information")),
        ObjectiveDefinition("digital-data.storage-units-and-capacity", "Storage units and capacity", "Understand bits, bytes and larger storage units and compare file or storage size.", ("bit", "bits", "byte", "bytes", "nibble", "kilobyte", "megabyte", "gigabyte", "terabyte", "storage", "capacity", "data storage", "smallest to largest", "ascending order", "binary", "0 and 1", "ones and zeros", "stores data in")),
        ObjectiveDefinition("digital-data.buffering-and-streaming", "Buffering and streaming", "Explain buffering during media transfer and playback.", ("buffer", "buffering", "stream", "streaming", "downloaded part of a video", "moving images", "tutorial video", "download videos quickly")),
        ObjectiveDefinition("digital-data.bitmap-images", "Bitmap images", "Describe pixels, resolution and how bitmap images are represented.", ("bitmap", "pixel", "pixels", "resolution", "colour depth", "image quality")),
        ObjectiveDefinition("digital-data.vector-graphics", "Vector graphics", "Describe how vector graphics are defined and why they resize without quality loss.", ("vector", "mathematical equation", "mathematical equations", "re-sized", "resized without loss", "loss of quality")),
        ObjectiveDefinition("digital-data.image-file-formats-and-compression", "Image file formats and compression", "Compare common image file formats and the effect of compression on size and quality.", ("jpeg", "jpg", "png", "bmp", "mpeg", "compressed", "compression", "lossless", "lossy", "file size")),
        ObjectiveDefinition("digital-data.basic-data-types", "Basic data types", "Recognise simple data types used to store values such as integers, strings and date/time.", ("data type", "integer", "character", "string", "real", "date/time", "student score")),
        ObjectiveDefinition("digital-data.sound-representation", "Sound representation", "Explain how digital sound quality depends on sample rate, bit depth or bit rate.", ("sample rate", "bit rate", "bit depth", "wav", "sound", "audio", "sampling", "recording")),
        ObjectiveDefinition("digital-data.portability-and-file-choice", "Portability and file choice", "Choose suitable digital file formats for portability and sharing.", ("portability", "portable", "share", "sharing", "suitable format", "file format", "pdf", "txt")),
    ),
    "software": (
        ObjectiveDefinition("software.software-categories", "Software categories", "Classify software as system, utility, application, translator or library software.", ("system software", "application software", "utility software", "translator", "compiler", "interpreter", "assembler", "library program", "library programs")),
        ObjectiveDefinition("software.operating-system-functions", "Operating system functions", "Explain how an operating system manages resources, files, interfaces and multitasking.", ("operating system", "os", "user interface", "processor time", "memory management", "file management", "multi-user", "multitasking", "resource", "operate the computer", "install programs")),
        ObjectiveDefinition("software.utility-software", "Utility software", "Recognise common utility programs and their purposes.", ("utility", "backup", "restore", "defragment", "antivirus", "compression utility", "firewall utility", "quarantine", "isolating files that are suspected of containing a virus", "remove detected viruses", "removal of any detected viruses", "virus removal", "store backups separately", "stored separately from the computer")),
        ObjectiveDefinition("software.translators-and-libraries", "Translators and libraries", "Explain the roles of translators and reusable library code in software development.", ("compiler", "interpreter", "assembler", "machine code", "high-level language", "library", "precompiled", "source code")),
        ObjectiveDefinition("software.startup-firmware-and-memory", "Startup firmware and memory", "Understand BIOS, ROM and RAM in relation to startup and running software.", ("bios", "rom", "ram", "cache memory", "cache", "boot", "booting", "volatile", "firmware", "stores the bios")),
        ObjectiveDefinition("software.processing-modes", "Processing modes", "Distinguish batch processing and real-time processing and choose appropriate examples.", ("batch processing", "real-time processing", "real time processing", "billing systems", "airline booking systems", "transaction processing", "mode of processing", "meter readings", "master file", "transaction file")),
    ),
    "database-applications": (
        ObjectiveDefinition("database-applications.database-structure", "Database structure", "Recognise tables, records and fields and how data is organised in a database.", ("what is a database", "table", "tables", "record", "records", "field", "fields", "rows and columns", "member table", "dvd rental database", "populate", "populated", "populate a database")),
        ObjectiveDefinition("database-applications.data-types", "Database data types", "Choose appropriate data types for stored data fields.", ("data type", "date/time", "currency", "boolean", "integer", "text/string", "text", "number field")),
        ObjectiveDefinition("database-applications.keys-and-identifiers", "Keys and identifiers", "Explain primary keys, foreign keys and unique identification of records.", ("primary key", "key field", "foreign key", "composite key", "composite primary key", "uniquely identifies", "membercode", "asterisk")),
        ObjectiveDefinition("database-applications.relationships-and-link-tables", "Relationships and link tables", "Identify one-to-one, one-to-many and many-to-many relationships and the purpose of linking tables.", ("relationship", "one to one", "one to many", "many to many", "link table", "membernewsletter", "junction table", "crow's foot", "er diagram")),
        ObjectiveDefinition("database-applications.queries-forms-and-reports", "Queries, forms and reports", "Describe the role of forms, queries and reports in capturing, retrieving and presenting data.", ("query", "qbe", "sql", "select", "from", "where", "criteria", "filter", "sorted", "sort", "order", "list dvds", "form", "report", "reports", "printable", "printed", "grouped", "input form", "macro", "macros")),
        ObjectiveDefinition("database-applications.validation", "Validation", "Apply validation checks to improve data quality at input.", ("validation", "presence check", "range check", "length check", "format check", "type check", "validation check")),
        ObjectiveDefinition("database-applications.data-analytics", "Data analytics", "Recognise basic techniques used to find patterns in data.", ("data analytics", "patterns in data", "statistical analysis", "algorithms", "artificial intelligence", "ai", "big data", "3v", "3 v", "volume", "velocity", "variety")),
        ObjectiveDefinition("database-applications.data-exchange-and-csv", "Data exchange and CSV", "Recognise CSV as a data exchange format and understand simple import/export contexts.", ("csv", "comma separated values", "comma-separated values", "import", "export", "transfer data between a database and a spreadsheet", "read by a different piece of software", "creating a data file using one piece of software")),
    ),
    "spreadsheet-applications": (
        ObjectiveDefinition("spreadsheet-applications.spreadsheet-structure", "Spreadsheet structure", "Recognise cells, rows, columns, worksheets and cell references.", ("cell", "row", "column", "cell reference", "worksheet", "sheet tab", "basic building block")),
        ObjectiveDefinition("spreadsheet-applications.data-types-and-values", "Spreadsheet data types and values", "Recognise the kinds of values stored in spreadsheet cells, including numeric and currency data.", ("data type", "currency", "£", "selling price", "values such as", "stored in these cells")),
        ObjectiveDefinition("spreadsheet-applications.formulas-and-operators", "Formulas and operators", "Write and interpret formulas using arithmetic operators.", ("formula", "=a1+b1", "add", "subtract", "multiply", "divide", "operator", "equals sign")),
        ObjectiveDefinition("spreadsheet-applications.functions-and-lookups", "Functions and lookups", "Use built-in functions and lookup formulas appropriately.", ("function", "sum", "average", "max", "min", "count", "vlookup", "lookup")),
        ObjectiveDefinition("spreadsheet-applications.macros-and-automation", "Macros and automation", "Explain what macros do and how they can automate repeated spreadsheet tasks.", ("macro", "macros", "record actions", "automate", "automatically update", "mouse click", "pressing a key", "created")),
        ObjectiveDefinition("spreadsheet-applications.references-and-fill", "References and fill", "Understand relative and absolute cell references and copying formulas.", ("absolute", "relative", "$", "fill handle", "copied", "copying a formula", "replication")),
        ObjectiveDefinition("spreadsheet-applications.validation-and-checking", "Validation and checking", "Use spreadsheet validation and checking features to control input and spot errors.", ("data validation", "validation", "error", "check", "reasonable and sensible", "correct format and range", "input rule", "allowed values")),
        ObjectiveDefinition("spreadsheet-applications.formatting-and-templates", "Formatting and templates", "Apply formatting features and recognise the purpose of templates.", ("conditional formatting", "formatting", "merge", "merged", "centred", "centered", "header spans", "bold", "template", "preformatted spreadsheet layout")),
        ObjectiveDefinition("spreadsheet-applications.csv-and-data-exchange", "CSV and data exchange", "Recognise CSV structure and how spreadsheet data can be exchanged.", ("csv", "comma separated values", "comma-separated values", "each comma", "each new line", "file format used to transfer")),
        ObjectiveDefinition("spreadsheet-applications.charts-and-visualisation", "Charts and visualisation", "Choose and interpret spreadsheet charts and graphs.", ("chart", "graph", "pie chart", "bar chart", "line graph", "visualisation", "visualization", "visually represent data", "linked to other applications")),
        ObjectiveDefinition("spreadsheet-applications.modelling-and-what-if", "Modelling and what-if analysis", "Use spreadsheets for modelling, predictions and scenario testing.", ("model", "modelling", "what-if", "scenario", "prediction", "forecast", "informed choices", "perform calculations")),
        ObjectiveDefinition("spreadsheet-applications.uses-and-workplace-applications", "Spreadsheet uses and workplace applications", "Recognise typical occupations and tasks where spreadsheets are used to process and display information.", ("occupations", "engineers", "scientists", "teachers", "designers", "people who run their own business", "process and display", "used to process and display")),
    ),
    "computer-hardware": (
        ObjectiveDefinition("computer-hardware.cpu-components", "CPU components", "Identify the CPU and the roles of the ALU, Control Unit and registers.", ("cpu", "central processing unit", "alu", "arithmetic logic unit", "control unit", "register", "brain of the computer")),
        ObjectiveDefinition("computer-hardware.fetch-execute-cycle", "Fetch-execute cycle", "Explain the fetch-execute cycle and the function of key registers.", ("fetch-execute", "fetch execute", "program counter", "mar", "mdr", "current instruction", "fetched from memory", "ias", "immediate access store")),
        ObjectiveDefinition("computer-hardware.processor-performance", "Processor performance", "Explain how clock speed, cache and number of cores affect performance.", ("clock speed", "ghz", "mhz", "cache", "core", "dual-core", "turbo boost", "instructions per second", "cycles per second", "online tutoring service")),
        ObjectiveDefinition("computer-hardware.primary-memory-and-firmware", "Primary memory and firmware", "Distinguish RAM, ROM and BIOS and their purposes.", ("ram", "rom", "bios", "volatile", "boot-up instructions", "temporarily hold data")),
        ObjectiveDefinition("computer-hardware.storage-devices", "Storage devices", "Compare storage devices and media such as SSDs and hard drives.", ("ssd", "solid state drive", "hard disk", "hdd", "flash memory", "magnetic disc", "optical storage", "magnetic storage", "cloud storage", "laser", "capacity", "portability", "storage device", "high-definition video", "limited space on his hard drive", "games")),
        ObjectiveDefinition("computer-hardware.peripherals-and-specifications", "Peripherals and specifications", "Interpret hardware specifications and recognise peripheral roles.", ("technical specification", "specification", "printer", "monitor", "keyboard", "peripheral", "device specification", "input device", "output device", "graphic digitiser", "microphone", "display", "speaker", "converts audio signals into sound")),
    ),
    "network-technologies": (
        ObjectiveDefinition("network-technologies.networking-basics-and-types", "Networking basics and types", "Define networking and distinguish LAN and WAN contexts.", ("networking", "lan", "wan", "local area network", "wide area network", "share data", "network of computers", "connected devices", "transmit information")),
        ObjectiveDefinition("network-technologies.internet-web-intranet-iot", "Internet, web, intranet and IoT", "Distinguish between the Internet, WWW, intranet and Internet of Things.", ("internet", "world wide web", "www", "intranet", "private network", "accessible only to employees", "iot", "internet of things", "application running on the internet", "communication protocols")),
        ObjectiveDefinition("network-technologies.communication-media", "Communication media", "Choose suitable wired and wireless communication media for networking tasks.", ("bluetooth", "wi-fi", "wifi", "5g", "4g", "fibre", "fiber", "optical", "wireless", "communication medium", "coaxial", "coaxial cable", "two conductors", "central single strand", "braided together", "twisted pair", "ethernet cable")),
        ObjectiveDefinition("network-technologies.network-devices", "Network devices", "Explain the roles of NICs, switches, routers, servers and related network hardware.", ("router", "switch", "switched hub", "nic", "file server", "server", "connects devices", "routes packets", "connect to a network")),
        ObjectiveDefinition("network-technologies.topologies", "Network topologies", "Recognise bus, star and ring topologies and their advantages or disadvantages.", ("topology", "bus", "star", "ring", "backbone", "terminator", "central device", "node to node", "closed loop")),
        ObjectiveDefinition("network-technologies.network-benefits-and-limitations", "Network benefits and limitations", "Explain benefits and limitations of connecting computers in a network.", ("advantage", "benefit", "disadvantage", "drawback", "share files", "share hardware", "communication method", "email", "instant messaging", "video conferencing", "software costs", "performance", "collision", "privacy issues", "reliability", "hackers", "viruses", "smart devices")),
    ),
    "cyberspace-network-security-and-data-transfer": (
        ObjectiveDefinition("cyberspace-network-security-and-data-transfer.cybercrime", "Cybercrime", "Identify common cybercrimes and what makes them harmful.", ("cybercrime", "hacking", "cyber stalking", "data theft", "denial of service", "dos", "ddos", "digital forgery", "cyber defamation", "spamming", "spam", "phishing", "wikileaks", "stolen data", "whistleblowing", "confidential information", "public interest", "wrongdoing", "large numbers of requests almost simultaneously")),
        ObjectiveDefinition("cyberspace-network-security-and-data-transfer.malware", "Malware", "Recognise common forms of malware and how they behave.", ("malware", "virus", "worm", "trojan", "spyware", "key logger", "keylogger", "replicates itself", "attach itself to other programs", "malicious software program")),
        ObjectiveDefinition("cyberspace-network-security-and-data-transfer.protection-measures", "Protection measures", "Explain how passwords, backups, firewalls and access levels help protect data and networks.", ("password", "backup", "firewall", "levels of access", "read only", "read and write", "protect data", "prevent hackers", "stop hackers gaining entry", "data security", "copied and archived", "restored if the original is corrupted")),
        ObjectiveDefinition("cyberspace-network-security-and-data-transfer.encryption-and-access-control", "Encryption and access control", "Explain encryption and controlled access to data on networks.", ("encryption", "encrypted", "key", "scramble", "access control", "permission", "secure transfer", "manager can install software")),
        ObjectiveDefinition("cyberspace-network-security-and-data-transfer.data-transfer-protocols", "Data transfer protocols", "Recognise the role and purpose of FTP, HTTP and HTTPS.", ("protocol", "ftp", "http", "https", "transfer web pages", "send and receive files", "secure web", "packet switching", "data packets", "router")),
    ),
    "cloud-technology": (
        ObjectiveDefinition("cloud-technology.cloud-computing-concepts", "Cloud computing concepts", "Define cloud computing and explain how remote services replace local provision.", ("cloud computing", "what is cloud computing", "provided by a cloud provider", "services over the internet", "remote servers", "would normally be provided by a local area network")),
        ObjectiveDefinition("cloud-technology.cloud-advantages", "Cloud advantages", "Explain organisational benefits such as lower cost, scalability and accessibility.", ("advantage", "lower initial cost", "rent", "scalable", "scalability", "access from any location", "bandwidth can be rented")),
        ObjectiveDefinition("cloud-technology.cloud-disadvantages", "Cloud disadvantages", "Explain risks and limitations such as dependence on connectivity and provider lock-in.", ("disadvantage", "internet connection", "downtime", "security concern", "provider", "lock-in", "moving data", "different provider")),
        ObjectiveDefinition("cloud-technology.cloud-gaming", "Cloud gaming", "Recognise cloud gaming models and their technical implications.", ("cloud gaming", "cloud-supported gaming", "online distribution of games", "video streaming", "file streaming", "executed on the provider", "downloaded incrementally", "streamed to the user", "game developers", "helped customers")),
        ObjectiveDefinition("cloud-technology.cloud-file-sharing-and-collaboration", "Cloud file sharing and collaboration", "Explain the impact of cloud storage and sharing on collaboration.", ("file storage and sharing service", "dropbox", "onedrive", "google drive", "file sharing", "collaborative", "different offices", "share files", "collaboration", "real time feedback", "two people in different offices")),
    ),
    "ethical-legal-and-environmental-impact": (
        ObjectiveDefinition("ethical-legal-and-environmental-impact.internet-misuse-and-ethics", "Internet misuse and ethics", "Recognise unethical online behaviour and misuse of digital technology.", ("internet misuse", "misuse", "social media", "cyberbullying", "nasty comments", "harass", "ethical", "reputation")),
        ObjectiveDefinition("ethical-legal-and-environmental-impact.copyright-plagiarism-and-law", "Copyright, plagiarism and law", "Apply the main legal rules around copying, downloading and passing work off as your own.", ("copyright", "copyright design", "copyright, design and patents", "plagiarism", "illegally downloads", "data protection act", "computer misuse act", "consumer contracts", "consumer contracts regulations", "contracts regulations", "rights of customers when shopping online", "protects the rights of customers", "purchasing goods and services online", "digitally created media", "intellectual property rights", "software copying", "copy and gives it to his friend", "information commissioner", "act is broken", "law did the company break")),
        ObjectiveDefinition("ethical-legal-and-environmental-impact.gps-concepts-and-operation", "GPS concepts and operation", "Explain what GPS is and how location is calculated.", ("gps", "global positioning system", "what does the acronym gps stand for", "triangulation", "satellite", "three satellites", "location")),
        ObjectiveDefinition("ethical-legal-and-environmental-impact.gps-uses-and-benefits", "GPS uses and benefits", "Recognise practical uses and benefits of GPS-enabled services.", ("sat nav", "ships navigate", "track a lost phone", "use of gps", "recreational use", "navigate", "gives the user directions to a destination", "navigation system")),
        ObjectiveDefinition("ethical-legal-and-environmental-impact.gps-risks-privacy-and-accuracy", "GPS risks, privacy and accuracy", "Explain privacy concerns and factors affecting GPS accuracy.", ("without permission", "privacy", "inaccurate location", "indoors", "works best indoors", "signal blocked", "accuracy", "track a person's location")),
        ObjectiveDefinition("ethical-legal-and-environmental-impact.environmental-impact", "Environmental impact", "Recognise environmental issues associated with digital technology such as e-waste and energy use.", ("environmental", "e-waste", "waste electrical", "recycling", "energy consumption", "carbon footprint")),
    ),
    "changes-in-employment-opportunities-skills-requirements-and-work-practices": (
        ObjectiveDefinition("changes-in-employment-opportunities-skills-requirements-and-work-practices.teleworking", "Teleworking", "Explain advantages, disadvantages and requirements of teleworking.", ("teleworking", "work from home", "remote staff", "reduced overheads", "geographical restriction", "home working")),
        ObjectiveDefinition("changes-in-employment-opportunities-skills-requirements-and-work-practices.job-displacement-and-automation", "Job displacement and automation", "Explain how automation and digital technology can remove or change jobs.", ("job displacement", "job losses", "robots", "automation", "low-skilled workers", "productivity")),
        ObjectiveDefinition("changes-in-employment-opportunities-skills-requirements-and-work-practices.new-ict-job-roles", "New ICT job roles", "Recognise new job roles created by digital technology.", ("new job role", "new, skilled job opportunities", "positive impact of digital technology on employment", "web designer", "app developer", "social media", "ict consultant", "ict technician", "programmer", "software engineer")),
        ObjectiveDefinition("changes-in-employment-opportunities-skills-requirements-and-work-practices.training-and-skills-development", "Training and skills development", "Explain the need for retraining and new digital skills in the workplace.", ("retrain", "reskill", "training", "skills", "new software packages", "learn new skills")),
        ObjectiveDefinition("changes-in-employment-opportunities-skills-requirements-and-work-practices.work-patterns-and-flexibility", "Work patterns and flexibility", "Explain how digital technology changes working hours, location and work patterns.", ("flexible hours", "flexible working", "work patterns", "any geographic location", "wider recruitment area", "remote working", "change in work patterns", "commuting", "flexibility")),
    ),
    "health-and-safety": (
        ObjectiveDefinition("health-and-safety.rsi", "Repetitive strain injury", "Recognise RSI, its causes and how to reduce it.", ("rsi", "repetitive strain injury", "mouse clicking", "typing", "wrist", "keyboard", "joypad")),
        ObjectiveDefinition("health-and-safety.eye-strain", "Eye strain", "Recognise causes of eye strain and suitable screen or lighting adjustments.", ("eye strain", "anti-glare", "brightness", "contrast", "lighting", "sunlight", "screen resolution", "blurry eyes", "headaches", "screen glare")),
        ObjectiveDefinition("health-and-safety.back-strain-and-posture", "Back strain and posture", "Explain posture, seating and workstation setup needed to reduce back strain.", ("back strain", "back pain", "backache", "posture", "feet flat", "footrest", "chair", "adjustable chair")),
        ObjectiveDefinition("health-and-safety.ergonomic-prevention", "Ergonomic prevention", "Apply ergonomic measures and healthy working habits to reduce harm.", ("ergonomic", "regular breaks", "wrist rests", "adjustable", "prevention method", "prevent or reduce")),
        ObjectiveDefinition("health-and-safety.workplace-and-electrical-safety", "Workplace and electrical safety", "Recognise employer safety responsibilities and safe practice around electrical equipment.", ("safe working environment", "employer", "weee", "fire extinguisher", "anti-static", "static build-up", "electrical equipment", "snacking", "trip hazard", "electrical safety")),
        ObjectiveDefinition("health-and-safety.gaming-related-health-risks", "Gaming-related health risks", "Recognise health hazards associated with prolonged gaming.", ("computer gaming", "gaming", "joypad", "gamer", "health hazard")),
    ),
    "digital-applications": (
        ObjectiveDefinition("digital-applications.online-training-and-vles", "Online training and VLEs", "Explain the benefits, drawbacks and features of online training and virtual learning environments.", ("online training", "online learning", "vle", "virtual learning environment", "google classroom", "learner", "training costs", "human interaction")),
        ObjectiveDefinition("digital-applications.e-commerce-models", "E-commerce models", "Define e-commerce and distinguish B2B and B2C models.", ("e-commerce", "b2b", "b2c", "business to business", "business to consumer", "commercial transactions")),
        ObjectiveDefinition("digital-applications.online-shopping", "Online shopping", "Explain advantages, disadvantages and risks of online shopping for customers.", ("online shopping", "goods may not meet expectations", "delivered", "delivery", "compare prices", "shop from the comfort")),
        ObjectiveDefinition("digital-applications.online-banking", "Online banking", "Explain customer and bank advantages, risks and technical issues in online banking.", ("online banking", "online bank user", "bank account", "mobile banking", "bank teller", "public wi-fi", "bank's website", "hacked")),
        ObjectiveDefinition("digital-applications.mobile-apps-and-strategy", "Mobile apps and strategy", "Recognise app ecosystems, mobile-first design and app monetisation.", ("mobile first", "mobile app", "in-app purchase", "iap", "app developer", "mobile web browsing")),
        ObjectiveDefinition("digital-applications.digital-games-and-online-experiences", "Digital games and online experiences", "Recognise examples and characteristics of digital gaming experiences such as MMOGs.", ("mmog", "massively multiplayer online game", "world of warcraft", "adventure", "crowther and wood", "online game")),
        ObjectiveDefinition("digital-applications.simulation-and-forecasting", "Simulation and forecasting", "Recognise how simulations and forecast-driven digital applications are used in real contexts.", ("flight simulator", "simulator", "weather forecast", "weather forecasts", "pilots", "forecasting")),
        ObjectiveDefinition("digital-applications.immersive-tech-and-gamification", "Immersive tech and gamification", "Distinguish simulation, AR, VR and gamification and recognise their uses.", ("simulation", "augmented reality", "virtual reality", "gamification", "game-playing elements", "computer-generated environment")),
        ObjectiveDefinition("digital-applications.gaming-impacts", "Gaming impacts", "Recognise non-health disadvantages and social impacts of gaming.", ("gaming", "addiction", "schoolwork suffers", "waste of time", "computer gaming")),
    ),
}


OBJECTIVES_BY_CODE: dict[str, ObjectiveDefinition] = {
    objective.code: objective
    for objectives in OBJECTIVE_CATALOG.values()
    for objective in objectives
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _keyword_score(keyword: str, haystack: str) -> int:
    needle = _normalize_text(keyword)
    if not needle:
        return 0
    if " " in needle or "/" in needle or "-" in needle:
        return 3 if needle in haystack else 0
    pattern = rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])"
    return 2 if re.search(pattern, haystack) else 0


def build_objective_haystack(*parts: object) -> str:
    flat: list[str] = []
    for part in parts:
        if isinstance(part, str):
            flat.append(part)
        elif isinstance(part, Iterable):
            for item in part:
                flat.append(str(item))
        elif part is not None:
            flat.append(str(part))
    return _normalize_text(" ".join(flat))


def infer_objective_codes(
    topic_slug: str,
    *,
    stem: str,
    answer: str,
    source_locator: str,
    qtype_label: str,
    tags: list[str],
    content_blocks: list[dict],
    max_codes: int = 2,
) -> list[str]:
    objectives = OBJECTIVE_CATALOG.get(topic_slug, ())
    if not objectives:
        return []

    block_text: list[str] = []
    for block in content_blocks:
        if block.get("type") == "text":
            block_text.append(block.get("text", ""))
        elif block.get("type") == "figure":
            block_text.append(block.get("caption", ""))
        elif block.get("type") == "list_block":
            block_text.append(block.get("label", ""))
            block_text.extend(block.get("items", []))

    haystack = build_objective_haystack(
        stem,
        answer,
        source_locator,
        qtype_label,
        tags,
        block_text,
    )
    scores: list[tuple[int, str]] = []
    for objective in objectives:
        score = sum(_keyword_score(keyword, haystack) for keyword in objective.keywords)
        if score > 0:
            scores.append((score, objective.code))

    if not scores:
        return []

    scores.sort(key=lambda item: (-item[0], item[1]))
    selected = [scores[0][1]]
    top_score = scores[0][0]

    for score, code in scores[1:]:
        if len(selected) >= max_codes:
            break
        if score >= 3 and score >= top_score - 1:
            selected.append(code)

    question_haystack = build_objective_haystack(stem, answer, qtype_label, tags, block_text)
    if topic_slug == "ethical-legal-and-environmental-impact":
        law_signals = ("copyright", "plagiarism", "data protection act", "computer misuse act", "illegal", "law")
        gps_privacy_signals = ("gps", "location", "satellite", "triangulation", "privacy", "social media")
        if (
            "ethical-legal-and-environmental-impact.copyright-plagiarism-and-law" in selected
            and any(signal in question_haystack for signal in gps_privacy_signals)
            and not any(signal in question_haystack for signal in law_signals)
        ):
            selected = [
                code
                for code in selected
                if code != "ethical-legal-and-environmental-impact.copyright-plagiarism-and-law"
            ]
        if (
            "gps" in question_haystack
            and "ethical-legal-and-environmental-impact.copyright-plagiarism-and-law" in selected
            and not any(signal in question_haystack for signal in law_signals)
        ):
            selected = [
                code
                for code in selected
                if code != "ethical-legal-and-environmental-impact.copyright-plagiarism-and-law"
            ]

    def promote(code: str) -> None:
        if code in selected:
            selected.remove(code)
        selected.insert(0, code)
        del selected[max_codes:]

    def include(code: str) -> None:
        if code in selected:
            return
        if len(selected) < max_codes:
            selected.append(code)

    if topic_slug == "network-technologies":
        device_signals = ("router", "switch", "nic", "file server")
        if any(signal in question_haystack for signal in device_signals):
            promote("network-technologies.network-devices")
        if "bluetooth" in question_haystack or "wi-fi" in question_haystack or "wifi" in question_haystack or "fibre" in question_haystack or "fiber" in question_haystack:
            include("network-technologies.communication-media")

    if topic_slug == "cloud-technology":
        if any(signal in question_haystack for signal in ("potential risk", "security concern", "hacker", "downtime", "lock-in")):
            promote("cloud-technology.cloud-disadvantages")

    if topic_slug == "ethical-legal-and-environmental-impact":
        if "gps" in question_haystack and any(signal in question_haystack for signal in ("privacy", "location", "indoors", "accuracy", "sharing")):
            promote("ethical-legal-and-environmental-impact.gps-risks-privacy-and-accuracy")
        elif "gps" in question_haystack and any(signal in question_haystack for signal in ("use of gps", "uses of gps", "recreational use", "sat nav", "navigate", "lost phone")):
            promote("ethical-legal-and-environmental-impact.gps-uses-and-benefits")
        elif "gps" in question_haystack:
            promote("ethical-legal-and-environmental-impact.gps-concepts-and-operation")

    return selected
