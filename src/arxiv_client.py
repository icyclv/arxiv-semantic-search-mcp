"""arXiv API client for retrieving papers and metadata."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, cast
import re

import httpx
import xml.etree.ElementTree as ET
from .models import ArxivPaper, SearchResult

logger = logging.getLogger(__name__)

# A static dictionary of arXiv categories and their descriptions.
ARXIV_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.AR": "Hardware Architecture",
    "cs.CC": "Computational Complexity",
    "cs.CE": "Computational Engineering, Finance, and Science",
    "cs.CG": "Computational Geometry",
    "cs.CL": "Computation and Language",
    "cs.CR": "Cryptography and Security",
    "cs.CV": "Computer Vision and Pattern Recognition",
    "cs.CY": "Computers and Society",
    "cs.DB": "Databases",
    "cs.DC": "Distributed, Parallel, and Cluster Computing",
    "cs.DL": "Digital Libraries",
    "cs.DM": "Discrete Mathematics",
    "cs.DS": "Data Structures and Algorithms",
    "cs.ET": "Emerging Technologies",
    "cs.FL": "Formal Languages and Automata Theory",
    "cs.GL": "General Literature",
    "cs.GR": "Graphics",
    "cs.GT": "Computer Science and Game Theory",
    "cs.HC": "Human-Computer Interaction",
    "cs.IR": "Information Retrieval",
    "cs.IT": "Information Theory",
    "cs.LG": "Machine Learning",
    "cs.LO": "Logic in Computer Science",
    "cs.MA": "Multiagent Systems",
    "cs.MM": "Multimedia",
    "cs.MS": "Mathematical Software",
    "cs.NA": "Numerical Analysis",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.NI": "Networking and Internet Architecture",
    "cs.OH": "Other Computer Science",
    "cs.OS": "Operating Systems",
    "cs.PF": "Performance",
    "cs.PL": "Programming Languages",
    "cs.RO": "Robotics",
    "cs.SC": "Symbolic Computation",
    "cs.SD": "Sound",
    "cs.SE": "Software Engineering",
    "cs.SI": "Social and Information Networks",
    "cs.SY": "Systems and Control",
    "econ.EM": "Econometrics",
    "eess.AS": "Audio and Speech Processing",
    "eess.IV": "Image and Video Processing",
    "eess.SP": "Signal Processing",
    "math.AC": "Commutative Algebra",
    "math.AG": "Algebraic Geometry",
    "math.AP": "Analysis of PDEs",
    "math.AT": "Algebraic Topology",
    "math.CA": "Classical Analysis and ODEs",
    "math.CO": "Combinatorics",
    "math.CT": "Category Theory",
    "math.CV": "Complex Variables",
    "math.DG": "Differential Geometry",
    "math.DS": "Dynamical Systems",
    "math.FA": "Functional Analysis",
    "math.GM": "General Mathematics",
    "math.GN": "General Topology",
    "math.GR": "Group Theory",
    "math.GT": "Geometric Topology",
    "math.HO": "History and Overview",
    "math.IT": "Information Theory",
    "math.KT": "K-Theory and Homology",
    "math.LO": "Logic",
    "math.MG": "Metric Geometry",
    "math.MP": "Mathematical Physics",
    "math.NA": "Numerical Analysis",
    "math.NT": "Number Theory",
    "math.OA": "Operator Algebras",
    "math.OC": "Optimization and Control",
    "math.PR": "Probability",
    "math.QA": "Quantum Algebra",
    "math.RA": "Rings and Algebras",
    "math.RT": "Representation Theory",
    "math.SG": "Symplectic Geometry",
    "math.SP": "Spectral Theory",
    "math.ST": "Statistics Theory",
    "astro-ph.CO": "Cosmology and Nongalactic Astrophysics",
    "astro-ph.EP": "Earth and Planetary Astrophysics",
    "astro-ph.GA": "Astrophysics of Galaxies",
    "astro-ph.HE": "High Energy Astrophysical Phenomena",
    "astro-ph.IM": "Instrumentation and Methods for Astrophysics",
    "astro-ph.SR": "Solar and Stellar Astrophysics",
    "cond-mat.dis-nn": "Disordered Systems and Neural Networks",
    "cond-mat.mes-hall": "Mesoscale and Nanoscale Physics",
    "cond-mat.mtrl-sci": "Materials Science",
    "cond-mat.other": "Other Condensed Matter",
    "cond-mat.quant-gas": "Quantum Gases",
    "cond-mat.soft": "Soft Condensed Matter",
    "cond-mat.stat-mech": "Statistical Mechanics",
    "cond-mat.str-el": "Strongly Correlated Electrons",
    "cond-mat.supr-con": "Superconductivity",
    "gr-qc": "General Relativity and Quantum Cosmology",
    "hep-ex": "High Energy Physics - Experiment",
    "hep-lat": "High Energy Physics - Lattice",
    "hep-ph": "High Energy Physics - Phenomenology",
    "hep-th": "High Energy Physics - Theory",
    "math-ph": "Mathematical Physics",
    "nlin.AO": "Adaptation and Self-Organizing Systems",
    "nlin.CD": "Chaotic Dynamics",
    "nlin.CG": "Cellular Automata and Lattice Gases",
    "nlin.PS": "Pattern Formation and Solitons",
    "nlin.SI": "Exactly Solvable and Integrable Systems",
    "nucl-ex": "Nuclear Experiment",
    "nucl-th": "Nuclear Theory",
    "physics.acc-ph": "Accelerator Physics",
    "physics.ao-ph": "Atmospheric and Oceanic Physics",
    "physics.app-ph": "Applied Physics",
    "physics.atm-clus": "Atomic and Molecular Clusters",
    "physics.atom-ph": "Atomic Physics",
    "physics.bio-ph": "Biological Physics",
    "physics.chem-ph": "Chemical Physics",
    "physics.class-ph": "Classical Physics",
    "physics.comp-ph": "Computational Physics",
    "physics.data-an": "Data Analysis, Statistics and Probability",
    "physics.ed-ph": "Physics Education",
    "physics.flu-dyn": "Fluid Dynamics",
    "physics.gen-ph": "General Physics",
    "physics.geo-ph": "Geophysics",
    "physics.hist-ph": "History and Philosophy of Physics",
    "physics.ins-det": "Instrumentation and Detectors",
    "physics.med-ph": "Medical Physics",
    "physics.optics": "Optics",
    "physics.plasm-ph": "Plasma Physics",
    "physics.pop-ph": "Popular Physics",
    "physics.soc-ph": "Physics and Society",
    "physics.space-ph": "Space Physics",
    "q-bio.BM": "Biomolecules",
    "q-bio.CB": "Cell Behavior",
    "q-bio.GN": "Genomics",
    "q-bio.MN": "Molecular Networks",
    "q-bio.NC": "Neurons and Cognition",
    "q-bio.OT": "Other Quantitative Biology",
    "q-bio.PE": "Populations and Evolution",
    "q-bio.QM": "Quantitative Methods",
    "q-bio.SC": "Subcellular Processes",
    "q-bio.TO": "Tissues and Organs",
    "q-fin.CP": "Computational Finance",
    "q-fin.EC": "Economics",
    "q-fin.GN": "General Finance",
    "q-fin.MF": "Mathematical Finance",
    "q-fin.PM": "Portfolio Management",
    "q-fin.PR": "Pricing of Securities",
    "q-fin.RM": "Risk Management",
    "q-fin.ST": "Statistical Finance",
    "q-fin.TR": "Trading and Market Microstructure",
    "quant-ph": "Quantum Physics",
    "stat.AP": "Applications",
    "stat.CO": "Computation",
    "stat.ME": "Methodology",
    "stat.ML": "Machine Learning",
    "stat.OT": "Other Statistics",
    "stat.TH": "Statistics Theory",
}

ARXIV_MAJOR_CATEGORIES = set([code.split('.')[0] for code in ARXIV_CATEGORIES.keys()])


class ArxivClient:
    """Client for interacting with the public arXiv API."""

    def __init__(self, timeout: int = 30):
        self.base_url = "https://export.arxiv.org/api/query"
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    def get_categories(self, major_category: Optional[str] = None) -> Dict[str, str]:
        """Retrieves the list of arXiv categories."""
        if major_category:
            major_category = major_category.lower()
            if major_category not in ARXIV_MAJOR_CATEGORIES:
                logger.warning(f"'{major_category}' is not a valid major category.")
                return {}
            return {
                code: desc
                for code, desc in ARXIV_CATEGORIES.items()
                if code.lower().startswith(major_category)
            }
        return ARXIV_CATEGORIES

    @staticmethod
    def _parse_datetime(date_str: str) -> str:
        """Converts an ISO format datetime string to a YYYY-MM-DD format."""
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def _safe_get_text(element: Optional[ET.Element]) -> Optional[str]:
        """Safely retrieves the text content of an XML element."""
        return element.text if element is not None and element.text is not None else None

    def _parse_entry(self, entry: ET.Element, namespaces: Dict[str, str]) -> Optional[ArxivPaper]:
        """Parses a single <entry> element from the arXiv API response."""
        required_fields = {
            'id': entry.find('atom:id', namespaces),
            'title': entry.find('atom:title', namespaces),
            'summary': entry.find('atom:summary', namespaces),
            'published': entry.find('atom:published', namespaces)
        }

        if not all(self._safe_get_text(field) for field in required_fields.values()):
            return None

        authors = [
            name.text for author in entry.findall('atom:author', namespaces)
            if (name := author.find('atom:name', namespaces)) is not None and name.text
        ]
        if not authors:
            return None

        # Extract category terms, ensuring we only include string values and no None values
        category_terms = []
        for cat in entry.findall('atom:category', namespaces):
            term = cat.get('term')
            if term is not None:
                category_terms.append(term)
                
        if not category_terms:
            return None

        arxiv_id = cast(str, self._safe_get_text(required_fields['id'])).split('/')[-1].split('v')[0]
        comment = self._safe_get_text(entry.find('arxiv:comment', namespaces))

        return ArxivPaper(
            arxiv_id=arxiv_id,
            title=cast(str, self._safe_get_text(required_fields['title'])).strip(),
            authors=authors,
            abstract=cast(str, self._safe_get_text(required_fields['summary'])).strip(),
            categories=category_terms,
            published_date=self._parse_datetime(cast(str, self._safe_get_text(required_fields['published']))),
            comment=comment,
        )

    def _parse_response(self, response_text: str) -> List[ArxivPaper]:
        """Parses the full XML response from the arXiv API."""
        root = ET.fromstring(response_text)
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        total_results_elem = root.find('.//opensearch:totalResults', namespaces)
        total_results = int(cast(str, self._safe_get_text(total_results_elem)))
        logger.info(f"Total results found: {total_results}")

        papers = []
        for entry in root.findall('.//atom:entry', namespaces):
            try:
                paper = self._parse_entry(entry, namespaces)
                if paper:
                    papers.append(paper)
            except Exception as e:
                logger.error(f"Error parsing entry: {e}")
                continue

        return papers

    async def search(self, query: str, max_results: int = 10, start: int = 0, sort_by: str = "submittedDate", sort_order: str = "descending") -> List[ArxivPaper]:
        """Performs a keyword search on the arXiv API."""
        if max_results > 15 or max_results < 1:
            raise ValueError("Number of results per page must be between 1 and 15")
        if start < 0:
            raise ValueError("Start index must be greater than or equal to 0")
        params = {
            'search_query': query,
            'start': start,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        try:
            response = await self._client.get(self.base_url, params=params)
            response.raise_for_status()
            return self._parse_response(response.text)
        except httpx.HTTPError as e:
            logger.error(f"Error during arXiv API request: {e}")
            raise

    @staticmethod
    def normalize_arxiv_id(arxiv_id: str) -> str:
        """
        Normalizes various arXiv ID formats to the standard format required by the arXiv API.
        
        Handles the following formats:
        - Standard IDs: '2201.00001'
        - Versioned IDs: '2201.00001v1'
        - Full URLs: 'https://arxiv.org/abs/2201.00001'
        - URLs with versions: 'https://arxiv.org/abs/2201.00001v1'
        - PDF URLs: 'https://arxiv.org/pdf/2201.00001.pdf'
        
        Returns:
            str: Normalized arXiv ID (e.g., '2201.00001')
        """
        # Handle URLs
        if arxiv_id.startswith(('http://', 'https://')):
            # Extract the ID part from the URL
            url_pattern = r'arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:v[0-9]+)?)'
            match = re.search(url_pattern, arxiv_id)
            if match:
                arxiv_id = match.group(1)
                # Remove .pdf extension if present
                arxiv_id = arxiv_id.replace('.pdf', '')
        
        # Remove version suffix if present
        if 'v' in arxiv_id and re.match(r'^[0-9]+\.[0-9]+v[0-9]+$', arxiv_id):
            arxiv_id = arxiv_id.split('v')[0]
            
        return arxiv_id

    async def get_details(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """Fetches the details for a single paper by its arXiv ID."""
        # Normalize the arXiv ID to handle different formats
        normalized_id = self.normalize_arxiv_id(arxiv_id)
        params = {'id_list': normalized_id}
        
        try:
            logger.info(f"Fetching details for normalized arXiv ID: {normalized_id} (original: {arxiv_id})")
            response = await self._client.get(self.base_url, params=params)
            response.raise_for_status()
            result = self._parse_response(response.text)
            if len(result) > 0:
                return result[0]
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching details for {arxiv_id}: {e}")
            raise