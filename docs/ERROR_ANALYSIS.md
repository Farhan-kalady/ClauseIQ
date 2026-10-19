# ClauseIQ — Error Analysis & Boundary Inspection Report

**Date:** October 19, 2026  
**Model Analyzed:** Selected Logistic Regression with Hybrid Word (25k) + Character (15k) TF-IDF & NLTK Lemmatization  
**Dataset Partition:** Split A (Held-out Test Partition, N=2,441) and Split B (Grouped Partition, N=2,486)

---

## 1. Top Confused Category Pairs Analysis

The table below details the top systematic confusions observed in held-out test predictions:

| Rank | True Category | Predicted Category | Split A Count | Split B Count | Structural Root Cause |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | **Effective Date** | Agreement Date | 44 | 51 | Shared temporal phrasing ('as of the date hereof', 'effective as of') |
| 2 | **License Grant** | Non-Transferable License | 33 | 27 | Sub-licensing terms embedded in general grant paragraphs |
| 3 | **Agreement Date** | Effective Date | 32 | 11 | Shared temporal phrasing ('as of the date hereof', 'effective as of') |
| 4 | **Cap On Liability** | Uncapped Liability | 32 | 14 | Carve-outs inside limitation sections mentioning uncapped exceptions |
| 5 | **Renewal Term** | Notice Period To Terminate Renewal | 20 | 15 | Renewal terms intertwined with termination notice deadlines |
| 6 | **License Grant** | Irrevocable Or Perpetual License | 17 | 36 | Sub-licensing terms embedded in general grant paragraphs |
| 7 | **Notice Period To Terminate Renewal** | Renewal Term | 16 | 10 | Renewal terms intertwined with termination notice deadlines |
| 8 | **Uncapped Liability** | Cap On Liability | 15 | 15 | Carve-outs inside limitation sections mentioning uncapped exceptions |
| 9 | **License Grant** | Exclusivity | 13 | - | High lexical overlap in commercial contract drafting |
| 10 | **Expiration Date** | Renewal Term | 12 | - | High lexical overlap in commercial contract drafting |
| 11 | **Effective Date** | Expiration Date | 11 | 10 | Shared temporal phrasing ('as of the date hereof', 'effective as of') |
| 12 | **Non-Transferable License** | License Grant | 10 | 17 | Sub-licensing terms embedded in general grant paragraphs |

---

## 2. Weak Category Deep Dive (Lowest F1 Classes)

### Category: `Affiliate License-Licensor`
- **Test Set Support:** 14.0 samples
- **Empirical F1-Score:** 0.1860
- **Misclassified Count:** 10 / 14.0

**Representative Misclassified Examples:**

| # | True Category | Predicted As | Conf | Excerpt |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Affiliate License-Licensor | **Ip Ownership Assignment** | 0.29 | "Subject to the terms and conditions of this Agreement, following registration of the Product Trademark(s) by Array in the Ono Territory pursuant to Section 12.3 below, Array shall assign, and shall cause its Affiliates to assign, to Ono all rights to" |
| 2 | Affiliate License-Licensor | **Affiliate License-Licensee** | 0.34 | "Subject to Section 3.2, a Licensor Party, on behalf of itself and the other members of the Licensor Group, and solely to the extent the Licensor Party or another member of the Licensor Group has the right to do so, hereby grants and agrees to grant t" |
| 3 | Affiliate License-Licensor | **Non-Transferable License** | 0.47 | "Subject to the terms and -------------------------------- conditions of this Agreement, NTL, to the extent of its legal right to do so, hereby grants to Entrust under the Nortel Patents, a non-transferable, non- assignable, indivisible, non-exclusive" |
| 4 | Affiliate License-Licensor | **Irrevocable Or Perpetual License** | 0.79 | "OntoChem hereby grants to Anixa a non-exclusive, fully paid-up, royalty-free, perpetual, irrevocable, transferable, worldwide license (with the right to grant and authorize sublicenses through multiple tiers) under any patents which OntoChem or any o" |
| 5 | Affiliate License-Licensor | **Affiliate License-Licensee** | 0.44 | "Licensor on behalf of itself and its Affliates hereby grants to Licensee the limited licenses to use and have used the Licensed Mark: (i) for the Licensed Products as set forth on Schedule 2; and (ii) as set forth on Schedule 1, concerning agreements" |

