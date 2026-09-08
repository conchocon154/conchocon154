<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.png">
  <img alt="Lê Minh Đăng — Data &amp; Business Analyst, Ho Chi Minh City, open to remote" src="assets/banner-light.png">
</picture>

**[Portfolio](https://conchocon154.github.io/)** · [dangleminh6677@gmail.com](mailto:dangleminh6677@gmail.com) · [Kaggle](https://www.kaggle.com/minhngle)  

Computer Science graduate from Ton Duc Thang University, 2025. Most of what I know
came from building an inventory and accounting system for a hardware shop and then
doing the analysis on top of it. FIFO costing, two-way receivables, margin reporting.
It taught me that a report is worth exactly as much as the accounting decisions
underneath it, and not a bit more.

In each project below there is a baseline the method had to beat. Three of them ended
in a result I did not want, and those are written up as carefully as the rest.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/charts-dark.gif">
  <img alt="Four charts drawing themselves: discount drift against gross margin over 25 months; Recall@1 by retriever; buyers reached against share of the list contacted; BLEU-4 across beam widths" src="assets/charts-light.gif">
</picture>

<sub>Every series above is read out of the result files in the four repositories — `tools/render_charts.py` rebuilds the animation from them.</sub>

**[retail-analytics-sql](https://github.com/conchocon154/retail-analytics-sql)** · SQL · SQLite · pandas  
Eight analytical queries over a simulated hardware shop: 300 SKUs, 25 months, 8,500
invoices. 20 tests check the numbers, one of them guarding a reorder-point bug that
used to inflate average demand thirtyfold.

**[vn-product-matcher](https://github.com/conchocon154/vn-product-matcher)** · PyTorch · sentence-transformers · FastAPI  
Matches free-text Vietnamese product names onto 1,827 catalogue SKUs. The reranker I
designed to fix number handling turned out to do nothing at all, p = 1.00, and it is
still in the repository with the measurement that says so.

**[ev-purchase-analysis](https://github.com/conchocon154/ev-purchase-analysis)** · pandas · scikit-learn · statsmodels  
A cross-tab showed 69.3% against 2.5% and looked like a textbook interaction. The
likelihood ratio test put it at p = 0.62, so the effect was not there and the
recommendation changed. Shipped logistic regression at 0.938 AUC over a 0.941 GBM,
because coefficients can be explained to the people who act on them.

**[caption-decoding-study](https://github.com/conchocon154/caption-decoding-study)** · PyTorch · ResNet-50 · LSTM  
A controlled comparison of beam widths on MS-COCO. Beam search also ran five times
faster on CPU than on Apple MPS, which I did not expect and had to go and understand.

### Also here

- **[conchocon154.github.io](https://github.com/conchocon154/conchocon154.github.io)** — the portfolio. Hand-written HTML and CSS; every chart on it is generated from the result files of the four projects above.
- **[object-detection](https://github.com/conchocon154/object-detection)** — real-time detection from webcam, video or image. YOLO, OpenCV, CI.
- **[Chess_Ai](https://github.com/conchocon154/Chess_Ai)** — macOS chess in Swift and SwiftUI, three levels up to minimax with heuristics.
- **[MidDeep_Learning](https://github.com/conchocon154/MidDeep_Learning)** — the 2023 coursework captioner the decoding study is built on.

### Experience

| | |
|---|---|
| 04/2023 – 09/2025 | Python Instructor, [ICANTECH](https://www.icantech.vn/) — online classes of 5–10 secondary and high-school students |
| 07/2022 – 11/2022 | SEO, [BTSE](https://www.btse.com/en/home) |
| 03/2021 – 06/2021 | Developer, [Havi Technology](https://havi.com.au/) |

### Education

**B.Sc. Computer Science**, Ton Duc Thang University, 2020 – 2025.  
One-month exchange programme at Chinese Culture University, Taipei, July 2026, taught
entirely in English.

Vietnamese (native), English (PET B1), Chinese (conversational).
