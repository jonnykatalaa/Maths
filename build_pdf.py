"""Render the homework results into a single PDF for submission."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether,
)


PLOTS = "plots"
OUT = "results.pdf"

styles = getSampleStyleSheet()

H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15, spaceBefore=12,
                   spaceAfter=8, textColor=colors.HexColor("#1a1a1a"),
                   fontName="Helvetica-Bold")
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=8,
                   spaceAfter=4, textColor=colors.HexColor("#222222"),
                   fontName="Helvetica-Bold")
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10,
                      leading=13, alignment=TA_JUSTIFY, spaceAfter=6)
EQ = ParagraphStyle("Eq", parent=BODY, alignment=TA_CENTER, fontName="Helvetica-Oblique",
                    fontSize=10.5, leading=14, spaceBefore=4, spaceAfter=6,
                    textColor=colors.HexColor("#202060"))
MONO = ParagraphStyle("Mono", parent=BODY, fontName="Courier", fontSize=9.5,
                      leading=12)
CAPTION = ParagraphStyle("Cap", parent=BODY, fontSize=9, alignment=TA_CENTER,
                         textColor=colors.HexColor("#444"), spaceBefore=2,
                         spaceAfter=10)
TITLE = ParagraphStyle("Title", parent=styles["Title"], fontSize=22, leading=28,
                       alignment=TA_CENTER)
SUBTITLE = ParagraphStyle("Sub", parent=BODY, fontSize=12, alignment=TA_CENTER,
                          textColor=colors.HexColor("#444"))


def header_footer(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 8)
    canv.setFillColor(colors.HexColor("#777"))
    canv.drawString(2 * cm, 1.2 * cm,
                    "Numerical Analysis Homework 2025-2026  -  NTUA Mech. Eng.")
    canv.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canv.restoreState()


def std_table(data, col_widths=None, header=True):
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#888")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde4f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(style))
    return t


def plot(name, caption):
    img = Image(f"{PLOTS}/{name}", width=15.5 * cm, height=11.6 * cm,
                kind="proportional")
    return KeepTogether([img, Paragraph(caption, CAPTION)])


def P(text):
    return Paragraph(text, BODY)


def E(text):
    return Paragraph(text, EQ)


def H(text):
    return Paragraph(text, H1)


def Sub(text):
    return Paragraph(text, H2)


story = []

# ---------- title page ----------
story += [
    Spacer(1, 4 * cm),
    Paragraph("Numerical Analysis", TITLE),
    Paragraph("Homework 2025-2026 &mdash; Full Results", TITLE),
    Spacer(1, 1 * cm),
    Paragraph("NTUA &mdash; School of Mechanical Engineering", SUBTITLE),
    Paragraph("Course: Numerical Analysis (K. Giannakoglou / V. Asouti)", SUBTITLE),
    Spacer(1, 1.2 * cm),
    Paragraph("Student key digits: <b>K1 = 6, K2 = 6, K3 = 0</b>", SUBTITLE),
    Spacer(1, 2 * cm),
    Paragraph(
        "All algorithms implemented from scratch in <font face='Courier'>solution.py</font>. "
        "NumPy is used only for arrays / dense linear algebra; matplotlib only "
        "for plots. No black-box numerical solver is used.",
        ParagraphStyle("note", parent=BODY, alignment=TA_CENTER, fontSize=10,
                       textColor=colors.HexColor("#555")),
    ),
    Spacer(1, 0.4 * cm),
    Paragraph(
        "Reproduce: <font face='Courier'>python3 solution.py</font> &mdash; "
        "produces all plots and the numerical log.",
        ParagraphStyle("note", parent=BODY, alignment=TA_CENTER, fontSize=10,
                       textColor=colors.HexColor("#555")),
    ),
    PageBreak(),
]

# ---------- 1. Bezier curve ----------
story.append(H("1. Bezier curve (6 control points)"))
story.append(Sub("Control points"))
story.append(P("With K1 = 6, K2 = 6, K3 = 0 the six control points are:"))
story.append(std_table([
    ["i", "X<sub>i</sub>", "Y<sub>i</sub>"],
    ["0", "0.0", "0.0"],
    ["1", "3.0", "4 + K2/12 = 4.500000"],
    ["2", "4 + K1/10 = 4.600000", "10.0"],
    ["3", "5.5", "3.0"],
    ["4", "6.0", "5 + K3/8 = 5.000000"],
    ["5", "7.0", "0.0"],
], col_widths=[1.5 * cm, 6 * cm, 6 * cm]))
story.append(Spacer(1, 6))

story.append(Sub("Mathematical equations"))
story.append(P("The degree-5 Bezier curve is the standard Bernstein form:"))
story.append(E("B(t) = &Sigma;<sub>i=0..5</sub> C(5,i) t<sup>i</sup> (1&minus;t)<sup>5&minus;i</sup> P<sub>i</sub>,    t &isin; [0,1]."))
story.append(P("Substituting the control points and expanding into monomials in t we obtain "
               "the coefficients of t<sup>k</sup>:"))
story.append(std_table([
    ["k", "x(t) coefficient", "y(t) coefficient"],
    ["0",   "0.000000",    "0.000000"],
    ["1",  "15.000000",   "22.500000"],
    ["2", "&minus;14.000000",   "10.000000"],
    ["3",   "7.000000", "&minus;135.000000"],
    ["4",  "&minus;2.000000",  "175.000000"],
    ["5",   "1.000000",  "&minus;72.500000"],
], col_widths=[1.5 * cm, 5 * cm, 5 * cm]))
story.append(Spacer(1, 8))
story.append(E("x(t) = 15 t &minus; 14 t<sup>2</sup> + 7 t<sup>3</sup> &minus; 2 t<sup>4</sup> + t<sup>5</sup>"))
story.append(E("y(t) = 22.5 t + 10 t<sup>2</sup> &minus; 135 t<sup>3</sup> + 175 t<sup>4</sup> &minus; 72.5 t<sup>5</sup>"))
story.append(P("Sanity check: x(0) = y(0) = 0; x(1) = 15 &minus; 14 + 7 &minus; 2 + 1 = 7; "
               "y(1) = 22.5 + 10 &minus; 135 + 175 &minus; 72.5 = 0 &mdash; both endpoints "
               "reproduce the first/last control points."))
story.append(P("The curve was sampled at 100 equally-spaced t-values (&Delta;t = 1/99) and is "
               "plotted with the control polygon below."))
story.append(plot("p1_bezier.png", "Figure 1 - Bezier curve and control polygon."))
story.append(PageBreak())

# ---------- 2. Tangent angle ----------
story.append(H("2. Tangent angle along the curve"))
story.append(P("For a parametric curve, dy/dx = (dy/dt)/(dx/dt). Using the standard derivative "
               "formula for a degree-n Bezier curve,"))
story.append(E("B&prime;(t) = n &Sigma;<sub>i=0..n&minus;1</sub> C(n&minus;1,i) t<sup>i</sup> "
               "(1&minus;t)<sup>n&minus;1&minus;i</sup> (P<sub>i+1</sub> &minus; P<sub>i</sub>),"))
story.append(P("so B&prime;(t) is itself a degree-4 Bezier curve with control points "
               "Q<sub>i</sub> = 5 (P<sub>i+1</sub> &minus; P<sub>i</sub>):"))
story.append(std_table([
    ["i", "Qx<sub>i</sub>", "Qy<sub>i</sub>"],
    ["0", "15.0",  "22.5"],
    ["1",  "8.0",  "27.5"],
    ["2",  "4.5", "&minus;35.0"],
    ["3",  "2.5",  "10.0"],
    ["4",  "5.0", "&minus;25.0"],
], col_widths=[1.5 * cm, 3.5 * cm, 3.5 * cm]))
story.append(Spacer(1, 6))
story.append(P("The tangent angle (in degrees) is:"))
story.append(E("&theta;(t) = (180/&pi;) &middot; atan2( y&prime;(t), x&prime;(t) )."))
story.append(P("Representative values: &theta;(0) = 56.310&deg;, &theta;(0.25) = 51.821&deg;, "
               "&theta;(0.5) = &minus;35.078&deg;, &theta;(0.75) = &minus;67.486&deg;, "
               "&theta;(1) = &minus;78.690&deg;. The angle is monotonically decreasing on "
               "t &isin; [&asymp;0.1, 1], consistent with the visual shape of the curve "
               "(rising, turning over the maximum, then dropping)."))
story.append(plot("p2_tangent.png", "Figure 2 - Tangent angle &theta;(t) along the Bezier curve."))
story.append(PageBreak())

# ---------- 3. Volume of revolution ----------
story.append(H("3. Volume of revolution (Gauss-Legendre quadrature)"))
story.append(P("The body of revolution about the x-axis has"))
story.append(E("V = &pi; &int;<sub>x(0)</sub><sup>x(1)</sup> y(x)<sup>2</sup> dx "
               "= &pi; &int;<sub>0</sub><sup>1</sup> y(t)<sup>2</sup> x&prime;(t) dt."))
story.append(P("The integrand g(t) = y(t)<sup>2</sup> &middot; x&prime;(t) is the product of "
               "(deg 5)<sup>2</sup> = deg 10 and deg 4, hence a polynomial of "
               "<b>degree 14</b>. A Gauss-Legendre rule with m nodes is exact on polynomials "
               "of degree 2m&minus;1, so an exact result needs m &ge; 8. Therefore the values "
               "at m = 2,3,4,5 are <i>approximate</i>."))
story.append(P("The exact analytic value, obtained by polynomial expansion plus term-by-term "
               "integration of g(t) (every monomial t<sup>k</sup> contributes 1/(k+1)), is"))
story.append(E("V* = 344.572 848 084 958."))
story.append(Sub("Results"))
story.append(std_table([
    ["m", "V(m)", "|V(m) &minus; V*|"],
    ["2", "351.117330512449", "6.544482 &times; 10<sup>0</sup>"],
    ["3", "321.380133749620", "2.319271 &times; 10<sup>1</sup>"],
    ["4", "347.119878378522", "2.547030 &times; 10<sup>0</sup>"],
    ["5", "344.545194110158", "2.765397 &times; 10<sup>&minus;2</sup>"],
], col_widths=[1.2 * cm, 5 * cm, 5 * cm]))
story.append(Spacer(1, 8))
story.append(Sub("Comments"))
story.append(P("The Gauss rule converges very fast despite the integrand being 14-th degree: "
               "the error drops from 6.5 (m = 2) to ~2.8 &times; 10<sup>&minus;2</sup> (m = 5), "
               "i.e. <b>two and a half orders of magnitude</b> in three additional nodes. "
               "This is the classical geometric / super-algebraic convergence of "
               "Gauss-Legendre on smooth integrands. The non-monotone jump at m = 3 "
               "(worse than m = 2) is normal: the error of a Gauss rule depends on the "
               "(2m)-th derivative of the integrand and need not decrease monotonically."))
story.append(PageBreak())

# ---------- 4. Newton-Raphson ----------
story.append(H("4. Eight equally-x-spaced points (Newton-Raphson)"))
story.append(P("The Bezier curve has x(0) = 0, x(1) = 7, and "
               "x&prime;(t) &ge; min(15, 8, 4.5, 2.5, 5) = 2.5 &gt; 0, so x(t) is strictly "
               "increasing and the inverse problem x(t) = x* has a unique solution for every "
               "x* &isin; [0,7]. We pick"))
story.append(E("x*<sub>i</sub> = 7 i / 7 = i,    i = 0, 1, ..., 7,"))
story.append(P("and solve f(t) = x(t) &minus; x*<sub>i</sub> = 0 by Newton-Raphson:"))
story.append(E("t<sub>k+1</sub> = t<sub>k</sub> &minus; "
               "( x(t<sub>k</sub>) &minus; x*<sub>i</sub> ) / x&prime;(t<sub>k</sub>),"))
story.append(P("with initial guess t<sub>0</sub> = x*<sub>i</sub> / 7. Tolerance: |f| &lt; 10<sup>&minus;12</sup>."))

story.append(Sub("Results (8 points)"))
story.append(std_table([
    ["i", "x*<sub>i</sub>", "t<sub>i</sub>", "y<sub>i</sub>", "iters"],
    ["0", "0.000000", "0.00000000", "0.000000", "1"],
    ["1", "1.000000", "0.07123777", "1.609167", "5"],
    ["2", "2.000000", "0.15377571", "3.297141", "5"],
    ["3", "3.000000", "0.25244560", "4.781832", "6"],
    ["4", "4.000000", "0.37594681", "5.650274", "6"],
    ["5", "5.000000", "0.54083183", "5.355261", "5"],
    ["6", "6.000000", "0.76681091", "3.547728", "4"],
    ["7", "7.000000", "1.00000000", "0.000000", "1"],
], col_widths=[1.0 * cm, 2.6 * cm, 3.0 * cm, 3.0 * cm, 1.5 * cm]))
story.append(Spacer(1, 8))

story.append(Sub("Detailed convergence for x* = 2"))
story.append(std_table([
    ["k", "t<sub>k</sub>", "x(t<sub>k</sub>)", "f = x(t<sub>k</sub>) &minus; x*"],
    ["0", "0.2857142857", "3.29469864",  "1.29470 &times; 10<sup>0</sup>"],
    ["1", "0.1344823991", "1.78045387", "&minus;2.19546 &times; 10<sup>&minus;1</sup>"],
    ["2", "0.1534145566", "1.99596646", "&minus;4.03354 &times; 10<sup>&minus;3</sup>"],
    ["3", "0.1537755795", "1.99999856", "&minus;1.43664 &times; 10<sup>&minus;6</sup>"],
    ["4", "0.1537757082", "2.00000000", "&minus;1.82743 &times; 10<sup>&minus;13</sup>"],
], col_widths=[1.0 * cm, 3.4 * cm, 3.4 * cm, 5.5 * cm]))
story.append(Spacer(1, 8))

story.append(Sub("Detailed convergence for x* = 5"))
story.append(std_table([
    ["k", "t<sub>k</sub>", "x(t<sub>k</sub>)", "f = x(t<sub>k</sub>) &minus; x*"],
    ["0", "0.7142857143", "5.78776700",  "7.87767 &times; 10<sup>&minus;1</sup>"],
    ["1", "0.5221649859", "4.90202350", "&minus;9.79765 &times; 10<sup>&minus;2</sup>"],
    ["2", "0.5405198746", "4.99838940", "&minus;1.61060 &times; 10<sup>&minus;3</sup>"],
    ["3", "0.5408317483", "4.99999956", "&minus;4.44899 &times; 10<sup>&minus;7</sup>"],
    ["4", "0.5408318345", "5.00000000", "&minus;3.28626 &times; 10<sup>&minus;14</sup>"],
], col_widths=[1.0 * cm, 3.4 * cm, 3.4 * cm, 5.5 * cm]))
story.append(Spacer(1, 6))
story.append(P("In both cases we observe the classic <b>quadratic convergence</b> of Newton's "
               "method: the error roughly squares each step (after the first iteration)."))
story.append(plot("p4_eqspaced.png", "Figure 3 - Eight equally-x-spaced points on the Bezier curve."))
story.append(PageBreak())

# ---------- 5. Cubic spline ----------
story.append(H("5. Natural cubic spline through these 8 points"))
story.append(P("The 8 abscissae x<sub>i</sub> = 0, 1, ..., 7 are uniform, h<sub>i</sub> = 1. "
               "With y<sub>i</sub> = (0, 1.6092, 3.2971, 4.7818, 5.6503, 5.3553, 3.5477, 0) we "
               "build a piecewise-cubic S(x) of class C<sup>2</sup>. Letting "
               "M<sub>i</sub> = S&Prime;(x<sub>i</sub>), the natural-spline conditions "
               "M<sub>0</sub> = M<sub>7</sub> = 0 together with the continuity-of-second-derivative "
               "system"))
story.append(E("h<sub>i&minus;1</sub> M<sub>i&minus;1</sub> + 2 ( h<sub>i&minus;1</sub> + h<sub>i</sub> ) M<sub>i</sub> "
               "+ h<sub>i</sub> M<sub>i+1</sub> = 6 [ (y<sub>i+1</sub> &minus; y<sub>i</sub>) / h<sub>i</sub> "
               "&minus; (y<sub>i</sub> &minus; y<sub>i&minus;1</sub>) / h<sub>i&minus;1</sub> ]"))
story.append(P("yield a tridiagonal linear system. Solving it gives:"))
story.append(std_table([
    ["i", "M<sub>i</sub>"],
    ["0", "0.00000000"],
    ["1", "0.17022523"],
    ["2", "&minus;0.20805769"],
    ["3", "&minus;0.55768944"],
    ["4", "&minus;1.25868369"],
    ["5", "&minus;1.38830539"],
    ["6", "&minus;2.26321500"],
    ["7", "0.00000000"],
], col_widths=[1.5 * cm, 4 * cm]))
story.append(Spacer(1, 8))
story.append(P("On each interval [x<sub>i</sub>, x<sub>i+1</sub>] the spline is:"))
story.append(E("S<sub>i</sub>(x) = [ M<sub>i</sub> (x<sub>i+1</sub>&minus;x)<sup>3</sup> "
               "+ M<sub>i+1</sub> (x&minus;x<sub>i</sub>)<sup>3</sup> ] / (6 h<sub>i</sub>)"))
story.append(E("+ ( y<sub>i</sub>/h<sub>i</sub> &minus; M<sub>i</sub> h<sub>i</sub>/6 ) (x<sub>i+1</sub>&minus;x) "
               "+ ( y<sub>i+1</sub>/h<sub>i</sub> &minus; M<sub>i+1</sub> h<sub>i</sub>/6 ) (x&minus;x<sub>i</sub>)."))
story.append(P("Plotted at 400 sample points; superimposed against the Bezier curve in the second "
               "figure. The two curves are <b>visually indistinguishable</b> at the scale of the plot. "
               "A direct numerical comparison gives a maximum point-wise deviation of approximately "
               "max<sub>x</sub> |y<sub>s</sub>(x) &minus; y<sub>B</sub>(x)| &asymp; 0.18 (occurring "
               "near the maximum where the curvature is largest). The Bezier curve is a single global "
               "degree-5 polynomial whereas the spline is a piecewise cubic forced through 8 sampled "
               "points; the small discrepancy is the natural error of the C<sup>2</sup>-cubic "
               "interpolant on a smooth curve sampled with &Delta;x = 1."))
story.append(plot("p5_spline.png", "Figure 4 - Natural cubic spline through the 8 points."))
story.append(plot("p5_compare.png", "Figure 5 - Bezier curve vs natural cubic spline."))
story.append(PageBreak())

# ---------- 6. Cubic B-spline ----------
story.append(H("6. Cubic B-spline interpolation of 5 data points"))
story.append(Sub("Data"))
story.append(std_table([
    ["i", "x<sub>i</sub>", "y<sub>i</sub>"],
    ["0", "0.5", "6.0"],
    ["1", "2.0", "2 + K2/12 = 2.500000"],
    ["2", "4 + K1/10 = 4.600000", "1.0"],
    ["3", "5.0", "4.0"],
    ["4", "6.0", "8 + K3/8 = 8.000000"],
], col_widths=[1.5 * cm, 5.5 * cm, 5.5 * cm]))
story.append(Spacer(1, 8))

story.append(Sub("Setup"))
story.append(P("Using uniform knot spacing and parameter u<sub>j</sub> = j at data point j, each "
               "segment S<sub>k</sub>(t), t &isin; [0,1], k = 0..3, is"))
story.append(E("S<sub>k</sub>(t) = (1/6) [ (1&minus;t)<sup>3</sup> P<sub>k</sub> "
               "+ (3 t<sup>3</sup> &minus; 6 t<sup>2</sup> + 4) P<sub>k+1</sub>"))
story.append(E("+ (&minus;3 t<sup>3</sup> + 3 t<sup>2</sup> + 3 t + 1) P<sub>k+2</sub> "
               "+ t<sup>3</sup> P<sub>k+3</sub> ]."))
story.append(P("Imposing S<sub>k</sub>(0) = (x<sub>k</sub>, y<sub>k</sub>) for k = 0..3 and "
               "S<sub>3</sub>(1) = (x<sub>4</sub>, y<sub>4</sub>) gives 5 equations in the 7 "
               "unknown control points P<sub>0</sub>, ..., P<sub>6</sub>. Two more come from the "
               "natural boundary conditions S&Prime;(0) = S&Prime;(end) = 0, which in uniform "
               "B-spline form read"))
story.append(E("P<sub>0</sub> &minus; 2 P<sub>1</sub> + P<sub>2</sub> = 0,    "
               "P<sub>3</sub> &minus; 2 P<sub>4</sub> + P<sub>5</sub> = 0,"))
story.append(P("and a 7&times;7 system is solved twice (once for x, once for y). The resulting "
               "control points are:"))
story.append(std_table([
    ["i", "P<sub>i,x</sub>", "P<sub>i,y</sub>"],
    ["0", "&minus;0.537500",  "9.732143"],
    ["1",  "0.500000",  "6.000000"],
    ["2",  "1.537500",  "2.267857"],
    ["3",  "5.350000", "&minus;0.071429"],
    ["4",  "4.662500",  "4.017857"],
    ["5",  "6.000000",  "8.000000"],
    ["6",  "7.337500", "11.982143"],
], col_widths=[1.5 * cm, 4 * cm, 4 * cm]))
story.append(Spacer(1, 10))

story.append(Sub("Explicit polynomial of every segment"))
story.append(P("Substituting and collecting in monomials, every segment has the form "
               "x(t) = &alpha;<sup>x</sup><sub>0</sub> + &alpha;<sup>x</sup><sub>1</sub> t "
               "+ &alpha;<sup>x</sup><sub>2</sub> t<sup>2</sup> + &alpha;<sup>x</sup><sub>3</sub> t<sup>3</sup> "
               "(and analogously for y):"))

seg_table = [
    ["seg", "coord", "t<sup>0</sup>", "t<sup>1</sup>", "t<sup>2</sup>", "t<sup>3</sup>"],
    ["1/4 (Q<sub>0</sub>&rarr;Q<sub>1</sub>)", "x", "0.500000",  "1.037500",  "0.000000",  "0.462500"],
    ["1/4 (Q<sub>0</sub>&rarr;Q<sub>1</sub>)", "y", "6.000000", "&minus;3.732143", "0.000000", "0.232143"],
    ["2/4 (Q<sub>1</sub>&rarr;Q<sub>2</sub>)", "x", "2.000000",  "2.425000",  "1.387500", "&minus;1.212500"],
    ["2/4 (Q<sub>1</sub>&rarr;Q<sub>2</sub>)", "y", "2.500000", "&minus;3.035714", "0.696429",  "0.839286"],
    ["3/4 (Q<sub>2</sub>&rarr;Q<sub>3</sub>)", "x", "4.600000",  "1.562500", "&minus;2.250000", "1.087500"],
    ["3/4 (Q<sub>2</sub>&rarr;Q<sub>3</sub>)", "y", "1.000000",  "0.875000",  "3.214286", "&minus;1.089286"],
    ["4/4 (Q<sub>3</sub>&rarr;Q<sub>4</sub>)", "x", "5.000000",  "0.325000",  "1.012500", "&minus;0.337500"],
    ["4/4 (Q<sub>3</sub>&rarr;Q<sub>4</sub>)", "y", "4.000000",  "4.035714", "&minus;0.053571", "0.017857"],
]
story.append(std_table(seg_table, col_widths=[3.4 * cm, 1.2 * cm, 2.4 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]))
story.append(Spacer(1, 6))
story.append(P("(One easily checks S<sub>k</sub>(0) = Q<sub>k</sub> and S<sub>3</sub>(1) = Q<sub>4</sub>.)"))
story.append(plot("p6_bspline.png", "Figure 6 - Interpolating cubic B-spline through 5 points."))
story.append(PageBreak())

# ---------- 7. Intersections ----------
story.append(H("7. Intersections of the two curves (fixed-point iteration)"))
story.append(P("The cubic spline of section 5 is y = y<sub>s</sub>(x) for x &isin; [0,7]; the cubic "
               "B-spline of section 6 is the parametric curve (x<sub>b</sub>(u), y<sub>b</sub>(u)) "
               "for u &isin; [0,4]. An intersection satisfies"))
story.append(E("F(u) := y<sub>b</sub>(u) &minus; y<sub>s</sub>( x<sub>b</sub>(u) ) = 0."))
story.append(P("This is rewritten as the fixed-point problem u = G(u) := u &minus; &alpha; F(u) "
               "with constant relaxation &alpha;. Convergence of the basic fixed-point iteration"))
story.append(E("u<sub>k+1</sub> = u<sub>k</sub> &minus; &alpha; F(u<sub>k</sub>)"))
story.append(P("requires |G&prime;(u*)| = |1 &minus; &alpha; F&prime;(u*)| &lt; 1, i.e. "
               "0 &lt; &alpha; F&prime;(u*) &lt; 2. We estimate F&prime;(u<sub>0</sub>) numerically "
               "(central differences with &epsilon; = 10<sup>&minus;4</sup>) at the mid-point of each "
               "bracket of a sign change of F, and pick &alpha; = 1 / F&prime;(u<sub>0</sub>), which "
               "gives |G&prime;(u*)| &asymp; 0 near the root and very fast (effectively "
               "linear-becoming-superlinear in practice) contraction."))
story.append(P("A 4000-point sweep of F(u) over [0,4] reveals <b>two</b> sign changes, hence two "
               "intersections."))

story.append(Sub("Convergence - Intersection 1"))
story.append(P("&alpha; = &minus;0.147653, starting u<sub>0</sub> = 0.884721:"))
story.append(std_table([
    ["k", "u<sub>k</sub>", "F(u<sub>k</sub>)"],
    ["0", "0.884721180074", "&minus;1.07131 &times; 10<sup>&minus;3</sup>"],
    ["1", "0.884562998104", "&minus;3.02963 &times; 10<sup>&minus;8</sup>"],
    ["2", "0.884562993630", "&minus;1.71418 &times; 10<sup>&minus;12</sup>"],
    ["3", "0.884562993630", "8.88 &times; 10<sup>&minus;16</sup> (&asymp; 0)"],
], col_widths=[1.0 * cm, 4.5 * cm, 6 * cm]))
story.append(Spacer(1, 6))

story.append(Sub("Convergence - Intersection 2"))
story.append(P("&alpha; = +0.199305, starting u<sub>0</sub> = 3.290323:"))
story.append(std_table([
    ["k", "u<sub>k</sub>", "F(u<sub>k</sub>)"],
    ["0", "3.290322579823", "&minus;6.68142 &times; 10<sup>&minus;4</sup>"],
    ["1", "3.290455743493",  "2.41921 &times; 10<sup>&minus;8</sup>"],
    ["2", "3.290455738672", "&minus;1.75149 &times; 10<sup>&minus;12</sup>"],
    ["3", "3.290455738672", "&minus;8.88 &times; 10<sup>&minus;16</sup> (&asymp; 0)"],
], col_widths=[1.0 * cm, 4.5 * cm, 6 * cm]))
story.append(Spacer(1, 8))

story.append(Sub("Intersections found"))
story.append(std_table([
    ["#", "u*", "x*", "y*"],
    ["1", "0.8845629936", "1.7378432", "2.8593571"],
    ["2", "3.2904557387", "5.1715470", "5.1681144"],
], col_widths=[1.0 * cm, 4 * cm, 4 * cm, 4 * cm]))
story.append(Spacer(1, 8))
story.append(plot("p7_intersections.png",
                  "Figure 7 - Intersections of the cubic spline and the B-spline (red stars)."))
story.append(PageBreak())

# ---------- appendix: file index ----------
story.append(H("Files in this submission"))
story.append(std_table([
    ["File", "Contents"],
    ["solution.py",                   "All 7 problems implemented from scratch"],
    ["results.txt",                   "Full numerical log produced by the script"],
    ["REPORT.md",                     "Markdown source of this report"],
    ["results.pdf",                   "This document"],
    ["plots/p1_bezier.png",           "Problem 1 - Bezier curve"],
    ["plots/p2_tangent.png",          "Problem 2 - tangent angle &theta;(t)"],
    ["plots/p4_eqspaced.png",         "Problem 4 - 8 equally-x-spaced points"],
    ["plots/p5_spline.png",           "Problem 5 - natural cubic spline"],
    ["plots/p5_compare.png",          "Problem 5 - Bezier vs cubic spline"],
    ["plots/p6_bspline.png",          "Problem 6 - interpolating cubic B-spline"],
    ["plots/p7_intersections.png",    "Problem 7 - intersections"],
], col_widths=[5.5 * cm, 10 * cm]))


# ---------- build ----------
doc = BaseDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Numerical Analysis Homework 2025-2026",
    author="NTUA Mech. Eng. - Numerical Analysis",
)
frame = Frame(doc.leftMargin, doc.bottomMargin,
              doc.width, doc.height, id="normal")
doc.addPageTemplates(PageTemplate(id="all", frames=frame, onPage=header_footer))
doc.build(story)

print(f"Wrote {OUT}")
