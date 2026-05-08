"""Build a Word (.docx) version of REPORT.md.

Tables are populated with literal Unicode characters (×, −, ², ³, …) so they
render correctly in Word — no raw HTML entities.
"""
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

PLOTS = "/home/user/Maths/plots"
OUT = "/home/user/Maths/REPORT.docx"

doc = Document()

# Default font
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

# ---------- helpers ----------
def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    return h

def add_par(text, bold=False, italic=False, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if align is not None:
        p.alignment = align
    return p

def add_centered(text, bold=False, italic=False):
    return add_par(text, bold=bold, italic=italic, align=WD_ALIGN_PARAGRAPH.CENTER)

def add_mono(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Consolas"
    r.font.size = Pt(10)
    return p

def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def add_table(headers, rows, header_align=None, col_align=None, header_shade="D9E1F2"):
    """col_align: list of WD_ALIGN_PARAGRAPH for each column (data rows)."""
    n_cols = len(headers)
    t = doc.add_table(rows=1 + len(rows), cols=n_cols)
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = t.rows[0].cells
    for j, htext in enumerate(headers):
        hdr[j].text = ""
        p = hdr[j].paragraphs[0]
        r = p.add_run(htext)
        r.bold = True
        p.alignment = (header_align[j] if header_align
                       else WD_ALIGN_PARAGRAPH.CENTER)
        shade_cell(hdr[j], header_shade)

    for i, row in enumerate(rows, start=1):
        cells = t.rows[i].cells
        for j, val in enumerate(row):
            cells[j].text = ""
            p = cells[j].paragraphs[0]
            r = p.add_run(str(val))
            if col_align is not None:
                p.alignment = col_align[j]
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_paragraph()
    return t

def add_image(path, width_in=5.5):
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width_in))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ---------- Title ----------
title = doc.add_heading("Numerical Analysis Homework 2025-2026 — Report", level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_centered("NTUA, School of Mechanical Engineering", bold=True)
add_centered("Course: Numerical Analysis (K. Giannakoglou / V. Asouti)")
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run("Student key digits: ").bold = True
p.add_run("K1 = 6 (last digit of registration number),  K2 = 6 (second-to-last),  K3 = 0 (third-to-last).")

doc.add_paragraph(
    "All algorithms are implemented from scratch in solution.py. NumPy is used "
    "only for arrays / dense linear-algebra; matplotlib only for the plots. No "
    "black-box numerical solver is used."
)
doc.add_paragraph(
    "To reproduce: python3 solution.py — produces the plots in plots/ and the "
    "numerical log in results.txt."
)

# ---------- 1. Bezier curve ----------
add_heading("1. Bezier curve (6 control points)", 1)
add_heading("Control points", 2)
doc.add_paragraph("With K1=6, K2=6, K3=0:")
add_table(
    headers=["i", "Xᵢ", "Yᵢ"],
    rows=[
        ["0", "0.0", "0.0"],
        ["1", "3.0", "4 + K2/12 = 4.500000"],
        ["2", "4 + K1/10 = 4.600000", "10.0"],
        ["3", "5.5", "3.0"],
        ["4", "6.0", "5 + K3/8 = 5.000000"],
        ["5", "7.0", "0.0"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Mathematical equations", 2)
doc.add_paragraph("The degree-5 Bezier curve is the standard Bernstein form")
add_centered("B(t) = Σᵢ₌₀⁵ C(5,i) · tⁱ · (1−t)⁵⁻ⁱ · Pᵢ,    t ∈ [0,1].", italic=True)
doc.add_paragraph(
    "Substituting the control points and expanding into monomials in t we obtain "
    "(coefficients of t^k):"
)
add_table(
    headers=["k", "x(t)", "y(t)"],
    rows=[
        ["0", "0.000000", "0.000000"],
        ["1", "15.000000", "22.500000"],
        ["2", "−14.000000", "10.000000"],
        ["3", "7.000000", "−135.000000"],
        ["4", "−2.000000", "175.000000"],
        ["5", "1.000000", "−72.500000"],
    ],
)

doc.add_paragraph("Hence")
add_centered("x(t) = 15t − 14t² + 7t³ − 2t⁴ + t⁵", italic=True)
add_centered("y(t) = (45/2) t + 10t² − 135t³ + 175t⁴ − (145/2) t⁵", italic=True)
doc.add_paragraph(
    "(Sanity check: x(0)=y(0)=0,  x(1)=15−14+7−2+1=7,  "
    "y(1)=22.5+10−135+175−72.5=0 — both endpoints reproduce the first/last "
    "control points, as expected.)"
)

add_heading("Plot", 2)
doc.add_paragraph(
    "The curve was sampled at 100 equally-spaced t (Δt = 1/99) and is plotted "
    "with the control polygon — see plots/p1_bezier.png."
)
add_image(os.path.join(PLOTS, "p1_bezier.png"))

# ---------- 2. Tangent angle ----------
add_heading("2. Tangent angle along the curve", 1)
doc.add_paragraph(
    "For a parametric curve the slope is dy/dx = (dy/dt)/(dx/dt). Using the "
    "standard derivative formula for a degree-n Bezier curve,"
)
add_centered(
    "B′(t) = n · Σᵢ₌₀^(n−1) C(n−1,i) · tⁱ · (1−t)^(n−1−i) · (Pᵢ₊₁ − Pᵢ),", italic=True
)
doc.add_paragraph(
    "so B′(t) is itself a degree-4 Bezier curve with control points "
    "Qᵢ = 5(Pᵢ₊₁ − Pᵢ):"
)
add_table(
    headers=["i", "Qxᵢ", "Qyᵢ"],
    rows=[
        ["0", "15.0", "22.5"],
        ["1", "8.0", "27.5"],
        ["2", "4.5", "−35.0"],
        ["3", "2.5", "10.0"],
        ["4", "5.0", "−25.0"],
    ],
)

doc.add_paragraph("The tangent angle (in degrees) is")
add_centered("θ(t) = (180/π) · atan2(y′(t), x′(t)).", italic=True)
doc.add_paragraph(
    "Plotted in plots/p2_tangent.png. A few representative values: "
    "θ(0) = 56.310°, θ(0.25) = 51.821°, θ(0.5) = −35.078°, "
    "θ(0.75) = −67.486°, θ(1) = −78.690°. The angle is monotonically decreasing "
    "on t ∈ [≈0.1, 1], consistent with the visual shape of the curve "
    "(rising, turning over the maximum, then dropping)."
)
add_image(os.path.join(PLOTS, "p2_tangent.png"))

# ---------- 3. Volume of revolution ----------
add_heading("3. Volume of revolution (Gauss-Legendre quadrature)", 1)
doc.add_paragraph("The body of revolution about the x-axis has")
add_centered("V = π · ∫_{x(0)}^{x(1)} y(x)² dx  =  π · ∫₀¹ y(t)² · x′(t) dt.", italic=True)
doc.add_paragraph(
    "The integrand g(t) = y(t)² · x′(t) is the product of (deg 5)² = deg 10 and "
    "deg 4, hence a polynomial of degree 14. A Gauss-Legendre rule with m nodes "
    "is exact on polynomials of degree 2m−1, so an exact result needs m ≥ 8. "
    "Therefore the values at m = 2, 3, 4, 5 are approximate."
)
doc.add_paragraph(
    "The exact analytic value, obtained by polynomial expansion + term-by-term "
    "integration of g(t) (every monomial t^k contributes 1/(k+1)) is"
)
add_centered("V* = 344.572 848 084 958.", bold=True)

add_heading("Results", 2)
add_table(
    headers=["m", "V(m)", "|V(m) − V*|"],
    rows=[
        ["2", "351.117330512449", "6.544482 × 10⁰"],
        ["3", "321.380133749620", "2.319271 × 10¹"],
        ["4", "347.119878378522", "2.547030 × 10⁰"],
        ["5", "344.545194110158", "2.765397 × 10⁻²"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Comments", 2)
doc.add_paragraph(
    "The Gauss rule converges very fast despite the integrand being 14-th "
    "degree: the error drops from 6.5 (m = 2) to ~2.8 × 10⁻² (m = 5), i.e. "
    "two and a half orders of magnitude in three additional nodes. This is the "
    "classical geometric / super-algebraic convergence of Gauss-Legendre on "
    "smooth integrands. The non-monotone jump at m = 3 (worse than m = 2) is "
    "normal: the error of a Gauss rule depends on the (2m)-th derivative of the "
    "integrand and need not decrease monotonically."
)

# ---------- 4. Newton-Raphson ----------
add_heading("4. Eight equally-x-spaced points (Newton-Raphson)", 1)
doc.add_paragraph(
    "The Bezier curve has x(0)=0, x(1)=7 and x′(t) ≥ min(15, 8, 4.5, 2.5, 5) "
    "= 2.5 > 0, so x(t) is strictly increasing and the inverse problem "
    "x(t) = x* has a unique solution for every x* ∈ [0,7]. We pick"
)
add_centered("xᵢ* = 7·i / 7 = i,    i = 0, 1, …, 7,", italic=True)
doc.add_paragraph(
    "and solve f(t) = x(t) − xᵢ* = 0 by Newton-Raphson:"
)
add_centered("tₖ₊₁ = tₖ − (x(tₖ) − xᵢ*) / x′(tₖ)", italic=True)
doc.add_paragraph("with initial guess t₀ = xᵢ*/7. Tolerance: |f| < 10⁻¹².")

add_heading("Results (8 points)", 2)
add_table(
    headers=["i", "xᵢ*", "tᵢ", "yᵢ", "iters"],
    rows=[
        ["0", "0.000000", "0.00000000", "0.000000", "1"],
        ["1", "1.000000", "0.07123777", "1.609167", "5"],
        ["2", "2.000000", "0.15377571", "3.297141", "5"],
        ["3", "3.000000", "0.25244560", "4.781832", "6"],
        ["4", "4.000000", "0.37594681", "5.650274", "6"],
        ["5", "5.000000", "0.54083183", "5.355261", "5"],
        ["6", "6.000000", "0.76681091", "3.547728", "4"],
        ["7", "7.000000", "1.00000000", "0.000000", "1"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER]*5,
)

add_heading("Detailed convergence — x* = 2", 2)
add_table(
    headers=["k", "tₖ", "x(tₖ)", "f = x(tₖ) − x*"],
    rows=[
        ["0", "0.2857142857", "3.29469864",  "1.29470 × 10⁰"],
        ["1", "0.1344823991", "1.78045387", "−2.19546 × 10⁻¹"],
        ["2", "0.1534145566", "1.99596646", "−4.03354 × 10⁻³"],
        ["3", "0.1537755795", "1.99999856", "−1.43664 × 10⁻⁶"],
        ["4", "0.1537757082", "2.00000000", "−1.82743 × 10⁻¹³"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER]+[WD_ALIGN_PARAGRAPH.RIGHT]*3,
)

add_heading("Detailed convergence — x* = 5", 2)
add_table(
    headers=["k", "tₖ", "x(tₖ)", "f = x(tₖ) − x*"],
    rows=[
        ["0", "0.7142857143", "5.78776700",  "7.87767 × 10⁻¹"],
        ["1", "0.5221649859", "4.90202350", "−9.79765 × 10⁻²"],
        ["2", "0.5405198746", "4.99838940", "−1.61060 × 10⁻³"],
        ["3", "0.5408317483", "4.99999956", "−4.44899 × 10⁻⁷"],
        ["4", "0.5408318345", "5.00000000", "−3.28626 × 10⁻¹⁴"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER]+[WD_ALIGN_PARAGRAPH.RIGHT]*3,
)

doc.add_paragraph(
    "In both cases we observe the classic quadratic convergence of Newton's "
    "method: the error roughly squares each step (after the first iteration)."
)
doc.add_paragraph("The 8 points are plotted on the Bezier curve in plots/p4_eqspaced.png.")
add_image(os.path.join(PLOTS, "p4_eqspaced.png"))

# ---------- 5. Natural cubic spline ----------
add_heading("5. Natural cubic spline through these 8 points", 1)
doc.add_paragraph(
    "The 8 abscissae xᵢ = 0, 1, …, 7 are uniform, hᵢ = 1. With "
    "yᵢ = (0, 1.6092, 3.2971, 4.7818, 5.6503, 5.3553, 3.5477, 0) we build a "
    "piecewise-cubic S(x) of class C². Letting Mᵢ = S″(xᵢ), the natural-spline "
    "conditions M₀ = M₇ = 0 together with the continuity-of-second-derivative "
    "system"
)
add_centered(
    "hᵢ₋₁ Mᵢ₋₁ + 2(hᵢ₋₁ + hᵢ) Mᵢ + hᵢ Mᵢ₊₁ = 6 · ((yᵢ₊₁ − yᵢ)/hᵢ − (yᵢ − yᵢ₋₁)/hᵢ₋₁),    i = 1, …, n−1",
    italic=True,
)
doc.add_paragraph("yield a tridiagonal linear system. Solving it gives")

add_table(
    headers=["i", "Mᵢ"],
    rows=[
        ["0", "0.00000000"],
        ["1", "0.17022523"],
        ["2", "−0.20805769"],
        ["3", "−0.55768944"],
        ["4", "−1.25868369"],
        ["5", "−1.38830539"],
        ["6", "−2.26321500"],
        ["7", "0.00000000"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT],
)

doc.add_paragraph("On each interval [xᵢ, xᵢ₊₁] the spline is")
add_centered(
    "Sᵢ(x) = [Mᵢ (xᵢ₊₁ − x)³ + Mᵢ₊₁ (x − xᵢ)³] / (6 hᵢ) "
    "+ (yᵢ/hᵢ − Mᵢ hᵢ/6) (xᵢ₊₁ − x) "
    "+ (yᵢ₊₁/hᵢ − Mᵢ₊₁ hᵢ/6) (x − xᵢ).",
    italic=True,
)

doc.add_paragraph(
    "Plotted at 400 sample points in plots/p5_spline.png; superimposed against "
    "the Bezier curve in plots/p5_compare.png. The two curves are visually "
    "indistinguishable at the scale of the plot. A direct numerical comparison "
    "gives a maximum point-wise deviation of approximately "
    "max_x |y_s(x) − y_B(x)| ≈ 0.18 (occurring near the maximum where the "
    "curvature is largest). The Bezier curve is a single global degree-5 "
    "polynomial whereas the spline is a piecewise cubic forced through 8 sampled "
    "points; the small discrepancy is the natural error of the C²-cubic "
    "interpolant on a smooth curve sampled with Δx = 1."
)
add_image(os.path.join(PLOTS, "p5_spline.png"))
add_image(os.path.join(PLOTS, "p5_compare.png"))

# ---------- 6. Cubic B-spline ----------
add_heading("6. Cubic B-spline interpolation of 5 data points", 1)
add_heading("Data", 2)
add_table(
    headers=["i", "xᵢ", "yᵢ"],
    rows=[
        ["0", "0.5", "6.0"],
        ["1", "2.0", "2 + K2/12 = 2.500000"],
        ["2", "4 + K1/10 = 4.600000", "1.0"],
        ["3", "5.0", "4.0"],
        ["4", "6.0", "8 + K3/8 = 8.000000"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Setup", 2)
doc.add_paragraph(
    "Using uniform knot spacing and parameter uⱼ = j at data point j, each "
    "segment Sₖ(t), t ∈ [0,1], k = 0..3, is"
)
add_centered(
    "Sₖ(t) = (1/6) · [(1−t)³ Pₖ + (3t³ − 6t² + 4) Pₖ₊₁ "
    "+ (−3t³ + 3t² + 3t + 1) Pₖ₊₂ + t³ Pₖ₊₃].",
    italic=True,
)
doc.add_paragraph(
    "Imposing Sₖ(0) = (xₖ, yₖ) for k = 0..3 and S₃(1) = (x₄, y₄) gives 5 "
    "equations in the 7 unknown control points P₀, …, P₆. Two more come from "
    "the natural boundary conditions S″(0) = S″(end) = 0, which in uniform-"
    "B-spline form read"
)
add_centered("P₀ − 2 P₁ + P₂ = 0,    P₃ − 2 P₄ + P₅ = 0,", italic=True)
doc.add_paragraph(
    "and a 7×7 system is solved twice (once for x, once for y). The resulting "
    "control points are"
)
add_table(
    headers=["i", "Pᵢ,ₓ", "Pᵢ,ᵧ"],
    rows=[
        ["0", "−0.537500", "9.732143"],
        ["1", "0.500000",  "6.000000"],
        ["2", "1.537500",  "2.267857"],
        ["3", "5.350000",  "−0.071429"],
        ["4", "4.662500",  "4.017857"],
        ["5", "6.000000",  "8.000000"],
        ["6", "7.337500",  "11.982143"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Explicit polynomial of every segment", 2)
doc.add_paragraph(
    "Substituting and collecting in monomials, every segment has the form "
    "x(t) = αx₀ + αx₁ t + αx₂ t² + αx₃ t³, "
    "y(t) = αy₀ + αy₁ t + αy₂ t² + αy₃ t³:"
)
def seg_block(title, xs, ys):
    p = doc.add_paragraph()
    p.add_run(title).bold = True
    add_mono("  x(t) = " + xs)
    add_mono("  y(t) = " + ys)

seg_block("Segment 1/4 — between Q₀ and Q₁:",
          "0.500000 + 1.037500 t + 0 · t² + 0.462500 t³",
          "6.000000 − 3.732143 t + 0 · t² + 0.232143 t³")
seg_block("Segment 2/4 — between Q₁ and Q₂:",
          "2.000000 + 2.425000 t + 1.387500 t² − 1.212500 t³",
          "2.500000 − 3.035714 t + 0.696429 t² + 0.839286 t³")
seg_block("Segment 3/4 — between Q₂ and Q₃:",
          "4.600000 + 1.562500 t − 2.250000 t² + 1.087500 t³",
          "1.000000 + 0.875000 t + 3.214286 t² − 1.089286 t³")
seg_block("Segment 4/4 — between Q₃ and Q₄:",
          "5.000000 + 0.325000 t + 1.012500 t² − 0.337500 t³",
          "4.000000 + 4.035714 t − 0.053571 t² + 0.017857 t³")

doc.add_paragraph("(One easily checks Sₖ(0) = Qₖ and S₃(1) = Q₄.)")
doc.add_paragraph(
    "The curve sampled at 400 points and the control polygon are in plots/p6_bspline.png."
)
add_image(os.path.join(PLOTS, "p6_bspline.png"))

# ---------- 7. Intersections ----------
add_heading("7. Intersections of the two curves (fixed-point iteration)", 1)
doc.add_paragraph(
    "The cubic spline of §5 is y = y_s(x) for x ∈ [0,7]; the cubic B-spline "
    "of §6 is the parametric curve (x_b(u), y_b(u)) for u ∈ [0,4]. An "
    "intersection satisfies"
)
add_centered("F(u) := y_b(u) − y_s(x_b(u)) = 0.", italic=True)
doc.add_paragraph(
    "This is rewritten as the fixed-point problem u = G(u) := u − α F(u) "
    "with constant relaxation α. Convergence of the basic fixed-point iteration"
)
add_centered("uₖ₊₁ = uₖ − α · F(uₖ)", italic=True)
doc.add_paragraph(
    "requires |G′(u*)| = |1 − α F′(u*)| < 1, i.e. 0 < α F′(u*) < 2. We "
    "estimate F′(u₀) numerically (central differences with ε = 10⁻⁴) at the "
    "mid-point of each bracket of a sign change of F, and pick α = 1/F′(u₀), "
    "which gives |G′(u*)| ≈ 0 near the root and very fast (effectively "
    "linear-becoming-superlinear in practice) contraction."
)
doc.add_paragraph(
    "A 4000-point sweep of F(u) over [0,4] reveals two sign changes, hence "
    "two intersections."
)

add_heading("Convergence — Intersection 1", 2)
doc.add_paragraph("α = −0.147653, starting u₀ = 0.884721:")
add_table(
    headers=["k", "uₖ", "F(uₖ)"],
    rows=[
        ["0", "0.884721180074", "−1.07131 × 10⁻³"],
        ["1", "0.884562998104", "−3.02963 × 10⁻⁸"],
        ["2", "0.884562993630", "−1.71418 × 10⁻¹²"],
        ["3", "0.884562993630", "8.88 × 10⁻¹⁶ (≈ 0)"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Convergence — Intersection 2", 2)
doc.add_paragraph("α = +0.199305, starting u₀ = 3.290323:")
add_table(
    headers=["k", "uₖ", "F(uₖ)"],
    rows=[
        ["0", "3.290322579823", "−6.68142 × 10⁻⁴"],
        ["1", "3.290455743493",  "2.41921 × 10⁻⁸"],
        ["2", "3.290455738672", "−1.75149 × 10⁻¹²"],
        ["3", "3.290455738672", "−8.88 × 10⁻¹⁶ (≈ 0)"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT],
)

add_heading("Intersections found", 2)
add_table(
    headers=["#", "u*", "x*", "y*"],
    rows=[
        ["1", "0.8845629936", "1.7378432", "2.8593571"],
        ["2", "3.2904557387", "5.1715470", "5.1681144"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.CENTER]*4,
)

doc.add_paragraph(
    "Plotted with red stars on the two curves in plots/p7_intersections.png."
)
add_image(os.path.join(PLOTS, "p7_intersections.png"))

# ---------- Files in submission ----------
add_heading("Files in this submission", 1)
add_table(
    headers=["File", "Contents"],
    rows=[
        ["solution.py",                "All 7 problems implemented from scratch"],
        ["results.txt",                "Full numerical log produced by the script"],
        ["REPORT.md",                  "Markdown source of this report"],
        ["REPORT.docx",                "Word version of this report"],
        ["plots/p1_bezier.png",        "Problem 1 — Bezier curve"],
        ["plots/p2_tangent.png",       "Problem 2 — tangent angle θ(t)"],
        ["plots/p4_eqspaced.png",      "Problem 4 — 8 equally-x-spaced points"],
        ["plots/p5_spline.png",        "Problem 5 — natural cubic spline"],
        ["plots/p5_compare.png",       "Problem 5 — Bezier vs cubic spline"],
        ["plots/p6_bspline.png",       "Problem 6 — interpolating cubic B-spline"],
        ["plots/p7_intersections.png", "Problem 7 — intersections"],
    ],
    col_align=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT],
)

doc.save(OUT)
print(f"Saved: {OUT}")
