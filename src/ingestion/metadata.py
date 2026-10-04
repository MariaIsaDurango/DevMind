"""Metadatos de trazabilidad (contrato en docs/arquitectura.md).

Todo chunk debe llevar: source, section, repository, tech_stack, page.
ChromaDB solo acepta str/int/float/bool, por eso nunca se usa None.
"""
import re

DEFAULT_SECTION = "General"
UNKNOWN = "N/A"

# Palabras clave para deducir la tecnología cuando el documento no la declara.
TECH_KEYWORDS = {
    "GitLab CI": ["gitlab ci", "gitlab-ci", ".gitlab-ci"],
    "GitHub Actions": ["github actions", ".github/workflows"],
    "Kubernetes": ["kubernetes", "kubectl", "helm"],
    "Docker": ["docker", "dockerfile", "docker-compose"],
    "Terraform": ["terraform"],
    "FastAPI": ["fastapi"],
    "AWS": ["aws", "ec2", "s3 bucket"],
}

_REPO_RE = re.compile(r"^\s*(?:repositorio|repository)\s*:\s*(.+?)\s*$", re.I | re.M)
_TECH_RE = re.compile(r"^\s*(?:tecnolog[ií]a|tech[_ ]stack)\s*:\s*(.+?)\s*$", re.I | re.M)


def _compile_keyword_patterns() -> dict[str, list[re.Pattern]]:
    """Compila cada palabra clave con límites de palabra (\\b) para evitar falsos
    positivos como 'helmets' -> Kubernetes o 'laws' -> AWS."""
    patterns = {}
    for tech, keywords in TECH_KEYWORDS.items():
        patterns[tech] = [re.compile(r"\b" + re.escape(k) + r"\b", re.I) for k in keywords]
    return patterns


_TECH_PATTERNS = _compile_keyword_patterns()


def extract_doc_info(text: str, filename: str = "") -> tuple[str, str]:
    """Devuelve (repository, tech_stack) leyendo la cabecera del documento.

    Si el documento no declara 'Repositorio:' / 'Tecnología:', se intenta
    deducir la tecnología por palabras clave. Si no se puede, devuelve 'N/A'.
    """
    repo_match = _REPO_RE.search(text)
    tech_match = _TECH_RE.search(text)
    repository = repo_match.group(1) if repo_match else UNKNOWN

    if tech_match:
        tech_stack = tech_match.group(1)
    else:
        combined = f"{filename} {text}"
        scores = {
            tech: sum(len(p.findall(combined)) for p in patterns)
            for tech, patterns in _TECH_PATTERNS.items()
        }
        best = max(scores, key=scores.get)
        tech_stack = best if scores[best] > 0 else UNKNOWN
    return repository, tech_stack


def build_metadata(
    source: str,
    section: str | None = None,
    repository: str | None = None,
    tech_stack: str | None = None,
    page: int | None = None,
) -> dict:
    """Construye el diccionario de metadatos siguiendo el contrato."""
    return {
        "source": source,
        "section": section or DEFAULT_SECTION,
        "repository": repository or UNKNOWN,
        "tech_stack": tech_stack or UNKNOWN,
        "page": int(page) if page else 1,
    }
