## Lê Minh Đăng

Data & Business Analyst · Ho Chi Minh City · open to remote work

**[Portfolio](https://conchocon154.github.io/)** · [dangleminh6677@gmail.com](mailto:dangleminh6677@gmail.com) · [Kaggle](https://www.kaggle.com/minhngle)

---

Computer Science graduate from Ton Duc Thang University, 2025. I work in SQL and
Python, mostly on the part of data work that decides whether a number can be
trusted at all: how cost gets assigned, what a rate is being measured against,
whether a gap survives a test.

Most of what I know came from building an inventory and accounting system for a
hardware shop and then doing the analysis on top of it. FIFO costing, two-way
receivables, margin reporting. It taught me that a report is worth exactly as
much as the accounting decisions underneath it, and not a bit more.

In each project below there is a baseline the method had to beat. Three of them
ended in a result I did not want, and those are written up as carefully as the
rest.

### Projects

**[retail-analytics-sql](https://github.com/conchocon154/retail-analytics-sql)**
Eight analytical queries over a simulated hardware shop: 300 SKUs, 25 months,
8,500 invoices. Discounts to credit customers had drifted from 3.1% to 6.8%
while revenue held steady, which is exactly why nobody had noticed. 20 tests
check the numbers, including one guarding a reorder-point bug that used to
inflate demand thirtyfold.

**[vn-product-matcher](https://github.com/conchocon154/vn-product-matcher)**
Matches free-text Vietnamese product names onto 1,827 catalogue SKUs. The
fine-tuned encoder reaches 96.9% Recall@1 on SKUs held out of training, 1.9
points over a TF-IDF baseline (McNemar p = 1.2e-3). The reranker I designed to
fix number handling turned out to do nothing at all, p = 1.00, and it is still
in the repository with the measurement that says so.

**[ev-purchase-analysis](https://github.com/conchocon154/ev-purchase-analysis)**
668,665 records from a live Kaggle competition, written up in English and
Vietnamese. A cross-tab showed 69.3% against 2.5% and looked like a textbook
interaction between subsidy and environmental concern. The likelihood ratio test
put it at p = 0.62; the effect was not there, and the recommendation changed.
Shipped logistic regression at 0.938 AUC instead of a 0.941 GBM, because
coefficients can be explained to the people who act on them.

**[caption-decoding-study](https://github.com/conchocon154/caption-decoding-study)**
A controlled comparison of beam widths for a CNN-LSTM captioner on MS-COCO.
BLEU-4 peaks at beam 5 and falls again at 10 (p = 0.017), while caption variety
declines the whole way. Beam search also ran five times faster on CPU than on
Apple MPS, which I did not expect and had to go and understand.

**[object-detection](https://github.com/conchocon154/object-detection)**
Real-time detection from webcam, video or image. YOLO and OpenCV, modular
pipeline, configurable thresholds, CI.

**[Chess_Ai](https://github.com/conchocon154/Chess_Ai)**
Native macOS chess in Swift and SwiftUI. Full international rules and three
levels of opponent, from random moves to minimax with heuristics.

**[MidDeep_Learning](https://github.com/conchocon154/MidDeep_Learning)**
The 2023 coursework captioner that the decoding study above is built on.

**[conchocon154.github.io](https://github.com/conchocon154/conchocon154.github.io)**
The portfolio itself. Hand-written HTML and CSS; every chart on it is generated
from the result files of the four projects above rather than drawn by hand.

### Experience

| | |
|---|---|
| 04/2023 – 09/2025 | Python Instructor, [ICANTECH](https://www.icantech.vn/) — online classes of 5–10 secondary and high-school students |
| 07/2022 – 11/2022 | SEO, [BTSE](https://www.btse.com/en/home) |
| 03/2021 – 06/2021 | Developer, [Havi Technology](https://havi.com.au/) |

### Education

**B.Sc. Computer Science**, Ton Duc Thang University, 2020 – 2025.
One-month exchange programme at Chinese Culture University, Taipei, July 2026,
taught entirely in English.

Vietnamese (native), English (PET B1), Chinese (conversational).
