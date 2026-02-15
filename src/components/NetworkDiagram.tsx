function Callout({ x, y, label }: { x: number; y: number; label: string }) {
  return (
    <g>
      <circle cx={x} cy={y} r="14" fill="#136f63" />
      <text x={x} y={y + 5} textAnchor="middle" fontSize="12" fill="#ffffff" fontWeight="700">
        {label}
      </text>
    </g>
  );
}

function WorkstationIcon({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x} y={y} width="38" height="24" rx="3" fill="#eef6ff" stroke="#3e5c76" strokeWidth="2" />
      <line x1={x + 19} y1={y + 24} x2={x + 19} y2={y + 30} stroke="#3e5c76" strokeWidth="2" />
      <rect x={x + 8} y={y + 30} width="22" height="4" rx="2" fill="#3e5c76" />
    </g>
  );
}

function SwitchIcon({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x} y={y} width="44" height="16" rx="3" fill="#f1f7fb" stroke="#3e5c76" strokeWidth="2" />
      <rect x={x + 5} y={y + 5} width="6" height="6" rx="1" fill="#3e5c76" />
      <rect x={x + 14} y={y + 5} width="6" height="6" rx="1" fill="#3e5c76" />
      <rect x={x + 23} y={y + 5} width="6" height="6" rx="1" fill="#3e5c76" />
      <rect x={x + 32} y={y + 5} width="6" height="6" rx="1" fill="#3e5c76" />
    </g>
  );
}

function RouterIcon({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <ellipse cx={x + 20} cy={y + 10} rx="20" ry="10" fill="#f1f7fb" stroke="#3e5c76" strokeWidth="2" />
      <line x1={x + 10} y1={y + 10} x2={x + 16} y2={y + 10} stroke="#3e5c76" strokeWidth="2" />
      <line x1={x + 24} y1={y + 10} x2={x + 30} y2={y + 10} stroke="#3e5c76" strokeWidth="2" />
      <polygon points={`${x + 16},${y + 7} ${x + 16},${y + 13} ${x + 20},${y + 10}`} fill="#3e5c76" />
      <polygon points={`${x + 24},${y + 7} ${x + 24},${y + 13} ${x + 20},${y + 10}`} fill="#3e5c76" />
    </g>
  );
}

function PrinterIcon({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x + 8} y={y} width="24" height="10" rx="1" fill="#eef6ff" stroke="#3e5c76" strokeWidth="2" />
      <rect x={x} y={y + 10} width="40" height="20" rx="3" fill="#d9e7f3" stroke="#3e5c76" strokeWidth="2" />
      <rect x={x + 10} y={y + 18} width="20" height="7" rx="1" fill="#f7fbff" stroke="#3e5c76" strokeWidth="1" />
    </g>
  );
}