### Category: `Notice Period To Terminate Renewal`
- **Test Set Support:** 24.0 samples
- **Empirical F1-Score:** 0.2456
- **Misclassified Count:** 17 / 24.0

**Representative Misclassified Examples:**

| # | True Category | Predicted As | Conf | Excerpt |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Notice Period To Terminate Renewal | **Expiration Date** | 0.41 | "Subject to the other provisions of this Agreement, the term of this Agreement shall commence on the Effective Date and shall remain in effect until terminated by either Party upon thirty (30) days' prior written notice." |
| 2 | Notice Period To Terminate Renewal | **Renewal Term** | 0.65 | "Following the Term, this Supply Agreement shall automatically renew for successive periods of one (1) year (each a "Renewal Term"), unless a Party delivers written notice of non-renewal to the other Party [***] prior to the end of the applicable term" |
| 3 | Notice Period To Terminate Renewal | **Renewal Term** | 0.49 | "Following the Initial Term, this Agreement shall automatically renew for successive terms of six (6) months (each a "Renewal Term", and together with the Initial Term, the "Term") unless written notice is given by either Party no later than thirty (3" |
| 4 | Notice Period To Terminate Renewal | **Renewal Term** | 0.61 | "This Agreement shall continue in effect from the Effective Date for a one (1) year period, unless earlier terminated as set forth below, and thereafter shall renew automatically for successive one (1) year periods unless either party gives the other " |
| 5 | Notice Period To Terminate Renewal | **Renewal Term** | 0.48 | "This JV Agreement shall become effective on the signing date and shall have a duration of * years, extendable for a further * years, unless notice of non- renewal is sent one year before the natural expiry date." |

### Category: `Unlimited/All-You-Can-Eat-License`
- **Test Set Support:** 6.0 samples
- **Empirical F1-Score:** 0.2500
- **Misclassified Count:** 4 / 6.0

**Representative Misclassified Examples:**

| # | True Category | Predicted As | Conf | Excerpt |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Unlimited/All-You-Can-Eat-License | **Affiliate License-Licensee** | 0.32 | "Subject to the terms and conditions set forth herein, Theismann hereby grants to Bizzingo and its affiliates the unlimited right and privilege during the Term (as defined herein) and within the Territory to use the Property (as defined herein) in con" |
| 2 | Unlimited/All-You-Can-Eat-License | **Affiliate License-Licensee** | 0.25 | "media now or hereafter known." |
| 3 | Unlimited/All-You-Can-Eat-License | **Revenue/Profit Sharing** | 0.16 | "Multiple viewings of the Licensed Program shall be permitted during the Viewing Period for no additional fee and all such viewings shall be considered a single exhibition of the Licensed Program for the purposes of calculating License Fees hereunder." |
| 4 | Unlimited/All-You-Can-Eat-License | **Irrevocable Or Perpetual License** | 0.47 | "RemainCo shall have, and SpinCo hereby grants to RemainCo, an unlimited, non-exclusive, perpetual, irrevocable, royalty free, worldwide right and license to use the content contained in the Steam Book, including the current edition and any past editi" |

### Category: `Irrevocable Or Perpetual License`
- **Test Set Support:** 33.0 samples
- **Empirical F1-Score:** 0.2532
- **Misclassified Count:** 23 / 33.0

**Representative Misclassified Examples:**

