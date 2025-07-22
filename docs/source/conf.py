# ── Project information ────────────────────────────────────────────────────
project   = 'Coexistence Simulator'
copyright = '2025, Stephen Itschner'
author    = 'Stephen Itschner'

# ── General configuration ──────────────────────────────────────────────────
from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
import re, pathlib, sys
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[2].as_posix())

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx.ext.viewcode",
]

autosummary_generate = True
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
html_theme = "sphinx_rtd_theme"

# ── 1. Pre‑processing the source (Python side) ────────────────────────────
_CTRL  = re.compile(r"[\x00-\x08\x0B-\x1F]")          # C0 except TAB/LF/CR
_ARROWS = {"➔": r"$\rightarrow$"}                     # extend as needed

def _clean(app, docname, source):
    """Strip stray control bytes & tame exotic glyphs before LaTeX sees them."""
    if app.builder.name != "latex":
        return
    txt = _CTRL.sub("", source[0])                     # kill ^H, ^K, …
    for bad, good in _ARROWS.items():
        txt = txt.replace(bad, good)                   # swap fancy arrows
    source[0] = txt

class _MathNoWrap(SphinxPostTransform):
    """Tag every math_block with ``nowrap`` for LaTeX output.

    Sphinx then emits plain ``\[ … \]`` instead of ``\begin{split}``, so
    nested ``cases`` (or other multi‑& environments) no longer trip amsmath.
    """
    builders = ("latex",)          # run only when producing LaTeX/PDF
    default_priority = 5           # early, but after math nodes exist

    def run(self) -> None:         # -> None keeps mypy happy
        for node in self.document.findall(nodes.math_block):
            node["nowrap"] = True


def setup(app):
    app.connect("source-read", _clean)
    app.add_post_transform(_MathNoWrap)

# ── 2. LaTeX / PDF tweaks (TeX side) ───────────────────────────────────────
latex_engine = "xelatex"

latex_elements = {
    "preamble": r"""
% ----------------------------------------------------------------------
%  A.  Map troublesome Unicode characters to safe TeX equivalents
% ----------------------------------------------------------------------
\usepackage{newunicodechar}
\newunicodechar{‒}{\textendash}         % figure dash
\newunicodechar{–}{\textendash}         % en‑dash
\newunicodechar{—}{\textemdash}         % em‑dash
\newunicodechar{‑}{-}                   % non‑breaking hyphen
\newunicodechar{ }{\nobreakspace}       % NBSP (U+00A0)
\newunicodechar{ }{\,}                  % narrow NBSP (U+202F)
\newunicodechar{•}{\textbullet}         % bullet
\newunicodechar{▸}{\textbullet}         % small triangle bullet
\newunicodechar{→}{\textrightarrow}     % U+2192
\newunicodechar{↔}{\textleftrightarrow} % U+2194
\newunicodechar{↦}{\ensuremath{\mapsto}}% U+21A6
\newunicodechar{⟶}{\textrightarrow}     % U+27F6
\newunicodechar{♯}{\#}                  % music sharp = hash
\newunicodechar{∗}{\ensuremath{\ast}}   % math star
% Add more with \newunicodechar{<char>}{<replacement>} as needed.

% ----------------------------------------------------------------------
%  B.  Keep #, &, _ literals from breaking longtable’s internal macros
% ----------------------------------------------------------------------
\usepackage{etoolbox}
\makeatletter
\AtBeginEnvironment{longtable}{%
  \catcode`\#=12 \catcode`\&=12 \catcode`\_=12
}
\AtEndEnvironment{longtable}{%
  \catcode`\#=6  \catcode`\&=4  \catcode`\_=8
}
\makeatother
"""
    # You can add more LaTeX keys here (e.g. 'sphinxsetup', 'figure_align', ...)
}