export function NetworkDiagram({ diagramKey }: { diagramKey: string }) {
  if (diagramKey === "star_topology") {
    return (
      <figure className="diagram-shell">
        <figcaption>Star Topology Diagram</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 300" aria-label="Star topology diagram">
          <rect x="330" y="120" width="100" height="60" rx="8" fill="#dcecf0" stroke="#3e5c76" />
          <SwitchIcon x={358} y={142} />

          <rect x="80" y="50" width="110" height="60" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={116} y={64} />

          <rect x="570" y="50" width="110" height="60" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={606} y={64} />

          <rect x="80" y="210" width="110" height="60" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={116} y={224} />

          <rect x="570" y="210" width="110" height="60" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <PrinterIcon x={605} y={224} />

          <line x1="330" y1="145" x2="190" y2="80" stroke="#3e5c76" strokeWidth="3" />
          <line x1="430" y1="145" x2="570" y2="80" stroke="#3e5c76" strokeWidth="3" />
          <line x1="330" y1="155" x2="190" y2="240" stroke="#3e5c76" strokeWidth="3" />
          <line x1="430" y1="155" x2="570" y2="240" stroke="#3e5c76" strokeWidth="3" />

          <Callout x={135} y={35} label="1" />
          <Callout x={380} y={105} label="2" />
          <Callout x={625} y={195} label="3" />
          <Callout x={290} y={182} label="4" />
        </svg>
      </figure>
    );
  }

  if (diagramKey === "bus_topology") {
    return (
      <figure className="diagram-shell">
        <figcaption>Bus Topology Diagram</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 220" aria-label="Bus topology diagram">
          <line x1="80" y1="120" x2="680" y2="120" stroke="#3e5c76" strokeWidth="8" />
          <rect x="58" y="105" width="12" height="30" fill="#102a43" />
          <rect x="690" y="105" width="12" height="30" fill="#102a43" />

          <line x1="180" y1="120" x2="180" y2="70" stroke="#3e5c76" strokeWidth="3" />
          <rect x="130" y="25" width="100" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={161} y={31} />

          <line x1="380" y1="120" x2="380" y2="70" stroke="#3e5c76" strokeWidth="3" />
          <rect x="330" y="25" width="100" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={361} y={31} />

          <line x1="560" y1="120" x2="560" y2="70" stroke="#3e5c76" strokeWidth="3" />
          <rect x="510" y="25" width="100" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={541} y={31} />

          <Callout x={60} y={82} label="1" />
          <Callout x={380} y={155} label="2" />
          <Callout x={560} y={24} label="3" />
        </svg>
      </figure>
    );
  }

  if (diagramKey === "ring_topology") {
    return (
      <figure className="diagram-shell">
        <figcaption>Ring Topology Diagram</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 250" aria-label="Ring topology diagram">
          <ellipse cx="380" cy="130" rx="280" ry="85" fill="none" stroke="#3e5c76" strokeWidth="4" />

          <rect x="120" y="105" width="95" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={148} y={112} />

          <rect x="332" y="30" width="95" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={360} y={37} />

          <rect x="545" y="105" width="95" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={573} y={112} />

          <rect x="332" y="185" width="95" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={360} y={192} />

          <Callout x={380} y={26} label="1" />
          <Callout x={650} y={130} label="2" />
          <Callout x={520} y={50} label="3" />
        </svg>
      </figure>
    );
  }

  if (diagramKey === "lan_internet_path") {
    return (
      <figure className="diagram-shell">
        <figcaption>LAN to Internet Path</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 220" aria-label="LAN to internet path diagram">
          <rect x="40" y="85" width="130" height="55" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <WorkstationIcon x={86} y={96} />

          <rect x="220" y="85" width="110" height="55" rx="6" fill="#dcecf0" stroke="#3e5c76" />
          <SwitchIcon x={253} y={104} />

          <rect x="380" y="85" width="110" height="55" rx="6" fill="#dcecf0" stroke="#3e5c76" />
          <RouterIcon x={415} y={102} />

          <ellipse cx="640" cy="112" rx="85" ry="48" fill="#eef7ff" stroke="#3e5c76" />
          <path d="M600 118 Q610 95 630 112 Q645 82 664 112 Q685 102 686 122 Z" fill="#dcecf0" stroke="#3e5c76" strokeWidth="2" />

          <line x1="170" y1="112" x2="220" y2="112" stroke="#3e5c76" strokeWidth="3" />
          <line x1="330" y1="112" x2="380" y2="112" stroke="#3e5c76" strokeWidth="3" />
          <line x1="490" y1="112" x2="555" y2="112" stroke="#3e5c76" strokeWidth="3" />

          <Callout x={105} y={70} label="1" />
          <Callout x={275} y={70} label="2" />
          <Callout x={435} y={70} label="3" />
          <Callout x={640} y={52} label="4" />
        </svg>
      </figure>
    );
  }

  if (diagramKey === "media_links") {
    return (
      <figure className="diagram-shell">
        <figcaption>Communication Media Scenarios</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 280" aria-label="Communication media scenarios diagram">
          <rect x="40" y="35" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="100" y="63" textAnchor="middle" fontSize="12">Phone</text>
          <rect x="230" y="35" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="290" y="63" textAnchor="middle" fontSize="12">Headphones</text>
          <line x1="160" y1="58" x2="230" y2="58" stroke="#3e5c76" strokeWidth="3" strokeDasharray="6 4" />

          <rect x="40" y="120" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="100" y="148" textAnchor="middle" fontSize="12">Home Router</text>
          <rect x="230" y="120" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="290" y="148" textAnchor="middle" fontSize="12">Smart TV</text>
          <line x1="160" y1="143" x2="230" y2="143" stroke="#3e5c76" strokeWidth="3" strokeDasharray="6 4" />

          <rect x="410" y="35" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="470" y="63" textAnchor="middle" fontSize="12">Traveller Phone</text>
          <ellipse cx="640" cy="58" rx="80" ry="30" fill="#eef7ff" stroke="#3e5c76" />
          <text x="640" y="62" textAnchor="middle" fontSize="12">Cloud Files</text>
          <line x1="530" y1="58" x2="560" y2="58" stroke="#3e5c76" strokeWidth="3" strokeDasharray="6 4" />

          <rect x="410" y="120" width="120" height="45" rx="6" fill="#f7fbff" stroke="#3e5c76" />
          <text x="470" y="148" textAnchor="middle" fontSize="12">Business LAN</text>
          <ellipse cx="640" cy="143" rx="80" ry="30" fill="#eef7ff" stroke="#3e5c76" />
          <text x="640" y="147" textAnchor="middle" fontSize="12">Internet</text>
          <line x1="530" y1="143" x2="560" y2="143" stroke="#3e5c76" strokeWidth="3" />

          <Callout x={195} y={25} label="1" />
          <Callout x={195} y={110} label="2" />
          <Callout x={545} y={25} label="3" />
          <Callout x={545} y={110} label="4" />
        </svg>
      </figure>
    );
  }

  if (diagramKey === "fibre_properties") {
    return (
      <figure className="diagram-shell">
        <figcaption>Fibre-Optic Properties</figcaption>
        <svg className="network-diagram-svg" viewBox="0 0 760 210" aria-label="Fibre properties diagram">
          <rect x="90" y="45" width="260" height="120" rx="10" fill="#eef7ff" stroke="#3e5c76" />
          <text x="220" y="83" textAnchor="middle" fontSize="14">Property A</text>
          <text x="220" y="112" textAnchor="middle" fontSize="13">Transmission characteristic</text>

          <rect x="410" y="45" width="260" height="120" rx="10" fill="#eef7ff" stroke="#3e5c76" />
          <text x="540" y="83" textAnchor="middle" fontSize="14">Property B</text>
          <text x="540" y="112" textAnchor="middle" fontSize="13">Capacity characteristic</text>

          <Callout x={220} y={30} label="1" />
          <Callout x={540} y={30} label="2" />
        </svg>
      </figure>
    );
  }

  return null;
}