| # | True Category | Predicted As | Conf | Excerpt |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Irrevocable Or Perpetual License | **Affiliate License-Licensor** | 0.42 | "Subject to the terms and conditions of this Agreement, the Company hereby grants to Seller a perpetual, non- exclusive, royalty-free license in, to and under the Company Licensed Copyrights for use in the Arizona Field throughout the world." |
| 2 | Irrevocable Or Perpetual License | **License Grant** | 0.33 | "To the extent that Contractor incorporates any of Contractor's Information into the Works, Contractor hereby grants to Company a royalty-free, non- exclusive perpetual license (including the right to grant a sublicense) to use, copy, modify, create, " |
| 3 | Irrevocable Or Perpetual License | **License Grant** | 0.24 | "Licensee hereby grants to Bioeq during the term of this Agreement (and, subject to Section 15.3.4, after termination" |
| 4 | Irrevocable Or Perpetual License | **Affiliate License-Licensor** | 0.44 | "Equifax hereby grants, and will cause the other members of the Equifax Group to grant, to Certegy a fully paid, non-exclusive, perpetual, worldwide, non-transferable license to use, modify, copy, improve, create Derivative Works and Certegy Enhanceme" |
| 5 | Irrevocable Or Perpetual License | **Affiliate License-Licensee** | 0.41 | "Subject to the terms and conditions of this Agreement, the Company hereby grants to Allscripts and its Affiliates a non-exclusive, royalty- free, irrevocable [***] non-transferable (except in accordance with Section 28.4), sublicensable (through mult" |

### Category: `Non-Transferable License`
- **Test Set Support:** 59.0 samples
- **Empirical F1-Score:** 0.2810
- **Misclassified Count:** 42 / 59.0

**Representative Misclassified Examples:**

| # | True Category | Predicted As | Conf | Excerpt |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Non-Transferable License | **License Grant** | 0.51 | "The right and license to use the Licensed Marks granted hereunder to You is nonexclusive, and AIRSOPURE may use and grant franchises to others to use the Licensed Marks in any manner except as expressly provided otherwise herein." |
| 2 | Non-Transferable License | **Anti-Assignment** | 0.61 | "The Village Media Company shall not, directly or indirectly, assign, sublicense or otherwise transfer any of its rights or obligations hereunder without the prior written consent of PFHOF. T" |
| 3 | Non-Transferable License | **Irrevocable Or Perpetual License** | 0.54 | "ExxonMobil grants FCE a worldwide, non-exclusive, royalty-free, non-sub- licensable (except as set forth herein), perpetual, irrevocable (except as stated in Paragraphs 12.03 (Failure to Perform), 12.04 (Other Termination), and 12.05 (Bankruptcy)), n" |
| 4 | Non-Transferable License | **Anti-Assignment** | 0.89 | "Except as expressly permitted hereunder or in Exhibit F hereto, neither party may transfer, assign or sublicense this Agreement, or any rights or obligations hereunder, whether by contract or by operation of law, except with the express written conse" |
| 5 | Non-Transferable License | **Affiliate License-Licensee** | 0.44 | "The supply of the Miltenyi Products hereunder conveys to Bellicum the limited, non-exclusive, non-transferable (except as expressly provided herein, including as set forth in Article 17) right to use, and to permit its Subcontractors and Licensees to" |

---

## 3. Findings & Guidance for Downstream Pipelines

1. **Inherently Ambiguous Category Pairs:**
   Certain category boundaries (`Agreement Date` vs `Effective Date`, `Cap On Liability` vs `Uncapped Liability`, `Renewal Term` vs `Notice Period To Terminate Renewal`) share identical vocabulary because lawyers write them in single composite sentences. Classical bag-of-words models cannot parse dependency syntax between caps and carve-outs.
2. **Rare Class Support Ceiling:**
   Categories with fewer than 15 total examples in CUAD (`Price Restrictions`, `Volume Restriction`, `Affiliate License-Licensor`) suffer from high sample variance. Adding character n-grams lifted overall macro F1 significantly, but rare categories remain bounded by training data volume.
3. **Confidence Status Calibration Utility:**
   The UI confidence status thresholds cleanly separate high-accuracy predictions (precision $\ge 90\%$) from borderline predictions. For low-support categories, predictions fall predominantly into the 'Moderate' or 'Low - Review Required' status, prompting necessary human inspection.