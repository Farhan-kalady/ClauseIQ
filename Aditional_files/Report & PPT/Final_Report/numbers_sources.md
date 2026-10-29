# ClauseIQ Quantitative Audit: Reported Numbers and Ground Truth Sources

This document maps every numerical macro defined in `report/generated/numbers.tex` directly to its authoritative source file in the repository.

| Macro Name | Value | Repository Source File | Description / Notes |
| :--- | :--- | :--- | :--- |
| `\TotalClauses` | `12,204` | `data/clauseiq_dataset_clean.csv` | Total verified clause rows |
| `\TotalContracts` | `510` | `data/clauseiq_dataset_clean.csv` | Unique parent commercial contracts |
| `\NumClasses` | `41` | `data/clauseiq_dataset_clean.csv` | Legal clause categories |
| `\NullValueCount` | `0` | `data/clauseiq_dataset_clean.csv` | Missing values across all fields |
| `\DuplicateClauseCount` | `1655` | `data/clauseiq_dataset_clean.csv` | Clauses with identical text |
| `\MinWordCount` | `3` | `data/clauseiq_dataset_clean.csv` | Shortest clause in tokens |
| `\MaxWordCount` | `479` | `data/clauseiq_dataset_clean.csv` | Longest clause in tokens |
| `\MeanWordCount` | `45.89` | `data/clauseiq_dataset_clean.csv` | Average tokens per clause |
| `\MedianWordCount` | `36.0` | `data/clauseiq_dataset_clean.csv` | Median tokens per clause |
| `\StdWordCount` | `43.66` | `data/clauseiq_dataset_clean.csv` | Standard deviation of tokens |
| `\MinCharCount` | `9` | `data/clauseiq_dataset_clean.csv` | Shortest clause in chars |
| `\MaxCharCount` | `3,169` | `data/clauseiq_dataset_clean.csv` | Longest clause in chars |
| `\MeanCharCount` | `289.16` | `data/clauseiq_dataset_clean.csv` | Average characters per clause |
| `\MedianCharCount` | `224.0` | `data/clauseiq_dataset_clean.csv` | Median characters per clause |
| `\StdCharCount` | `277.38` | `data/clauseiq_dataset_clean.csv` | Standard deviation of characters |
| `\MinClausesPerContract` | `1` | `data/clauseiq_dataset_clean.csv` | Min clauses extracted per contract |
| `\MaxClausesPerContract` | `93` | `data/clauseiq_dataset_clean.csv` | Max clauses extracted per contract |
| `\MeanClausesPerContract` | `23.93` | `data/clauseiq_dataset_clean.csv` | Mean clauses per contract |
| `\MedianClausesPerContract` | `19.0` | `data/clauseiq_dataset_clean.csv` | Median clauses per contract |
| `\StdClausesPerContract` | `17.88` | `data/clauseiq_dataset_clean.csv` | Standard deviation clauses per contract |
| `\MostFrequentCategory` | `Parties` | `data/clauseiq_dataset_clean.csv` | Highest support class |
| `\MostFrequentCategoryCount` | `1,251` | `data/clauseiq_dataset_clean.csv` | Count of highest class |
| `\LeastFrequentCategory` | `Price Restrictions` | `data/clauseiq_dataset_clean.csv` | Lowest support class |
| `\LeastFrequentCategoryCount` | `27` | `data/clauseiq_dataset_clean.csv` | Count of lowest class |
| `\ImbalanceRatio` | `46.33:1` | `data/clauseiq_dataset_clean.csv` | Ratio of largest to smallest class |
| `\SplitATrainClauses` | `9,763` | `artifacts/manifest.json` | Split A training count |
| `\SplitATestClauses` | `2,441` | `artifacts/manifest.json` | Split A testing count |
| `\SplitBTrainClauses` | `9,718` | `docs/BASELINE.md` | Split B training count |
| `\SplitBTestClauses` | `2,486` | `docs/BASELINE.md` | Split B testing count |
| `\SplitBTrainContracts` | `408` | `docs/BASELINE.md` | Split B train contracts |
| `\SplitBTestContracts` | `102` | `docs/BASELINE.md` | Split B test contracts |
| `\FinalSplitAAcc` | `72.31\%` | `results/final_model_comparison.json` | Final Model Split A Accuracy |
| `\FinalSplitAMacroFScore` | `65.91\%` | `results/final_model_comparison.json` | Final Model Split A Macro F1 |
| `\FinalSplitAWeightedFScore` | `72.65\%` | `results/final_model_comparison.json` | Final Model Split A Weighted F1 |
| `\FinalSplitAMacroP` | `66.07\%` | `results/final_model_comparison.json` | Final Model Split A Macro Precision |
| `\FinalSplitAMacroR` | `66.96\%` | `results/final_model_comparison.json` | Final Model Split A Macro Recall |
| `\FinalSplitAECE` | `0.1545` | `results/final_model_comparison.json` | Final Model Split A ECE |
| `\FinalSplitAHighConfPrec` | `81.95\%` | `results/final_model_comparison.json` | Split A High Conf Precision |
| `\FinalSplitAHighConfShare` | `58.09\%` | `results/final_model_comparison.json` | Split A High Conf Share |
| `\FinalSplitBAcc` | `73.93\%` | `results/final_model_comparison.json` | Final Model Split B Accuracy |
| `\FinalSplitBMacroFScore` | `69.47\%` | `results/final_model_comparison.json` | Final Model Split B Macro F1 |
| `\FinalSplitBWeightedFScore` | `73.71\%` | `results/final_model_comparison.json` | Final Model Split B Weighted F1 |
| `\FinalSplitBMacroP` | `69.76\%` | `results/final_model_comparison.json` | Final Model Split B Macro Precision |
| `\FinalSplitBMacroR` | `71.23\%` | `results/final_model_comparison.json` | Final Model Split B Macro Recall |
| `\FinalSplitBECE` | `0.2005` | `results/final_model_comparison.json` | Final Model Split B ECE |
| `\FinalSplitBHighConfPrec` | `86.55\%` | `results/final_model_comparison.json` | Split B High Conf Precision |
| `\FinalSplitBHighConfShare` | `53.22\%` | `results/final_model_comparison.json` | Split B High Conf Share |
| `\SamplePdfClauses` | `29` | `data/raw_pdfs/sample_contract.pdf` | Sample contract extracted clause count |
| `\SyntheticPdfClauses` | `69` | `test_data/ClauseIQ_Synthetic_Company_Service_Agreement_Test.pdf` | Synthetic contract clause count |
| `\BenchClassifyAvg` | `6.58~ms` | `benchmark` | Average single clause inference latency |
| `\BenchClassifyPNinetyFive` | `8.93~ms` | `benchmark` | 95th percentile inference latency |
| `\BenchSearchAvg` | `100.68~ms` | `benchmark` | Average search retrieval latency |
| `\BenchSearchPNinetyFive` | `109.84~ms` | `benchmark` | 95th percentile search retrieval latency |
| `\BenchModelLoad` | `158.61~ms` | `benchmark` | Cold model load latency |
| `\BenchMemoryRSS` | `464.62~MB` | `benchmark` | Process resident memory footprint |
| `\PytestTotal` | `45` | `pytest` | Total automated pytest test cases |
| `\PytestPassRate` | `100\%` | `pytest` | Pytest pass rate |
| `\HostOS` | `Windows 11 (64-bit)` | `hardware` | Host OS |
| `\HostCPUCores` | `16 physical / 22 logical` | `hardware` | Host CPU cores |
| `\HostRAM` | `31.43~GB` | `hardware` | Host RAM detected |
